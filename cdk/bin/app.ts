#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BedrockAgentStack } from '../lib/bedrock-agent-stack';

const app = new cdk.App();

// Get configuration from context or environment
const agentName = app.node.tryGetContext('agentName') ?? process.env.AGENT_NAME ?? 'my-bedrock-agent';
const foundationModel = app.node.tryGetContext('foundationModel') ??
  process.env.FOUNDATION_MODEL ??
  'anthropic.claude-3-sonnet-20240229-v1:0';

new BedrockAgentStack(app, 'BedrockAgentStack', {
  agentName,
  foundationModel,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
  },
  description: 'Amazon Bedrock Agent Infrastructure',
  tags: {
    Project: 'bedrock-agent',
    ManagedBy: 'cdk',
  },
});
