#!bin/bash

export HTTP_PROXY=http://webproxy.merck.com:8080
export HTTPS_PROXY=http://webproxy.merck.com:8080

# configure the aiml environment
if [ -d /opt/ml/processing/env ]; then
    conda env create -f /opt/ml/processing/env/environment.yml
    . /miniconda3/etc/profile.d/conda.sh
    conda activate aiml
fi

# run the python script
cd /opt/ml/processing/code
#python LightGBM.py BEL > /opt/ml/processing/output/run_seg.log
python CatBoost.py > /opt/ml/processing/output/run_seg.log
#python LogisticRegression.py > /opt/ml/processing/output/run_seg.log