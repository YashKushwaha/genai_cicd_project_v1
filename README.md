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

## Components

### The Genai project
- Implements simple chat engine by using `llama-index` framework
- LLM is provided by AWS Bedrock, the project uses novalite model by AWS but it can be easily replaced with other models available on AWS 
- FastAPI is used to build the back end endpoints, a simple Web UI has been created to interact with the application
- Screenshot of application running on EC2 instances can be seen [here](/docs/ui%20screenshot.jpg) & [here](/docs/chat%20engine%20screenshot.jpg) 

### Terraform
- Terraform can be used to automate the creation of EC2 instance for deployment
- Instead of hard coding Infra config in the configuration, the code is designed to take configuration externally
- The code can be found the [terraform](/terraform/) folder of code repository

### Infra config 
- Infra details have been specified in the file `configs/infra_config.ini`

### Github Action Workflows
Following workflows have been created for automation

**Docker image creation and push to ECR** 
- After code has been commited we can use github to build the docker image and push to ECR repository
- AWS credentials are provided as secrets
- A separate python [script](/configs/load_config.py) has been created to read the ECR details from the [infra_config.ini](/configs/infra_config.ini) file and load it into the github actions environment

**ECR repository creation and EC2 instance creation**
- Workflow created to run the Terraform script for creating ECR repository and EC2 instance based on the configuration provided in `infra_config.ini` file
- Since Terraform scripts are run on Github on temporary runners, the terraform state is not saved. Thus we may try to create a resource that already exists. To avoid this we run a python script that check the current status of resources specified in the terraform config file. 

