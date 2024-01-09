FROM pytorch/pytorch:latest

RUN pip install vllm

RUN pip install tiktoken

ARG VLLM_MODEL=meta-llama/Llama-2-70b-hf

CMD python -m vllm.entrypoints.openai.api_server --model $VLLM_MODEL --trust-remote-code