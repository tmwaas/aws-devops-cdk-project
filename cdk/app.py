#!/usr/bin/env python3
import aws_cdk as cdk
from networking_stack import NetworkingStack
from compute_stack import ComputeStack
from observability_stack import ObservabilityStack

app = cdk.App()
env = cdk.Environment(region="us-east-1")

network = NetworkingStack(app, "NetworkingStack", env=env)
compute = ComputeStack(app, "ComputeStack", vpc=network.vpc, env=env)
ObservabilityStack(app, "ObservabilityStack", env=env)

app.synth()
