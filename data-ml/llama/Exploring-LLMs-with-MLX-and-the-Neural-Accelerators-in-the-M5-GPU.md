---
title: "Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU"
source: "https://machinelearning.apple.com/research/exploring-llms-mlx-m5"
author:
published:
created: 2026-04-11
description: "Mac with Apple silicon is increasingly popular among AI developers and researchers interested in using their Mac to experiment with the…"
tags:
  - "clippings"
---

# Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU

Mac with Apple silicon is increasingly popular among AI developers and researchers interested in using their Mac to experiment with the latest models and techniques. With MLX, users can explore and run LLMs efficiently on Mac. It allows researchers to experiment with new inference or fine-tuning techniques, or investigate AI techniques in a private environment, on their own hardware. MLX works with all Apple silicon systems, and with the latest macOS beta release <sup><a href="#footnotes">1</a></sup>, it now takes advantage of the Neural Accelerators in the new M5 chip, introduced in the new 14-inch MacBook Pro. The Neural Accelerators provide dedicated matrix-multiplication operations, which are critical for many machine learning workloads, and enable even faster model inference experiences on Apple silicon, as showcased in this post.

### What is MLX

[MLX](https://mlx-framework.org/) is an open source array framework that is efficient, flexible, and highly tuned for Apple silicon. You can use MLX for a wide variety of applications ranging from numerical simulations and scientific computing to machine learning. MLX comes with built in support for neural network training and inference, including text and image generation. MLX makes it easy to generate text with or fine tune of large language models on Apple silicon devices.

MLX takes advantage of Apple silicon’s unified memory architecture. Operations in MLX can run on either the CPU or the GPU without needing to move memory around. The API closely follows [NumPy](https://numpy.org/) and is both familiar and flexible. MLX also has higher level neural net and optimizer packages along with function transformations for automatic differentiation and graph optimization.

Getting started with MLX in Python is as simple as:

```python
pip install mlx
```

To learn more, check-out the [documentation](https://ml-explore.github.io/mlx/). MLX also has numerous [examples](https://github.com/ml-explore/mlx-examples) to help as an entry point for building and using many common ML models.

[MLX Swift](https://github.com/ml-explore/mlx-swift) builds on the same core library as the MLX Python front-end. It also has several [examples](https://github.com/ml-explore/mlx-swift-examples) to help get you started with developing machine learning applications in Swift. If you prefer something lower level, MLX has easy to use C and C++ APIs that can run on any Apple silicon platform.

### Running LLMs on Apple Silicon

MLX LM is a package built on top of MLX for generating text and fine-tuning language models. It allows running most LLMs available on Hugging Face. You can install MLX LM with:

```python
pip install mlx-lm
```

And, you can initiate a chat with your favorite language model by simply calling `mlx_lm.chat` in the terminal.

MLX natively supports quantization, a compression approach which reduces the memory footprint of a language model by using a lower precision for storing the parameters of the model. Using `mlx_lm.convert`, a model downloaded from Hugging Face can be quantized in a few seconds. For example quantizing a 7B Mistral model to a 4-bit takes only few seconds by running a simple command.

```python
mlx_lm.convert \
  --hf-path mistralai/Mistral-7B-Instruct-v0.3 \
  -q \
  --upload-repo mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

### Inference Performance on M5 with MLX

The GPU Neural Accelerators introduced with the M5 chip provides dedicated matrix-multiplication operations, which are critical for many machine learning workloads. MLX leverages the Tensor Operations (TensorOps) and Metal Performance Primitives framework introduced with Metal 4 to support the Neural Accelerators’ features. To illustrate the performance of M5 with MLX, we benchmark a set of LLMs with different sizes and architectures, running on [MacBook Pro with M5 and 24GB of unified memory](https://www.apple.com/macbook-pro/specs/), that we compare against a similarly configured MacBook Pro M4.

We evaluate Qwen 1.7B and 8B, in native BF16 precision, and 4-bit quantized Qwen 8B and Qwen 14B models. In addition, we benchmark two Mixture of Experts (MoE): Qwen 30B (3B active parameters, 4-bit quantized) and GPT OSS 20B (in native MXFP4 precision). Evaluation is performed with `mlx_lm.generate`, and reported in terms of time to first token generation (in seconds), and generation speed (in terms of token/s). In all these benchmarks, the prompt size is 4096. Generation speed was evaluated when generating 128 additional tokens.

Model performance is reported in terms of time to first token (TTFT) for both M4 and M5 MacBook Pro, along with corresponding speedup.

Qwen3-1.7B-MLX-bf16: M4 is 3.79, M5 is 1.06.Qwen3-8B-MLX-bf16: M4 is 16.92, M5 is 4.67.Qwen3-8B-MLX-4bit: M4 is 18.6, M5 is 4.69.Qwen3-14B-MLX-4bit: M4 is 35.15, M5 is 8.66.gpt-oss-20b-MXFP4-Q4: M4 is 9.54, M5 is 2.87.Qwen3-30B-A3B-MLX-4bit: M4 is 9.37, M5 is 2.66.

Figure 1: TTFT in seconds (smaller is better) for different LLMs run with MLX on M4 and M5 MacBook Pro. Speedup values listed underneath each model name.

In LLM inference, generating the first token is compute-bound, and takes full advantage of the Neural Accelerators. The M5 pushes the time-to-first-token generation under 10 seconds for a dense 14B architecture, and under 3 seconds for a 30B MoE, delivering strong performance for these architectures on a MacBook Pro.

Generating subsequent tokens is bounded by memory bandwidth, rather than by compute ability. On the architectures we tested in this post, the M5 provides 19-27% performance boost compared to the M4, thanks to its greater memory bandwidth (120GB/s for the M4, 153GB/s for the M5, which is 28% higher). Regarding memory footprint, the MacBook Pro 24GB can easily hold a 8B in BF16 precision or a 30B MoE 4-bit quantized, keeping the inference workload under 18GB for both of these architectures.

|  |  | **TTFT Speedup** | **Generation Speedup** | **Memory (GB)** |  |
| --- | --- | --- | --- | --- | --- |
|  | Qwen3-1.7B-MLX-bf16 | 3.57 | 1.27 | 4.40 |  |
|  | Qwen3-8B-MLX-bf16 | 3.62 | 1.24 | 17.46 |  |
|  | Qwen3-8B-MLX-4bit | 3.97 | 1.24 | 5.61 |  |
|  | Qwen3-14B-MLX-4bit | 4.06 | 1.19 | 9.16 |  |
|  | gpt-oss-20b-MXFP4-Q4 | 3.33 | 1.24 | 12.08 |
|  | Qwen3-30B-A3B-MLX-4bit | 3.52 | 1.25 | 17.31 |  |

Table 1: Inference speedup achieved for different LLMs with MLX on M5 MacBook Pro (compared to M4) for TTFT and subsequent token generation, with corresponding memory demands. TTFT is compute-bound, while generation is memory-bandwidth-bound.

The GPU Neural Accelerators shine with MLX on ML workloads involving large matrix multiplications, yielding up to 4x speedup compared to a M4 baseline for time-to-first-token in language model inference. Similarly, generating a 1024x1024 image with FLUX-dev-4bit (12B parameters) with MLX is more than 3.8x faster on a M5 than it is on a M4. As we continue to add features and improve the performance of MLX, we are looking forward to the new architectures and models the ML community will investigate and run on Apple silicon.
