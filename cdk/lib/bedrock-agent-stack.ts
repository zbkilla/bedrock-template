import * as cdk from 'aws-cdk-lib';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { readFileSync } from 'fs';
import * as path from 'path';

interface BedrockAgentStackProps extends cdk.StackProps {
  agentName?: string;
  foundationModel?: string;
}

export class BedrockAgentStack extends cdk.Stack {
  public readonly agentId: string;
  public readonly agentAliasId: string;

  constructor(scope: Construct, id: string, props?: BedrockAgentStackProps) {
    super(scope, id, props);

    const agentName = props?.agentName ?? 'bedrock-agent';
    const foundationModel = props?.foundationModel ?? 'anthropic.claude-3-sonnet-20240229-v1:0';

    // Agent execution role
    const agentRole = new iam.Role(this, 'AgentRole', {
      roleName: `${agentName}-role`,
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      description: 'Role for Bedrock Agent execution',
    });

    // Add Bedrock model invocation permissions
    agentRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['bedrock:InvokeModel'],
      resources: [`arn:aws:bedrock:${this.region}::foundation-model/${foundationModel}`],
    }));

    // Lambda function for action group
    const actionHandler = new lambda.Function(this, 'ActionHandler', {
      functionName: `${agentName}-action-handler`,
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/actions')),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        AGENT_NAME: agentName,
      },
    });

    // Allow Bedrock to invoke the Lambda
    actionHandler.addPermission('BedrockInvoke', {
      principal: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceArn: `arn:aws:bedrock:${this.region}:${this.account}:agent/*`,
    });

    // Load agent instructions
    const instructions = readFileSync(
      path.join(__dirname, '../../prompts/instructions.txt'),
      'utf-8'
    );

    // Load OpenAPI schema
    const openApiSchema = readFileSync(
      path.join(__dirname, '../../schemas/openapi.yaml'),
      'utf-8'
    );

    // Create Bedrock Agent
    const agent = new bedrock.CfnAgent(this, 'Agent', {
      agentName: agentName,
      foundationModel: foundationModel,
      instruction: instructions,
      agentResourceRoleArn: agentRole.roleArn,
      idleSessionTtlInSeconds: 600,
      autoPrepare: true,
      actionGroups: [
        {
          actionGroupName: 'DefaultActions',
          actionGroupExecutor: {
            lambda: actionHandler.functionArn,
          },
          apiSchema: {
            payload: openApiSchema,
          },
          description: 'Default action group for agent operations',
        },
      ],
    });

    // Create agent alias for deployment
    const agentAlias = new bedrock.CfnAgentAlias(this, 'AgentAlias', {
      agentId: agent.attrAgentId,
      agentAliasName: 'prod',
      description: 'Production alias for the Bedrock agent',
    });

    // Ensure alias is created after agent
    agentAlias.addDependency(agent);

    // Store IDs for reference
    this.agentId = agent.attrAgentId;
    this.agentAliasId = agentAlias.attrAgentAliasId;

    // Outputs
    new cdk.CfnOutput(this, 'AgentId', {
      value: agent.attrAgentId,
      description: 'Bedrock Agent ID',
      exportName: `${agentName}-agent-id`,
    });

    new cdk.CfnOutput(this, 'AgentAliasId', {
      value: agentAlias.attrAgentAliasId,
      description: 'Bedrock Agent Alias ID',
      exportName: `${agentName}-alias-id`,
    });

    new cdk.CfnOutput(this, 'ActionHandlerArn', {
      value: actionHandler.functionArn,
      description: 'Action Handler Lambda ARN',
    });
  }
}
