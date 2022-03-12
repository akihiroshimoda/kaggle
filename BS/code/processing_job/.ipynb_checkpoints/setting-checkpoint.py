#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pytz import timezone

S3PATH_ENV    = "shimoda_env" # additional env configuration, comment it out if not use
S3PATH_CONF = "NBE-JP3_DS_Engine"
S3PATH_INPUT  = "lf_test/MM/Data"
S3PATH_CODE   = "lf_test/MM/Code"
S3PATH_OUTPUT = "lf_test/MM/output"

JOBNAME_PREFIX = "AL"
INSTANCE_TYPE  = "ml.p2.xlarge"
RUN_TIME_LIMIT = 432000 #seconds, 86400=24h, 172800=48h, 259200=72h, 432000=120h=max
VOLUME_SIZE    = 30 #GB

CONTAINER_IMAGE = '121021644041.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3'

NBS_REGION_NAME = 'ap-southeast-1'
DEV_PREFIX  = 'datalake-lab-hh-jpn-pcvnbs'  #'pcvnbs'
UAT_PREFIX  = 'datalake-lab-hh-jpn-nbsuat'  #'nbsuat'
PROD_PREFIX = 'datalake-lab-hh-jpn-nbsprod' #'nbsprod'
TOKYO = timezone('Asia/Tokyo')
PROXIES = {'http': 'sgtuac.merck.com:8080', 'https': 'sgtuac.merck.com:8080'}