from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    Stack
)
from constructs import Construct

class ComputeStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Security Group for ECS Fargate
        app_sg = ec2.SecurityGroup(
            self, "AppSecurityGroup",
            vpc=vpc,
            description="Allow HTTP traffic from internet",
            allow_all_outbound=True
        )
        app_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP")

        # ECS Cluster
        cluster = ecs.Cluster(self, "AppCluster", vpc=vpc)

        # Task Definition with IAM Policy
        fargate_task = ecs.FargateTaskDefinition(self, "TaskDef")

        fargate_task.add_to_task_role_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=["*"]
        ))

        container = fargate_task.add_container(
            "AppContainer",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            memory_limit_mib=512
        )
        container.add_port_mappings(ecs.PortMapping(container_port=80))

        # Fargate Service
        fargate_service = ecs.FargateService(
            self, "FargateService",
            cluster=cluster,
            task_definition=fargate_task,
            desired_count=2,
            security_groups=[app_sg]
        )

        # Load Balancer and Listener
        lb = elbv2.ApplicationLoadBalancer(
            self, "LB",
            vpc=vpc,
            internet_facing=True
        )
        listener = lb.add_listener("PublicListener", port=80, open=True)
        listener.add_targets("AppTarget", port=80, targets=[fargate_service])
