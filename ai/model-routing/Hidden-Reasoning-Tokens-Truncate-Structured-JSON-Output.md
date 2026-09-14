# Hidden Reasoning Tokens Are Silently Truncating Your Structured JSON Output

> Debugging a production backend that calls OpenRouter for structured JSON extraction, a call would occasionally come back with `finish_reason: "length"` and a truncated, unparseable response — even though the system prompt already said "be concise, under 500 tokens" and the model was well within that limit on every other call. The obvious theory ("the model is being verbose") was wrong. This article is the actual root cause, how to find it in your own logs, and the counterintuitive fix that came out of testing it against two different providers.

---

## 1. The Symptom

The setup: an OpenRouter request with a `models: [primary, fallback]` array (OpenRouter's [Model Fallbacks](./OpenRouter-Auto-Router-vs-Model-Fallbacks.md) mechanism), `temperature: 0`, a `max_tokens` ceiling sized with real headroom over the expected output, and a system prompt that explicitly caps the answer's length. A small fraction of calls still came back with `finish_reason: "length"` and content that cut off mid-string — invalid JSON, unrecoverable.

The instinctive fix is "raise `max_tokens`" or "tighten the prompt's length instruction further." Both are reasonable-sounding and both, in this case, missed the actual mechanism.

## 2. What Actually Consumes the Token Budget

The two models behind this backend — OpenAI's open-weight `gpt-oss-120b` and DeepSeek's `deepseek-v4-flash` — are both **reasoning models**. Before writing the answer you asked for, they generate an internal chain-of-thought, and on most providers **that chain-of-thought is billed as completion tokens, from the same `max_tokens` budget as the visible answer.**

This is invisible by default. A normal streamed chat completion just shows the final JSON; nothing in the delta stream flags that a large chunk of the token budget was already spent before the first visible character arrived. The evidence only shows up if you go looking for it — a **non-streaming** call, inspecting the raw response body instead of just the parsed `content` string:

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek/deepseek-v4-flash",
    "temperature": 0,
    "max_tokens": 1200,
    "messages": [
      {"role": "system", "content": "Return ONLY valid JSON: {\"category\": \"...\", \"sampleSentences\": [...]}. Be concise, under 500 tokens."},
      {"role": "user", "content": "Explain the English word: \"ephemeral\""}
    ]
  }'
