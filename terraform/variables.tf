variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "agent_name" {
  description = "Name of the Bedrock agent"
  type        = string
  default     = "my-bedrock-agent"
}

variable "foundation_model" {
  description = "Foundation model ID for the agent"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"

  validation {
    condition = can(regex("^(anthropic|amazon|meta|cohere|ai21|mistral)", var.foundation_model))
    error_message = "Foundation model must be from a supported provider."
  }
}

variable "auto_prepare" {
  description = "Whether to automatically prepare the agent after creation (set false for production)"
  type        = bool
  default     = false
}
