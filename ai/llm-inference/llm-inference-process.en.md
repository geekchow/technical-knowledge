# The Full Journey of an LLM Inference Request: From Enter Key to Last Token

> You send a 2,000-token prompt to a large language model and it replies with 500 tokens. What actually happens on the server? Why does the first word take a moment while the rest stream out like a typewriter? Why do output tokens cost several times more than input tokens? And why is a "cache hit" on your input another order of magnitude cheaper?
>
> The answers all hide inside the two phases of inference: **prefill** and **decode**. Once you understand how fundamentally different these two phases are, API pricing, latency behavior, and the entire zoo of inference optimizations all snap into a single coherent picture.

---

## 1. Overview: The Four Steps of One Request

Say you send a 2,000-token prompt and the model generates a 500-token reply. On the server, four things happen:

1. **Tokenize** — text is split into a token sequence and mapped to an array of integer IDs;
2. **Prefill** — all input tokens are processed in parallel, producing the KV cache and the first output token;
3. **Decode** — an autoregressive loop emits the remaining 499 tokens, one at a time;
4. **Termination and release** — a stop token or the `max_tokens` limit ends the loop, and resources are freed.

Prefill and decode are two **completely different kinds of workload** — one is hungry for compute, the other for memory bandwidth. Let's walk through each step.

---

## 2. Tokenize: Text Becomes Numbers

Models don't read text; they read numbers. The tokenizer splits your text against a vocabulary and maps the pieces to integer IDs:

```
"The weather is nice" → [The, weather, is, nice] → [464, 6193, 318, 3621]
```

In English, roughly 4 characters make one token; in Chinese, roughly 1–2 characters per token, depending on the vocabulary. This step is pure string processing on the CPU, takes milliseconds, and its **cost is negligible**. But it defines the unit of account for everything downstream — every cent on your bill and every slot in the context window is counted in tokens.

---

## 3. Prefill: Swallowing the Whole Prompt in Parallel (Compute-Bound)

The model runs **one parallel forward pass** over all 2,000 input tokens.

The key insight: the input is already known. You don't need token 1,499's output to know what token 1,500 is — it's sitting right there in your prompt. So all 2,000 tokens flow through the network **simultaneously**. Every attention and MLP layer becomes a large matrix multiplication, and the GPU's compute units are fully saturated. This phase is **compute-bound**: the bottleneck is how many floating-point operations the GPU can do per second, not how fast data moves.

Prefill produces two things:

1. **The KV cache** — the Key/Value vectors of all 2,000 input tokens at every attention layer, written into GPU memory. This is the "memory" the decode phase will rely on: without it, every new token would require recomputing the entire context from scratch. (The KV cache deserves an article of its own; for now, just know that it trades repeated computation for memory footprint.)
2. **The first output token** — sampled from the probability distribution at the last input position.

The **time to first token (TTFT)** you experience is essentially the prefill time. The longer the prompt, the bigger the matrices, the slower the first word — which is why a request stuffed with tens of thousands of context tokens makes you wait several seconds before anything appears.

---

## 4. Decode: The One-Token-at-a-Time Autoregressive Loop (Bandwidth-Bound)

From the second output token onward, the model enters a completely different mode.

Each loop iteration handles exactly **one** token:

1. Read all model weights plus the accumulated KV cache;
2. Run one forward pass;
3. **Sample** the next token from the final layer's probability distribution;
4. Append this new token's K/V to the cache;
5. Repeat.

Five hundred iterations later, you've watched 500 tokens appear one by one — the typewriter effect.

### Why Is Decode Slow? The GPU Is Waiting for Data

Each step does **very little math** (matrix multiplications for a single token) but must move **the entire set of model weights** from GPU memory to the compute units. A quick back-of-the-envelope calculation makes it vivid:

- A 70B-parameter model in FP16 weighs about **140 GB**;
- An A100's memory bandwidth is about **2 TB/s**;
- Generating one token requires reading the weights at least once: 140 GB ÷ 2 TB/s ≈ **70 ms per token**;
- So a single request, with no other optimization, tops out around **14 tokens/s** — while the GPU's compute units sit at under 1% utilization.

This is what **memory-bound** means: the bottleneck isn't "can't compute fast enough" but "can't feed the data fast enough." The GPU spends most of its time waiting for weights to arrive from memory. This also explains why HBM bandwidth is the headline spec in the inference-chip race, and why weight quantization (INT8/INT4) directly speeds up decode — halve the bytes, halve the transfer time.

### Sampling: How a Probability Distribution Becomes an Actual Word

The forward pass doesn't output a token; it outputs a probability distribution over the whole vocabulary. Sampling parameters control how a token gets picked:

- **temperature** — lower makes the distribution sharper (more deterministic), higher makes it more random;
- **top-p / top-k** — sample only from the highest-probability candidates, cutting off the long tail;
- **greedy** (temperature = 0) — always take the single most likely token.

This is why the same prompt gives slightly different answers each time: every decode step rolls the dice.

---

## 5. Termination and Release

