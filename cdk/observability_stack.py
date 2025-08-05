from aws_cdk import (
    aws_cloudwatch as cw,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_cloudwatch_actions as actions,
    Duration,
    Stack
)
from constructs import Construct

class ObservabilityStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Dashboard
        dashboard = cw.Dashboard(self, "AppDashboard")
        cpu_metric = cw.Metric(
            namespace="AWS/ECS",
            metric_name="CPUUtilization",
            statistic="Average",
            dimensions_map={"ClusterName": "AppCluster"},
            period=Duration.minutes(1)
        )

        dashboard.add_widgets(
            cw.GraphWidget(
                title="Fargate CPU Usage",
                left=[cpu_metric]
            )
        )

        # SNS topic and subscription
        topic = sns.Topic(self, "CpuAlarmTopic")
        topic.add_subscription(subs.EmailSubscription("tmwinfotec@gmail.com"))

        # CloudWatch Alarm
        alarm = cw.Alarm(
            self, "FargateCpuHighAlarm",
            metric=cpu_metric,
            threshold=70,
            evaluation_periods=2,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD
        )

        # Attach SNS topic to alarm
        alarm.add_alarm_action(actions.SnsAction(topic))
