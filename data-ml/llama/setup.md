
# llama 2 model setup 


```shell
no_proxy=* git clone  https://github.com/ggerganov/llama.cpp.git
```

```shell
LLAMA_META=1 make
```


```shell
# install git large file storage
brew install git-lfs
# download from huggingface.co

# cat splitted model files into one.
cat llama-2-13b-chat-q4_0.gguf.* > llama-2-13b-chat-q4_0.gguf

# start the web ui
./server -m ../../ML/llama-2-13b-chat-q4_0.gguf -port 8000
```


## references

https://aitoolmall.com/news/how-to-use-huggingface-llama-2/

https://huggingface.co/Ywung/llama-models/tree/main/codellama

https://git-lfs.com/

https://github.com/ggerganov/llama.cpp

https://github.com/facebookresearch/llama