```

The response carries two things a streaming integration typically never looks at:

```json
{
  "choices": [{
    "finish_reason": "stop",
    "message": {
      "content": "{ \"category\": \"adjective\", \"sampleSentences\": [...] }",
      "reasoning": "We need to explain \"ephemeral\" and provide 3 example sentences with Chinese translations. The word means lasting for a very short time. Category: adjective. Provide sample sentences with source and Chinese translation."
    }
  }],
  "usage": {
    "completion_tokens": 202,
    "completion_tokens_details": {
      "reasoning_tokens": 55
    }
  }
}
```

`reasoning_tokens` sits *inside* `completion_tokens`, not alongside it. Every one of those tokens comes out of the same `max_tokens` ceiling the visible JSON has to fit into.

## 3. It's Not Small, and It's Not Stable

Repeating the identical request at `temperature: 0` — same prompt, same word, same model — produced wildly different reasoning-token counts across runs:

| Model | Reasoning tokens observed (repeated identical calls) |
|---|---|
| `openai/gpt-oss-120b` | 7 – 774 |
| `deepseek/deepseek-v4-flash` | 0 – 390 |

`temperature: 0` makes the *visible* output close to deterministic; it does nothing to bound the hidden reasoning phase, which can vary by two orders of magnitude call to call. A `max_tokens` budget sized against the visible answer's expected length — even with real headroom — has no defense against a reasoning phase that occasionally decides to think for 700+ tokens before it starts answering. That's the truncation.

And the system prompt's own "be concise, under 500 tokens" instruction is powerless against this, for a simple reason: **the model doesn't count its reasoning as part of "the response."** The instruction constrains what it writes as the answer; it has no visibility into, or authority over, a phase the model itself treats as scratch space.

## 4. The Fix Is Not "Disable Reasoning" — It's Capping It, and Providers Disagree on Whether You Can

The clean-sounding fix is to just turn reasoning off. OpenRouter exposes a unified `reasoning` parameter across providers for exactly this:

```json
"reasoning": { "enabled": false }
```

This worked immediately on `deepseek-v4-flash` — `reasoning_tokens` dropped to 0, latency dropped by more than half, and (in this testing) the model also correctly followed an enum constraint it had gotten wrong on a call where reasoning was left on.

It did **not** work on `gpt-oss-120b`:

```json
{"error": {"message": "Reasoning is mandatory for this endpoint and cannot be disabled.", "code": 400}}
```

Some reasoning models let you switch reasoning off entirely; others treat it as a fixed part of how they operate and reject the request outright if you try. If your integration calls more than one model — a primary/fallback pair, a router, an A/B test — a request shape that works on one can hard-fail on the other. **You cannot standardize on full disable across an arbitrary set of reasoning models.**

The portable middle ground is a **bounded cap** rather than a toggle:

```json
"reasoning": { "max_tokens": 150 }
```

`gpt-oss-120b` accepts this even though it rejects full disable — reasoning still runs, but only up to the cap. `deepseek-v4-flash` accepts it too. This is the one shape that worked, without error, across both models tested.

## 5. The Counterintuitive Part: A Bigger Cap Made Things Worse

The instinct when a cap doesn't fully solve a truncation problem is to raise it. Testing that instinct directly, repeated 3× per setting on the model that was still occasionally truncating:

| `reasoning.max_tokens` | Result over 3 identical calls |
|---:|---|
| *(uncapped — default)* | 1 truncated |
| `300` | 1 truncated |
| `150` | 0 truncated |

A **smaller** cap was more reliable than a **larger** one. That's backwards from how token budgets normally behave, and the explanation is about behavior, not arithmetic: given a generous reasoning allowance, the model used more of it — and still occasionally ran the visible answer past what remained of `max_tokens`. Given a tight allowance, it was forced to wrap up reasoning quickly, which left a larger, more consistent remainder for the actual answer. The cap doesn't just limit reasoning length — it changes how much of it the model attempts to produce in the first place.

This was then validated at scale: `reasoning: {"max_tokens": 150}` against five different structured-extraction prompts, on both models, two runs each — **20/20 succeeded**, zero truncations, where the uncapped baseline and the `effort: "low"` shorthand had both intermittently failed.

`"effort": "low"` (the other OpenRouter-standard way to bound reasoning) is worth naming as a trap here: it reads as equivalent to a numeric cap, but in this testing it was **not** — `deepseek-v4-flash` still produced a truncated response under `effort: "low"` in live testing, while an explicit `max_tokens: 150` did not. Where it's available, prefer the numeric form; it's the one that was actually verified to hold up.

## 6. The Practical Checklist

If a backend calling reasoning-capable models through an OpenRouter-style API sees intermittent, hard-to-reproduce truncated JSON — especially if it only happens on *some* calls to the *same* prompt, at `temperature: 0`, and raising `max_tokens` or tightening the prompt's own length instruction didn't fully fix it:

1. **Check whether the model is a reasoning model** — most current-generation open-weight and frontier models are, by default, even ones without "reasoning" or "thinking" in the model name (`gpt-oss` and DeepSeek's `v3`/`v4` line both qualify).
2. **Make one non-streaming call and read `usage.completion_tokens_details.reasoning_tokens`** — this is the fastest way to confirm the theory. If it's non-zero and varies across repeated identical calls, this is the cause.
3. **Try a bounded cap, not a toggle** — `reasoning: {"max_tokens": N}`. Confirm the model you're calling accepts it; some reasoning models (verified here: `gpt-oss-120b`) reject `enabled: false` outright but accept a numeric bound.
4. **Test the cap value, don't guess it** — a bigger number is not automatically safer, as §5 shows. Start small (the working value found here was ~150 tokens for short structured-extraction tasks) and validate with repeated calls before trusting it in production.
5. **If more than one model can serve the request** (fallback array, router, A/B test), verify the fix against *every* model that can actually receive it — a shape that works on one provider's reasoning implementation can hard-error on another's.

## 7. Why This Matters Beyond Fixing a Bug

This wasn't only a bug fix — it changed the cost and latency profile of a production system that was already live. The model that had been serving 100% of traffic was, by default, spending 600+ hidden reasoning tokens on a large share of its calls, for a task (structured JSON extraction with a fixed, narrow schema) that gains essentially nothing from extended chain-of-thought. That hidden spend was very likely the dominant contributor to multi-second latencies that had, until this investigation, been attributed to "the model is just slow."

The general lesson: **for structured-extraction and classification-style tasks — fixed schema, low ambiguity, no multi-step logic required — a reasoning model's default reasoning budget is close to pure overhead.** It costs latency and money, and paradoxically makes output *less* reliable by competing with the answer for the same token budget. Capping it isn't a quality compromise for this class of task; on the evidence here, it improves both speed and reliability at once.

---

**See also:** [OpenRouter Auto Router vs Model Fallbacks](./OpenRouter-Auto-Router-vs-Model-Fallbacks.md) — the routing mechanism this fix was layered on top of.
