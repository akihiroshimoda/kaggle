#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import boto3
from botocore.config import Config
import datetime
import subprocess
from setting import *

smcli = boto3.client('sts',region_name = NBS_REGION_NAME,config = Config(proxies = PROXIES))
iam_role = smcli.get_caller_identity()['Arn']

def GetTagsAndWorkgroup(region = NBS_REGION_NAME,role = iam_role, dev = DEV_PREFIX, uat = UAT_PREFIX, prod = PROD_PREFIX):
    if prod.split("-")[-1] in role:
        ENV_PREFIX = prod
        workgroup = 'nbsprod'
    elif uat.split("-")[-1] in role:
        ENV_PREFIX = uat
        workgroup = 'nbsuat'
    elif dev.split("-")[-1] in role:
        ENV_PREFIX = dev
        workgroup = 'pcvnbs'
    Tags = boto3.client('iam',region_name = region).list_role_tags(RoleName = ENV_PREFIX + '-admin')['Tags']
    # Adding PREFIX into BillingQualifier
    Tags = [{'Key': j['Key'], 'Value': j['Value']} if j['Key'] != 'BillingQualifier' else {'Key': j['Key'], 'Value': j['Value'].replace('System Resources',ENV_PREFIX)} for j in Tags]
    return(Tags, workgroup)

def CreateProcessingConfig():
    ProcessingInputs = []
    if "S3PATH_ENV" in globals():
        ProcessingInputs.append(
            {'InputName': 'input-env',
             'S3Input': {
                 'S3Uri': 's3://datalake-lab-hh-jpn-{}-data/'.format(workgroup) + S3PATH_ENV,
                 'LocalPath': '/opt/ml/processing/env',
                 'S3DataType': 'S3Prefix',
                 'S3InputMode': 'File',
                 'S3DataDistributionType': 'FullyReplicated',
                 'S3CompressionType': 'None'
             }
            }
        )
    if "S3PATH_CONF" in globals():
        ProcessingInputs.append(
            {'InputName': 'input-conf',
             'S3Input': {
                 'S3Uri': 's3://datalake-lab-hh-jpn-{}-data/'.format(workgroup) + S3PATH_CONF,
                 'LocalPath': '/opt/ml/processing/conf',
                 'S3DataType': 'S3Prefix',
                 'S3InputMode': 'File',
                 'S3DataDistributionType': 'FullyReplicated',
                 'S3CompressionType': 'None'
             }
            }
        )
    if "S3PATH_INPUT" in globals():
        ProcessingInputs.append(
            {'InputName': 'input-data',
             'S3Input': {
                 'S3Uri': 's3://datalake-lab-hh-jpn-{}-data/'.format(workgroup) + S3PATH_INPUT,
                 'LocalPath': '/opt/ml/processing/input',
                 'S3DataType': 'S3Prefix',
                 'S3InputMode': 'File',
                 'S3DataDistributionType': 'FullyReplicated',
                 'S3CompressionType': 'None'
             }
            }
        )
    if "S3PATH_CODE" in globals():
        ProcessingInputs.append(
            {'InputName': 'input-code',
             'S3Input': {
                 'S3Uri': 's3://datalake-lab-hh-jpn-{}-data/'.format(workgroup) + S3PATH_CODE,
                 'LocalPath': '/opt/ml/processing/code',
                 'S3DataType': 'S3Prefix',
                 'S3InputMode': 'File',
                 'S3DataDistributionType': 'FullyReplicated',
                 'S3CompressionType': 'None'
             }
            }
        )
    ProcessingOutputConfig={
    'Outputs': [{
        'OutputName': 'output',
        'S3Output': {
            'S3Uri': 's3://datalake-lab-hh-jpn-{}-data/'.format(workgroup) + S3PATH_OUTPUT,
            'LocalPath': '/opt/ml/processing/output',
            'S3UploadMode': 'EndOfJob'
        },
    }],
    'KmsKeyId': 'arn:aws:kms:ap-southeast-1:970005246817:key/3762a557-519e-4921-b162-ff8129c0d305'
}
    ProcessingJobName='datalake-lab-hh-jpn-{}-{}-{}'.format(workgroup, JOBNAME_PREFIX, datetime.datetime.now(TOKYO).strftime("%Y%m%d-%H%M"))

    ProcessingResources={
        'ClusterConfig': {
            'InstanceCount': 1,
            'InstanceType': INSTANCE_TYPE,
            'VolumeSizeInGB': VOLUME_SIZE,
            'VolumeKmsKeyId': 'arn:aws:kms:ap-southeast-1:970005246817:key/3762a557-519e-4921-b162-ff8129c0d305'
        }
    }
    StoppingCondition = {'MaxRuntimeInSeconds': RUN_TIME_LIMIT}
    
    AppSpecification={
        'ImageUri': CONTAINER_IMAGE,
        'ContainerEntrypoint': [
            '/bin/sh', '/opt/ml/processing/code/run_LR.sh'
        ]
    }
    NetworkConfig={
        'EnableInterContainerTrafficEncryption': False,
        'EnableNetworkIsolation': False,
        'VpcConfig': {
            'SecurityGroupIds': [
                'sg-01d876b0fc338acbb',
            ],
            'Subnets': [
                'subnet-00176524002966338',
            ]
        }
    }
    return(
        ProcessingInputs,
        ProcessingOutputConfig,
        ProcessingJobName,
        ProcessingResources,
        StoppingCondition,
        AppSpecification,
        NetworkConfig
    )

if __name__ == '__main__':    
    Tags, workgroup = GetTagsAndWorkgroup()

    ProcessingInputs,ProcessingOutputConfig,ProcessingJobName,ProcessingResources,\
    StoppingCondition,AppSpecification,NetworkConfig = CreateProcessingConfig()

    client = boto3.client('sagemaker',region_name = NBS_REGION_NAME,config = Config(proxies = PROXIES))
    print(ProcessingJobName)
    
    response = client.create_processing_job(
        ProcessingInputs = ProcessingInputs,
        ProcessingOutputConfig = ProcessingOutputConfig,
        ProcessingJobName = ProcessingJobName,
        ProcessingResources = ProcessingResources,
        StoppingCondition = StoppingCondition,
        AppSpecification = AppSpecification,
        NetworkConfig = NetworkConfig,
        RoleArn = "arn:aws:iam::970005246817:role/datalake-lab-hh-jpn-{}-service".format(workgroup),
        Tags = Tags
    )
    
    print(response)
