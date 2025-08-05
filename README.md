# GenAI Deployment Project

## Overview
In this project I have explored integrating CICD pipelines with genai application development.

This project builds upon my previous work in Generative AI, where I explored both **open-source** and **commercial** large language models (LLMs), including:

- **Open-source LLMs** such as **Phi-4**, **Mistral**, and **Qwen-3**
- **Commercial APIs** available through **AWS Bedrock**

### Evolution of the Approach

1. **Direct Integration with LLMs**  
   - Used the `openai` SDK and tools like **Ollama** for running models locally.  
   - Transitioned to structured APIs using **FastAPI**, and later, advanced pipelines via **LlamaIndex**.

2. **Development & Testing Tools**  
   - Started with **Jupyter Notebooks** and **Postman** for experimentation.  
   - Progressed to building simple front-end interfaces using **HTML**, **CSS**, and **JavaScript**.

3. **Backend Services**  
   - Integrated with services such as **MongoDB** and **ChromaDB**, hosted locally.

### Shift to Cloud Deployment

The focus has now moved to deploying **publicly accessible** applications. A major step toward this has been the integration of a **CI/CD pipeline**, which automates development-to-production workflows.

#### Key CI/CD Components:

- **Build & Packaging**  
  - Application is containerized as a **Docker image** and pushed to **Amazon ECR** using **GitHub Actions**.

- **Automated Deployment**  
  - Infrastructure is provisioned via **Terraform**, replacing manual setup (e.g., EC2 instance creation).

---

## Project Components

### 1. GenAI Chat Engine

- Implements a simple chat engine using the `llama-index` framework.
- Uses the **NOVA Lite** model via **AWS Bedrock** (easily replaceable with other supported models).
- Back-end built using **FastAPI**.
- Simple front-end UI for chat interaction.
- Screenshots of the UI given in the appendix

---

### 2. Terraform Infrastructure

- Automates the provisioning of **EC2 instances** for deployment.
- Infra configurations are externalized to avoid hardcoding.
- Terraform code resides in the [`terraform`](/terraform/) directory.

#### Infra Config

- Infrastructure parameters are defined in [`configs/infra_config.ini`](configs/infra_config.ini)

---

### 3. GitHub Actions Workflows

Automated workflows include:

#### a. **Docker Image Build & Push to ECR**

- Triggered on code commits.
- Builds Docker image and pushes it to **Amazon ECR**.
- AWS credentials are managed via GitHub Secrets.
- A Python [script](/configs/load_config.py) loads ECR details from `infra_config.ini` into the GitHub Actions environment.

#### b. **Terraform: ECR & EC2 Provisioning**

- A separate workflow runs Terraform to:
  - Create the ECR repository
  - Launch EC2 instances based on `infra_config.ini`
- Since GitHub runners are ephemeral, **Terraform state isn't persisted**, risking duplicate resource creation.
- To mitigate this, a Python script checks the current AWS resource status before provisioning.

---

## APPENDIX

Screenshots of Application deployed on EC2

  ![UI Screenshot](/docs/ui%20screenshot.jpg)  

  ![Chat Engine Screenshot](/docs/chat%20engine%20screenshot.jpg)
