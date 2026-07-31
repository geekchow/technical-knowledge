# How WebFlux improve I/O bound web service througout via async threading

## 0 Concept Explanation

### 0.1 Sync thread mode of servlet

![sync-thread-model-of-servlet](./01-sync-thread-model-of-servlet.webp)

### 0.2 Limitation of sync servlet thread mode

![limitation-of-servlet-thread-model](./02-limitation-of-servlet-thread-model.webp)

### 0.3 Async thread mode of WebFlux

![async-thread-mode-of-webflux](./03-async-thread-mode-of-webflux.webp)

### 0.4 Event Loop with thread pool

![event-loop-thread-pool](./04-event-loop-thread-pool.webp)

### 0.5 Event loop with one thread per cpu core

![Event loop with one thread per cpu core](./05-even-loop-thread-per-cpu-core.webp)

### 0.6 Event loop: thread pool vs thread per cpu core

![Event loop mode vs Traditional mode](./06-event-loop-vs-traditional.webp)

### 0.7 End to end async 

> Caution: The whole end to end link should be async, otherwise it's degraded to sync mode.

![End to end async ](./07-end-to-end-reactive.webp)

## 1 Implementation 

### 1.1 The traditional blocking mode with servlet

![The traditional blocking mode with servlet](./11-code-blocking-mode.webp)

### 1.2 Future as placeholder

![Future as placeholder](./12-code-future-placeholder.webp)

### 1.3 Computable<Future> as placeholder

![Computable<Future> as placeholder](./13-code-computable-future-placeholder.webp)

### 1.4 Mono & Flux as placeholder

![ Mono & Flux as placeholder](./14-code-webflux-mono-flux.webp)


### 1.5 Get continous stream data implementation 

![Get continous stream data](./15-code-continuous-get-live-data.webp)

### 1.6 Get continous stream data concept 

![Get continous stream data concept ](./16-continous-get-data-stream-mechanism.webp)

### 1.7 Put continous stream data implementation 

![Put continous stream data](./17-code-continous-post-live-data.webp)

### 1.8 Put continous stream data concept 

![Put continous stream data concept ](./18-continuous-put-data-stream-mechanism.webp)

## 2 Conclusion

### 2.1 Advantages of webflux

![Advantages of webflux](./21-webflux-advantages.webp)

### 2.2 Considerations of webflux

![Considerations of webflux](./22-webflux-Considerations.webp)


> References
- https://www.youtube.com/watch?v=M3jNn3HMeWg&t=71s