#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk import (
  Stack,
  aws_ec2,
  aws_emr
)
from constructs import Construct

class EmrDatapipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        emr_cluster_name = "cdk-demo"
        emr_version = "emr-7.2.0"
        
        # Create a new VPC for EMR cluster
        vpc = aws_ec2.Vpc(self, "EMRStackVPC",
            max_azs=2,
            gateway_endpoints={
                "S3": aws_ec2.GatewayVpcEndpointOptions(
                service=aws_ec2.GatewayVpcEndpointAwsService.S3
                )
            }
        )

        # Use the optional Parameters section to customize your templates. 
        # Parameters enable you to input custom values to your template each time you create or update a stack.
        emr_instances = aws_emr.CfnCluster.JobFlowInstancesConfigProperty(
            core_instance_group=aws_emr.CfnCluster.InstanceGroupConfigProperty(
                instance_count=2,
                instance_type="m5.xlarge",
                market="ON_DEMAND"
            ),
            ec2_subnet_id=vpc.public_subnets[0].subnet_id,
            keep_job_flow_alive_when_no_steps=True, # After last step completes: Cluster waits
            master_instance_group=aws_emr.CfnCluster.InstanceGroupConfigProperty(
                instance_count=1,
                instance_type="m5.xlarge",
                market="ON_DEMAND"
            ),
            termination_protected=False
        )

        # Specifies and EMR cluster resource
        emr_cfn_cluster = aws_emr.CfnCluster(self, "EMRCluster",
            instances=emr_instances,
            # In order to use the default role for `job_flow_role`, you must have already created it using the CLI or console
            job_flow_role="EMR_EC2_DefaultRole",
            name=emr_cluster_name,
            service_role="EMR_DefaultRole",
            applications=[
                aws_emr.CfnCluster.ApplicationProperty(name="Hadoop"),
                aws_emr.CfnCluster.ApplicationProperty(name="Hive"),
                aws_emr.CfnCluster.ApplicationProperty(name="JupyterHub"),
                aws_emr.CfnCluster.ApplicationProperty(name="Livy"),
                aws_emr.CfnCluster.ApplicationProperty(name="Spark"),
                aws_emr.CfnCluster.ApplicationProperty(name="JupyterEnterpriseGateway")
            ],
            bootstrap_actions=None,
            configurations=[
                aws_emr.CfnCluster.ConfigurationProperty(
                classification="delta-defaults",
                configuration_properties={
                    "delta.enabled": "true"
                }),
                aws_emr.CfnCluster.ConfigurationProperty(
                classification="hive-site",
                configuration_properties={
                    "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
                }),
                aws_emr.CfnCluster.ConfigurationProperty(
                classification="spark-hive-site",
                configuration_properties={
                    "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
                })
            ],
            ebs_root_volume_size=32,
            log_uri="s3n://aws-logs-{account}-{region}/elasticmapreduce/".format(account=cdk.Aws.ACCOUNT_ID, region=cdk.Aws.REGION),
            release_label=emr_version,
            scale_down_behavior="TERMINATE_AT_TASK_COMPLETION",
            visible_to_all_users=True
        )

        cdk.CfnOutput(self, 'EmrCluserName', value=emr_cfn_cluster.name)
        cdk.CfnOutput(self, 'EmrVersion', value=emr_cfn_cluster.release_label)       