# Locally hosting an LLM

While the setup process for the vLLM completion server isn't terribly complicated, containerizing the process is highly recommended. In this folder you'll see a Dockerfile and a docker-compose file, which can be used as a drop-in replacement for the standard OpenAI ChatGPT server. 

Running an LLM in this way requires that the [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html) be installed. 

Follow the steps on the Nvidia website to setup CUDA driver interfaces for your given container runtime. As per the instructions, you can run the following docker command to test that everything is running smoothly:

```bash
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

Once those libraries have been installed, the local server can be spun up with a good 'ol 

```bash
docker compose up
```

A server mimicking the OpenAI API protocol should now be running on port **8000**

The dockerfile is just running the steps from [this](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-compatible-server) how-to from vLLM. The containerization step is optional, but highly recommended.


---

<br />

> NOTE: This process has only been tested on linux.