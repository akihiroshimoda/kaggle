import pandas as pd
pd.set_option('display.max.columns',None)
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import pickle
import logging
import warnings
warnings.filterwarnings('ignore')
import boto3; s3cli = boto3.client('s3'); s3 = boto3.resource('s3')
import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold
import xgboost as xgb
from sklearn.metrics import roc_curve, auc, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from lightgbm import LGBMClassifier
import lightgbm as lgb
from keras.layers import Dense, Dropout
from keras.models import Sequential
from sklearn.preprocessing import StandardScaler
import shap
import sys
import os

if os.path.exists('/opt/ml/processing/'):
    STEPFUNC = True
    sys.path.append('../conf/')
else:
    STEPFUNC = False

from func import *
from conf3 import *
    
BUCKET_NAME = "datalake-lab-hh-jpn-pcvnbs-data"
if STEPFUNC==True:
    SAVE_DM_FOLDER = '/opt/ml/processing/input/'
    SAVE_OUTPUT = '/opt/ml/processing/output/'

else:
    SAVE_DM_FOLDER = S3PATH_INPUT
    SAVE_OUTPUT = S3PATH_OUTPUT

TRAIN_FNAME = SAVE_DM_FOLDER + '/' + 'train2.csv'
#TEST_FNAME = SAVE_DM_FOLDER + '/' + 'test.csv'

def GetData():
    if STEPFUNC:
        df = pd.read_csv(TRAIN_FNAME)
#     elif os.path.exists('C:/users/shimodak/'):
#         df = pd.read_csv(FILE_PATH_LOCAL+ACTIVITYLEVER_DM_FNAME_LOCAL)
#     else:
#         df = read_csv_s3('s3://{}/{}'.format(BUCKET_NAME, ACTIVITYLEVER_DM_FNAME))    
    return (df)

if __name__ == '__main__':
    train = GetData()
    try: train = train.drop(columns=['Unnamed: 0'])
    except: pass
    
    target_var = 'T1win'
    X_train = train.drop(columns=target_var)
    y_train= train[[target_var]]
    y_train2 = np.ravel(y_train)

    model = LGBMClassifier()
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    param_grid ={'n_estimators':[1000,2000],'max_depth':[4,8,16],'num_leaves':[31,15,7,3],'learning_rate':[0.1,0.05,0.01]}
    grid = GridSearchCV(estimator=model,param_grid=param_grid,n_jobs=-1,cv=cv,scoring='roc_auc')
    grid_result = grid.fit(X_train,y_train2)

    file = SAVE_OUTPUT + 'trained_model_220312.pkl'
    pickle.dump(grid_result, open(file, 'wb'))
    
    
    
    
    
    
    
