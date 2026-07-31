# KV Cache Explained: The Single Biggest Speedup in LLM Inference

> The previous article, *The Full Journey of an LLM Inference Request*, kept mentioning one thing: the KV cache. Prefill produces it, every decode step reads it, it devours most of your GPU memory, and PagedAttention, GQA, and prefix caching all revolve around it.
>
> This article takes it apart completely: what exactly gets cached? Why cache only K and V, but not Q? How does it deliver an order-of-magnitude speedup — and why is it also the number-one memory hog?

---

## 1. Where the Problem Starts: Redundant Computation in Autoregressive Generation

Transformer LLMs generate text by **predicting one token at a time**:

1. Feed in a sentence → get token 1 of the output;
2. Feed in the original text plus that new token → get token 2;
3. Repeat until done.

Every round runs self-attention: generate Query, Key, and Value vectors for all history tokens, score Q against every K with dot products, then use the scores to take a weighted sum of the Vs.

Here's the problem: **every new token requires recomputing the K and V of the entire history from scratch.** Generating token 100 means recomputing K/V for the previous 99; token 500 means redoing 499 — and those values are *identical* to what was computed the round before. Pure wasted work, getting slower with every step; total attention computation grows quadratically with sequence length.

The KV cache's idea is almost embarrassingly simple: **once computed, store it — never compute it again.** Each new token computes only its *own* K and V and appends them to a cache in GPU memory; the history's K/V is reused directly. Compute once, benefit forever.

That single change speeds up inference by several times to over 10×, making it mandatory for every production LLM service — chatbots, code completion, local deployments — anything autoregressive, without exception.

---

## 2. Foundations First: What Q, K, and V Actually Are

To understand "why cache only K and V," you first need each vector's job description.

### From text to vectors

Every token is first converted to a fixed-dimension **embedding** — an array of numbers representing its meaning. The model contains three independent trainable weight matrices, $W_Q$, $W_K$, $W_V$, which project the embedding matrix $X$ (all history tokens packed together) into three sets of vectors:

$$
Q = X W_Q,\quad K = X W_K,\quad V = X W_V
$$

One matrix multiplication, and every token has its own (Q, K, V) triple.

### The division of labor: a database lookup

The most intuitive analogy is a database query:

- **Q (Query)** — your search keywords. It represents **the token currently being computed**: "here's who I am, and here's the kind of context I'm looking for";
- **K (Key)** — the **index label** on every record: a feature summary of each history token, existing purely to be matched against Q;
- **V (Value)** — each record's **full body text**: the actual content each history token carries.

The lookup: score the keywords (Q) against every index (K) with dot products → normalize the scores into weights via softmax → take the weighted sum of all body texts (V) → that's the current token's output feature.

A concrete example: the context is "The cat is sleeping by the window," and the token being processed is "it." The Q of "it" scores highest against the K of "cat," so after softmax, cat's V dominates the weighted sum — that's how the model knows "it" refers to the cat. **K does the scoring; V supplies the content.** Distinct jobs, both essential.

### One full pass, end to end

Context: `[I, ate, strawberries, this, morning]`, predicting the next token:

1. The 5 tokens become embedding matrix X;
2. X times $W_Q$, $W_K$, $W_V$ → 5 rows each of Q, K, V;
3. Take the Q of the **last** token, score it against all 5 Ks;
4. Blend the 5 Vs by those weights → output feature → sample the next token (say, "They").

Look closely at step 3: **the only Q ever used is the last token's.** That's the key setup for everything that follows.

---

## 3. Why Cache K and V, but Not Q?

In autoregressive generation we only ever need to predict **the next** token. The querying party is always "the single newest token" — its Q gets matched against the K and V of the entire history.

And the history tokens' Qs? Each was used exactly once, back when that token was the newest one, and is **never referenced by any computation again**. Caching them would be pointless.

K and V are the opposite: every history token's K/V gets matched and weighted by the new token's Q **at every subsequent step** — they're the assets that get read over and over.

**In one sentence: Q is a one-shot query; K/V is the database that gets queried repeatedly.** That's why it's called the KV cache, not the QKV cache.

---

## 4. The KV Cache in Action

Plug the cache into the generation loop and compare:

**Without a KV cache** (continuing `[I, ate, strawberries, this, morning]` → "They were sweet"):

- Generating "They": re-run all 5 history tokens through $W_K$, $W_V$, then compute attention;
- Generating "were": re-run all 6 tokens (including the fresh "They") through K/V **all over again**;
- Every step starts from zero; the longer the context, the slower each step.

**With a KV cache:**

- Prefill: all 5 input tokens computed in one parallel pass → 5 K/V pairs stored in GPU memory;
- Generating "They": compute only its own 1 K/V pair, append to the cache; attention reads the 6 cached pairs;
- Generating "were": compute only its 1 pair, reuse the previous 7;
- Zero recomputation of history, ever.

