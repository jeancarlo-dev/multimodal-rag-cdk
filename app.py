#!/usr/bin/env python3
import os

import aws_cdk as cdk

from rag_app.rag_app_stack import RagAppStack

app = cdk.App()
RagAppStack(app, "RagAppStack")

app.synth()
