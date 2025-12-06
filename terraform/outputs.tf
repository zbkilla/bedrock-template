output "agent_id" {
  description = "The ID of the Bedrock agent"
  value       = aws_bedrockagent_agent.main.id
}

output "agent_alias_id" {
  description = "The ID of the agent alias"
  value       = aws_bedrockagent_agent_alias.prod.agent_alias_id
}

output "agent_arn" {
  description = "The ARN of the Bedrock agent"
  value       = aws_bedrockagent_agent.main.agent_arn
}

output "lambda_function_arn" {
  description = "ARN of the action handler Lambda"
  value       = aws_lambda_function.action_handler.arn
}

output "invoke_command" {
  description = "AWS CLI command to invoke the agent"
  value       = "aws bedrock-agent-runtime invoke-agent --agent-id ${aws_bedrockagent_agent.main.id} --agent-alias-id ${aws_bedrockagent_agent_alias.prod.agent_alias_id} --session-id test-session --input-text 'Hello'"
}
