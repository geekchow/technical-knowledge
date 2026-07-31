一、一次推理的完整过程

假设你发送了一段 2000 token 的 prompt，模型回复 500 token。服务端实际发生的事情分两个截然不同的阶段：

① Tokenize： 文本被切成 token 序列，转成 ID 数组。开销可忽略。

② Prefill（预填充）阶段： 模型对这 2000 个输入 token 做一次并行的前向计算。因为输入是已知的，2000 个 token 可以同时算，GPU 矩阵乘法吃得很满——这个阶段是**算力受限（compute-bound）**的。它产出两样东西：全部 2000 个 token 在每一层的 K/V 向量（写入 KV Cache），以及第一个输出 token。你感受到的"首字延迟"（TTFT）基本就是 prefill 的耗时。

③ Decode（解码）阶段： 从第二个输出 token 开始进入自回归循环——每一步只处理一个 token：读取全部权重 + 已积累的 KV Cache，做一次前向，对最后一层输出的概率分布采样出下一个 token，把它的 K/V 追加进 Cache，再进入下一步。循环 500 次。这个阶段每步计算量极小但要搬运全部权重，是**内存带宽受限（memory-bound）**的，也就是上一轮说的"GPU 在等数据"。你看到的逐字打字机效果就是 decode 在一个个吐。

④ 终止与释放： 采样到停止符或达到 max_tokens 后结束，这个请求的 KV Cache 被释放（或按缓存策略保留一段时间）。

实际生产中还有一层调度：continuous batching——不同用户的请求处于不同阶段（有的在 prefill、有的在 decode 第 300 步），推理引擎（vLLM、TensorRT-LLM 等）把它们动态拼在同一批里跑，谁生成完谁退出、新请求随时插入，以此把 GPU 填满。

关键结论：prefill 和 decode 是两种性质完全不同的负载。 Prefill 吞吐高、按 token 算便宜；decode 慢、每个 token 都要"读一遍全模型"，单位成本高得多。记住这一点，计费规则就全通了。