Per-step work drops from "proportional to context length" to "one token's constant amount," and total attention computation falls from quadratic back to linear.

### A note on multi-head attention

Real models use multi-head attention: $W_Q/W_K/W_V$ are split into multiple independent heads, each producing its own QKV set and doing its own matching, with results concatenated at the end — parallel lookups capturing finer-grained semantic relationships. The KV cache logic is unchanged; the model just stores K/V **per head, per layer**. That "layers × heads" multiplier is exactly where the memory bill in the next section comes from.

---

## 5. No Free Lunch: The Memory Bill

The KV cache is fundamentally a **memory-for-compute trade**. The savings are real, and so is the cost. Let's do the math:

Bytes cached per token =

$$
2 \times \text{layers} \times \text{KV heads} \times \text{head dim} \times \text{bytes per element}
$$

(The leading 2 is one copy each for K and V.)

Take Llama-3-70B: 80 layers × 8 KV heads × 128 dims × 2 bytes (FP16), times two for K and V:

$$
2 \times 80 \times 8 \times 128 \times 2 \approx 327{,}680 \text{ bytes} \approx 320\text{ KB per token}
$$

- An 8K-token conversation → **~2.6 GB** of GPU memory, for that one request's cache alone;
- A 128K long context → **~40 GB** — larger than many entire GPUs;
- A production server holding dozens of concurrent requests can easily spend more memory on KV cache than on the model weights themselves.

Hence the KV cache's two big downsides:

1. **Memory grows linearly with length** — long documents and marathon conversations readily blow past GPU memory (OOM), and concurrency is capped by how many caches fit;
2. **Longer means slower** — every decode step must read the entire cache out of memory for attention. The longer the context, the more data moved per step. This is part of the memory-bound bottleneck from the previous article, and the direct reason long chats get progressively more sluggish.

---

## 6. The Optimization Ecosystem Around the KV Cache

Precisely because the KV cache is both the hero of speed and the villain of memory, a whole family of optimizations has grown around it. Four strategies:

### 1. Manage it better: PagedAttention

The traditional approach reserves one contiguous memory region per request (sized for the maximum length), most of which goes unused — staggering fragmentation. **PagedAttention** borrows OS memory paging: chop the KV cache into fixed-size blocks, allocate on demand, store them scattered, and track logical order with a "page table." Fragmentation drops to near zero and the same GPU holds several times more concurrent requests. This made vLLM famous, and SGLang, TensorRT-LLM, and other mainstream engines have all adopted it.

### 2. Store it smaller: quantization and structural compression

- **KV cache quantization (INT8/INT4)** — store K/V tensors at low precision instead of FP16, halving or quartering memory with mild accuracy loss;
- **MQA / GQA / MLA** — cut the number of KV heads architecturally. Multi-Query Attention shares one K/V set across all heads; Grouped-Query Attention shares within groups (the Llama family's choice — 70B squeezes 64 query heads down to 8 KV heads, shrinking the cache 8×); DeepSeek's MLA goes further, compressing K/V into low-rank latent vectors. Fewer heads means a smaller multiplier in the formula above.

### 3. Discard it wisely: sliding windows

For very long conversations, keep only the **most recent N tokens'** K/V and drop distant history, pinning memory to a fixed ceiling (used by Mistral, among others). The trade-off: the model can't "remember" anything outside the window — fine for tasks that only need recent context.

### 4. Reuse it further: prefix caching and speculative decoding

- **Prefix caching** — don't release the cache when a request ends; the next request sharing the same prefix (system prompt, multi-turn history) reuses it and skips most of prefill. This is exactly why API providers charge ~10× less for cache-hit input tokens;
- **Speculative decoding** — a small draft model guesses several tokens and the large model verifies them in one parallel pass; the verification leans on the KV cache too, further cutting per-token latency.

---

## 7. Summary

The whole article in five sentences:

1. Autoregressive generation recomputes history K/V over and over; the KV cache's "compute once, store forever" turns quadratic attention cost back into linear;
2. Only K/V is cached — never Q — because Q is a one-shot query while K/V is the database read at every step;
3. The price is memory that grows linearly with context (hundreds of KB per token for a 70B-class model), which is why long chats get slower and heavier;
4. PagedAttention fights fragmentation, quantization and GQA/MLA shrink the footprint, sliding windows cap it, prefix caching reuses it — half of a modern inference engine exists to serve this one cache;
5. Understand the KV cache and you understand why LLM inference is fast, why it's expensive, and where the optimization battleground lies.

It may be the highest-leverage idea in the entire inference stack: one plain intuition — "store it, don't recompute it" — quietly holds up the usability of every LLM service running today.
