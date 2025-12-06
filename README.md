# AWS Bedrock Agent Template

Infrastructure as Code template for deploying Amazon Bedrock Agents with CDK, Terraform, or CloudFormation.

## Features

- **Multi-IaC Support**: Choose CDK (TypeScript), Terraform, or CloudFormation
- **Action Groups**: Lambda-backed tools for agent capabilities
- **Knowledge Bases**: RAG integration with your data sources
- **Guardrails**: Content filtering and safety controls
- **CI/CD Ready**: GitHub Actions workflows included

## Project Structure

```
bedrock-template/
├── cdk/                    # AWS CDK (TypeScript)
│   ├── lib/
│   │   └── bedrock-agent-stack.ts
│   ├── bin/
│   │   └── app.ts
│   └── package.json
├── terraform/              # Terraform
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── cloudformation/         # CloudFormation
│   └── template.yaml
├── lambda/                 # Action handler functions
│   └── actions/
│       └── handler.py
├── schemas/                # OpenAPI schemas for action groups
│   └── openapi.yaml
├── prompts/                # Agent instructions
│   └── instructions.txt
└── .github/
    └── workflows/
        └── deploy.yaml
```

## Quick Start

### Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js 18+ (for CDK)
- Python 3.12+ (for Lambda)
- Terraform 1.5+ (if using Terraform)

### Deploy with CDK

```bash
cd cdk
npm install
npx cdk deploy
```

### Deploy with Terraform

```bash
cd terraform
terraform init
terraform apply
```

### Deploy with CloudFormation

```bash
aws cloudformation deploy \
  --template-file cloudformation/template.yaml \
  --stack-name bedrock-agent \
  --capabilities CAPABILITY_IAM
```

## Configuration

### Agent Instructions

Edit `prompts/instructions.txt` to customize your agent's behavior and personality.

### Action Groups

1. Define your API in `schemas/openapi.yaml`
2. Implement the handler in `lambda/actions/handler.py`
3. Update the IaC to include the new action group

### Knowledge Bases

Configure knowledge base integration by:
1. Creating an S3 bucket with your documents
2. Setting up the vector database (OpenSearch Serverless recommended)
3. Updating the IaC with knowledge base association

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_REGION` | AWS region for deployment | Yes |
| `FOUNDATION_MODEL` | Bedrock model ID | Yes |
| `AGENT_NAME` | Name for your agent | Yes |

## Supported Models

- `anthropic.claude-3-5-sonnet-20241022-v2:0`
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `amazon.titan-text-premier-v1:0`
- `meta.llama3-70b-instruct-v1:0`

## License

MIT
