terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "bedrock-agent"
      ManagedBy = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# IAM Role for Bedrock Agent
resource "aws_iam_role" "agent_role" {
  name = "${var.agent_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "bedrock.amazonaws.com"
      }
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "agent_model_policy" {
  name = "${var.agent_name}-model-policy"
  role = aws_iam_role.agent_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "bedrock:InvokeModel"
      ]
      Resource = "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.foundation_model}"
    }]
  })
}

# Lambda for Action Group
resource "aws_lambda_function" "action_handler" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.agent_name}-action-handler"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      AGENT_NAME = var.agent_name
    }
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/actions"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.agent_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_permission" "bedrock_invoke" {
  statement_id  = "AllowBedrockInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.action_handler.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent/*"
}

# Bedrock Agent
resource "aws_bedrockagent_agent" "main" {
  agent_name              = var.agent_name
  agent_resource_role_arn = aws_iam_role.agent_role.arn
  foundation_model        = var.foundation_model
  instruction             = file("${path.module}/../prompts/instructions.txt")
  idle_session_ttl_in_seconds = 600
  prepare_agent           = true
}

# Action Group
resource "aws_bedrockagent_agent_action_group" "default" {
  agent_id          = aws_bedrockagent_agent.main.id
  agent_version     = "DRAFT"
  action_group_name = "DefaultActions"
  description       = "Default action group for agent operations"

  action_group_executor {
    lambda = aws_lambda_function.action_handler.arn
  }

  api_schema {
    payload = file("${path.module}/../schemas/openapi.yaml")
  }
}

# Agent Alias
resource "aws_bedrockagent_agent_alias" "prod" {
  agent_id         = aws_bedrockagent_agent.main.id
  agent_alias_name = "prod"
  description      = "Production alias"

  depends_on = [aws_bedrockagent_agent_action_group.default]
}
