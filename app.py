#!/usr/bin/env python3
import os

import aws_cdk as cdk

from emr_datapipeline.emr_datapipeline_stack import EmrDatapipelineStack


app = cdk.App()
EmrDatapipelineStack(app, "EmrDatapipelineStack",
    env=cdk.Environment(account=os.environ['AWS_ACCOUNT_ID'], region=os.environ['AWS_REGION']),
    )

app.synth()