The decode loop ends in one of two ways:

1. The model samples a **stop token** (EOS, or a stop sequence you specified) — it "finished its thought";
2. It hits the **`max_tokens`** limit — a hard cutoff (this is why answers sometimes stop mid-sentence).

Afterward, the request's KV cache is released and the memory returns to the scheduler for other requests. Or — depending on caching policy — it's kept around for a while. If the next turn of the same conversation arrives a few seconds later, the prefix's KV cache is still warm and most of the prefill can be skipped. This is **prefix caching**, and it's the technical reason API providers charge roughly **10× less for cache-hit input tokens**: the cached portion isn't computed at all, just read back from memory.

---

## 6. What Production Actually Looks Like: Continuous Batching

Everything above was the single-request view. On a real inference server, one GPU carries dozens or hundreds of requests at once, each at a different stage: one just arrived and is in prefill, another is on decode step 300, a third is about to finish.

The old approach was **static batching**: gather a batch, run it to completion, then take the next batch. The problem is obvious — one request in the batch finishes after 50 tokens while another needs 2,000, so the early finishers sit idle and GPU utilization is dragged down by the slowest request.

Modern inference engines (vLLM, TensorRT-LLM, SGLang, etc.) use **continuous batching**: scheduling happens at the granularity of a *step* — at every step, the engine dynamically decides who's in the batch. Finished requests exit immediately and free their slot; new requests join at any time; prefill and decode work can be mixed in the same batch. This spreads decode's fixed cost — "move all the weights every step" — across dozens of requests: the weights have to be read once anyway, and computing a few dozen extra tokens on top of that is nearly free. **Batching is the number-one lever for decode throughput.**

The key companion techniques:

- **PagedAttention** — manage the KV cache like an operating system pages memory: allocate in small blocks instead of reserving large contiguous regions, eliminating fragmentation and letting the same GPU hold several times more concurrent requests (the innovation that made vLLM famous);
- **Chunked prefill** — split a very long prompt's prefill into chunks interleaved with other requests' decode steps, so one giant prefill doesn't monopolize the GPU for hundreds of milliseconds and stall every user currently mid-generation;
- **Prefill/decode disaggregation** — the more radical architecture: since the two workloads are fundamentally different, run them on separate machine pools tuned for each, shipping the KV cache between them over fast interconnects.

---

## 7. Making Decode Faster: Speculative Decoding and Attention Variants

Beyond batching, two orthogonal families of optimization attack decode's per-step cost:

**Speculative decoding.** A small draft model (or a lightweight prediction head built into the model) quickly *guesses* the next 4–8 tokens, and the large model **verifies the whole guess in a single parallel forward pass**. When the guesses are right, one step yields many tokens; when wrong, generation resumes from the first mistake — with zero loss of correctness (the output is mathematically identical to the large model generating alone). In essence, it converts decode's serial memory traffic into one prefill-like parallel verification: trading cheap compute for expensive bandwidth.

**Shared attention heads (MQA / GQA / MLA).** In standard multi-head attention, every head keeps its own K/V, making the KV cache enormous. Multi-Query Attention shares one K/V set across all heads; Grouped-Query Attention shares within groups (the Llama family's choice); DeepSeek's MLA compresses K/V into low-rank latent vectors. A smaller KV cache means less data moved per step and more concurrent requests per GPU.

---

## 8. The Key Conclusion: Pricing, Explained by Physics

Back to the original questions. Put the two phases side by side:

| | Prefill (input tokens) | Decode (output tokens) |
|---|---|---|
| Computation | All tokens in one parallel pass | One token at a time, serially |
| Bottleneck | Compute-bound | Memory-bandwidth-bound |
| GPU utilization | High | Low (rescued by batching) |
| Cost per token | Low | Several times higher |
| What you feel | Time to first token (TTFT) | Per-token generation speed (TPOT) |

**Prefill has high throughput and is cheap per token; decode is slow, and every token requires "reading the whole model once," making its unit cost far higher.**

Suddenly everything on the API price sheet has a physical explanation:

- **Output tokens cost 3–5× more than input tokens** — not a pricing strategy, but decode's genuinely higher cost;
- **Cache-hit input is another order of magnitude cheaper** — a prefix cache hit skips prefill entirely, near-zero computation;
- **Long prompts mean slow first tokens** — prefill work grows with input length (and the attention portion grows quadratically);
- **Long conversations get slower and pricier every turn** — each turn carries the full history, the KV cache balloons linearly, and every decode step reads an ever-larger cache.

The practical takeaways for developers are the mirror image of those four points: **put cacheable prefixes (system prompt, few-shot examples, documents) at the start of the prompt and keep them byte-for-byte stable** so prefix caching hits; **trim output wherever you can** (ask for JSON, not prose; set a sensible `max_tokens`); and **stream when latency matters**, so users start reading right after TTFT and perceived latency collapses.

One sentence to remember it all: **input tokens are wholesale, output tokens are retail — hold onto that, and the performance, cost, and every optimization trick of LLM inference all live on the same map.**
