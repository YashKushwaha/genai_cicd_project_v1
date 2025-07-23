## Overview

In my previous Generative AI projects:

* I explored both open-source large language models (LLMs) such as **Phi-4**, **Mistral**, and **Qwen-3**, as well as commercial solutions like those offered through **AWS Bedrock**.
* The initial approach involved direct integration with LLMs using libraries like the `openai` SDK or tools like **Ollama** for running open-source models locally. This evolved into building structured APIs using **FastAPI**, and eventually, more sophisticated pipelines using frameworks like **LlamaIndex**.
* Early testing was done through tools such as **Jupyter Notebooks** and **Postman**, which later progressed to developing simple front-end interfaces using **HTML**, **CSS**, and **JavaScript** for better user interaction.
* I also integrated external services such as **MongoDB** and **ChromaDB**, which were hosted locally as backend components.

While earlier projects were run locally, the focus has now shifted toward deploying applications that are **publicly accessible** over the internet.

One critical component of building production-ready applications is establishing a **CI/CD pipeline**. Continuous Integration and Continuous Deployment streamline the transition from development to production by automating key steps such as:

* **Building and Packaging:** Application code is containerized into a **Docker image** and pushed to a remote container registry such as **Amazon ECR (Elastic Container Registry)**. This process is managed via **GitHub Actions** workflows.
* **Deployment Automation:** Instead of manually provisioning infrastructure like **EC2 instances**, I now use **Terraform** to automate the creation and management of AWS resources, significantly reducing manual overhead and risk of misconfiguration.
