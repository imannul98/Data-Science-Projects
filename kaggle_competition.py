# -*- coding: utf-8 -*-
"""Kaggle Competition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1htGc_ZaROCksIIgvV23F9ZUEvumXSIiC
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from google.colab import drive
drive.mount('/content/drive')

df=pd.read_csv('/content/drive/MyDrive/Colab Notebooks/train.csv')
print('Shape of Data:', df.shape)
df.head()

df_type=df.dtypes
df_type.unique()

df_type[df_type=='int64'].shape

df_type[df_type=='float64'].shape

df_type[df_type=='O'].shape

df_missing=pd.DataFrame(df.isna().sum(),columns=['NaN'])
df_missing['ratio_NaN']=df_missing['NaN']/df.shape[0]*100
display(df_missing.sort_values('ratio_NaN',ascending=False).head(10))
fig,ax=plt.subplots(figsize=(20,10))
df_missing['ratio_NaN'].plot(ylim=(0, 100), figsize=(15,5))
plt.title('NaN Values Percentage')
plt.show()

df1=df.drop(df_missing[df_missing['ratio_NaN']>10].index,axis=1)
df_missing=pd.DataFrame(df1.isna().sum(),columns=['NaN'])
df_missing['ratio_NaN']=df_missing['NaN']/df1.shape[0]*100
display(df_missing.sort_values('ratio_NaN',ascending=False).head(10))
fig,ax=plt.subplots(figsize=(20,10))
df_missing['ratio_NaN'].plot(ylim=(0, 100), figsize=(15,5))
plt.title('Missing Value Percentage')
plt.show()

import missingno as msno
msno.matrix(df1.loc[:,df_missing[(df_missing['ratio_NaN']>0)&(df_missing['ratio_NaN']<70)].index].sort_values('roam_og_mou_8'),fontsize=12)
plt.title('Missing Values Matrix')
plt.show()
msno.heatmap(df1.loc[:,df_missing[(df_missing['ratio_NaN']>0)&(df_missing['ratio_NaN']<70)].index].sort_values('roam_og_mou_8'),fontsize=8)

display(df_type[df_type.index.isin(df_missing[df_missing['ratio_NaN']>0].index)].value_counts())
df_type1=df1.dtypes
display(df1[df_type1[df_type1=='O'].index])

def create_woe_iv(df,feature,target):
    return (pd.crosstab(df[feature],df[target],normalize='columns')
            .assign(woe=lambda dfx: np.log(dfx[1] / dfx[0]))
            .assign(iv=lambda dfx: np.sum(dfx['woe']*(dfx[1]-dfx[0]))))

df_woe_iv = create_woe_iv(df,'date_of_last_rech_6','churn_probability')
display(df_woe_iv)

df_woe_iv = create_woe_iv(df,'date_of_last_rech_7','churn_probability')
display(df_woe_iv)

df_woe_iv = create_woe_iv(df,'date_of_last_rech_8','churn_probability')
display(df_woe_iv)

from sklearn.impute import SimpleImputer
imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
df1[df_type1[df_type1=='float64'].index]=imp_mean.fit_transform(df1[df_type1[df_type1=='float64'].index])

"""# Exploratory Data Analysis"""

display(df['churn_probability'].value_counts())
sns.countplot(x='churn_probability',data=df)
plt.title('Count of Labels')
plt.show()

df1=df1.set_index('id')
df1

display(df1[df_type1[df_type1=='O'].index].describe())
df1=df1.drop(['last_date_of_month_6','last_date_of_month_7','last_date_of_month_8'],axis=1)

df1['date_of_last_rech_6'].fillna('6/30/2014',inplace=True)
df1['date_of_last_rech_7'].fillna('7/31/2014',inplace=True)
df1['date_of_last_rech_8'].fillna('8/31/2014',inplace=True)

for x in ['date_of_last_rech_6','date_of_last_rech_7','date_of_last_rech_8']:
    df1[x]=pd.to_datetime(df1[x])
df1[['date_of_last_rech_6','date_of_last_rech_7','date_of_last_rech_8']]

df1[['date_of_last_rech_6','date_of_last_rech_7','date_of_last_rech_8']]
df1['date_of_last_rech_6']=(pd.to_datetime('2014-6-30')-df1['date_of_last_rech_6']).astype('int64')/(3600*24*1000000000)
df1['date_of_last_rech_7']=(pd.to_datetime('2014-7-31')-df1['date_of_last_rech_7']).astype('int64')/(3600*24*1000000000)
df1['date_of_last_rech_8']=(pd.to_datetime('2014-8-31')-df1['date_of_last_rech_8']).astype('int64')/(3600*24*1000000000)
df1[['date_of_last_rech_6','date_of_last_rech_7','date_of_last_rech_8','churn_probability']].corr()

df1.describe()

def outliers(df,col):
    q1=np.percentile(df[col],25)
    q3=np.percentile(df[col],75)
    iqr=q3-q1
    upper_outliers=q3+1.5*iqr
    lower_outliers=q1-1.5*iqr
    df[col]=[x if x<upper_outliers else upper_outliers for x in df[col]]
    df[col]=[x if x>lower_outliers else lower_outliers for x in df[col]]
    return df[col]

y=df1[['churn_probability']]
for x in df1.columns:
    df1[x]=outliers(df1,x)

df1.describe()

from sklearn.preprocessing import MinMaxScaler

def variance(df):
    mms=MinMaxScaler()
    summary_statistics=pd.DataFrame(mms.fit_transform(df), columns=df.columns).describe()
    return summary_statistics.loc['std']**2

variance_df=variance(df1)
fig,ax=plt.subplots(figsize=(20,10))
variance_df.sort_values().plot(kind='bar')
plt.title('Variance')
plt.show()

df2=df1.drop(variance_df[variance_df==0].index,axis=1)
df2.describe()

df2=pd.concat([df2,y],axis=1)
df2.describe()

df2[['date_of_last_rech_8','churn_probability']].corr()

fig,ax=plt.subplots(figsize=(20,10))
correlation_to_target=abs(df2.corr().loc['churn_probability'])
correlation_to_target.drop('churn_probability',axis=0).sort_values(ascending=False).plot(kind='bar')
plt.axhline(correlation_to_target.drop('churn_probability',axis=0).mean(),color='red',label='Average Correlation')
plt.axhline(correlation_to_target.drop('churn_probability',axis=0).median(),color='green',label='Median Correlation')
plt.axhline(0.1,color='yellow',label='Limit to Filter')
plt.title('Correlation to Target')
plt.legend()
plt.show()

df3=df2.drop(correlation_to_target[correlation_to_target<0.1].index,axis=1)
df3

fig,ax=plt.subplots(figsize=(20,10))
sns.heatmap(df3.corr(),annot=True)
plt.title('Correlation')
plt.show()

def korelasi(data,threshold):
    col_corr=set()
    corr_matrix=data.corr()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i,j])>threshold:
                colname=corr_matrix.columns[i]
                col_corr.add(colname)
    return col_corr
df4=df3.drop(korelasi(df3,0.9),axis=1)
df4

df4.columns

for x in df4.columns:
    sns.scatterplot(x=x,y='churn_probability',data=df4,alpha=0.1)
    plt.title(f'Scatterplot of {x} against Churn Probability')
    plt.show()
    
    sns.histplot(x=x,data=df4,hue='churn_probability')
    plt.title(f'Histogram of {x}')
    plt.show()

"""# Modelling"""

from imblearn.over_sampling import RandomOverSampler
from collections import Counter

df4=df4.reset_index(drop=True)
X=df4.drop('churn_probability',axis=1)
y=df4[['churn_probability']]

oversample = RandomOverSampler(sampling_strategy=0.5)

X_over,y_over=oversample.fit_resample(X,y)

display(y.value_counts())
y.value_counts().plot(kind='bar')
plt.title('Before Resampling')
plt.show()

display(y_over.value_counts())
y_over.value_counts().plot(kind='bar')
plt.title('After Resampling')
plt.show()

62867/7132

from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test=train_test_split(X_over,y_over,test_size=0.3,stratify=y_over)

y_train=y_train.values.ravel()
y_test=y_test.values.ravel()

#Model 1: XGBoost
import xgboost as xgb
from sklearn.metrics import roc_auc_score,confusion_matrix,roc_curve,accuracy_score
from sklearn.model_selection import cross_val_score,GridSearchCV


#Menginisiasi Model
model_prototype = xgb.XGBClassifier(objective ='binary:logistic', n_estimators = 100,
                                    use_label_encoder=False,eval_metric='mlogloss',max_depth=6,learning_rate=0.05)


model_prototype.fit(X_train,y_train)

#Melakukan Prediksi
proba=model_prototype.predict_proba(X_test)[:,1]
pred=model_prototype.predict(X_test)

#Evaluasi Model
TN, FP, FN, TP = confusion_matrix(y_test,pred).ravel()


def cm_score(tn,fp,fn,tp):
    tpr=tp/(tp+fn)
    tnr=tn/(tn+fp)
    ppv=tp/(tp+fp)
    npv=tn/(tn+fn)
    fpr=fp/(fp+tn)
    fnr=fn/(tp+fn)
    fdr=fp/(tp+fp)
    return tpr,tnr,ppv,npv,fpr,fnr,fdr

TPR,TNR,PPV,NPV,FPR,FNR,FDR=cm_score(TN, FP, FN, TP)

print('True Negative:',TN)
print('False Positive:',FP)
print('False Negative:',FN)
print('True Positive:',TP)
print('Recall:',TPR)
print('False Positive Rate:',FPR)
print('Precision:',PPV)
print('Specificity:',TNR)

auc_score_train=roc_auc_score(y_train,model_prototype.predict_proba(X_train)[:,1])
auc_score_test=roc_auc_score(y_test,proba)

print('AUC Score training data:',auc_score_train)
print('AUC Score test data:',auc_score_test)

cv=cross_val_score(model_prototype,X_test,y_test,cv=5)
print('AUC Score Cross-Validation:',cv.mean())
print('Accuracy:',accuracy_score(y_test,pred))

from hyperopt import STATUS_OK, Trials, fmin, hp, tpe

space={'max_depth': hp.quniform("max_depth", 3, 8, 1),
        'learning_rate': hp.quniform ('learning_rate', 0.05,0.5,0.01),
        'n_estimators' : hp.quniform('n_estimators', 50,500,50)
    }

def objective(space):
    clf=xgb.XGBClassifier(
                    n_estimators =int(space['n_estimators']), max_depth = int(space['max_depth']), learning_rate = space['learning_rate'])
    
    evaluation = [( X_train, y_train), ( X_test, y_test)]
    
    clf.fit(X_train, y_train,
            eval_set=evaluation, eval_metric="auc",
            early_stopping_rounds=10,verbose=False)
    

    pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, pred>0.5)
    print ("SCORE:", accuracy)
    return {'loss': -accuracy, 'status': STATUS_OK }

#trials = Trials()

#best_hyperparams = fmin(fn = objective,
                        #space = space,
                        #algo = tpe.suggest,
                        #max_evals = 100,
                        #trials = trials)

#best_hyperparams

#Model 1: XGBoost
import xgboost as xgb
from sklearn.metrics import roc_auc_score,confusion_matrix,roc_curve,accuracy_score
from sklearn.model_selection import cross_val_score,GridSearchCV


#Menginisiasi Model
model_prototype = xgb.XGBClassifier(objective ='binary:logistic', n_estimators = 500,
                                    use_label_encoder=False,eval_metric='mlogloss',max_depth=6,learning_rate=0.25)


model_prototype.fit(X_train,y_train)

#Melakukan Prediksi
proba=model_prototype.predict_proba(X_test)[:,1]
pred=model_prototype.predict(X_test)

#Evaluasi Model
TN, FP, FN, TP = confusion_matrix(y_test,pred).ravel()


def cm_score(tn,fp,fn,tp):
    tpr=tp/(tp+fn)
    tnr=tn/(tn+fp)
    ppv=tp/(tp+fp)
    npv=tn/(tn+fn)
    fpr=fp/(fp+tn)
    fnr=fn/(tp+fn)
    fdr=fp/(tp+fp)
    return tpr,tnr,ppv,npv,fpr,fnr,fdr

TPR,TNR,PPV,NPV,FPR,FNR,FDR=cm_score(TN, FP, FN, TP)

print('True Negative:',TN)
print('False Positive:',FP)
print('False Negative:',FN)
print('True Positive:',TP)
print('Recall:',TPR)
print('False Positive Rate:',FPR)
print('Precision:',PPV)
print('Specificity:',TNR)

auc_score_train=roc_auc_score(y_train,model_prototype.predict_proba(X_train)[:,1])
auc_score_test=roc_auc_score(y_test,proba)

print('AUC Score training data:',auc_score_train)
print('AUC Score test data:',auc_score_test)

cv=cross_val_score(model_prototype,X_test,y_test,cv=5)
print('AUC Score Cross-Validation:',cv.mean())
print('Accuracy:',accuracy_score(y_test,pred))

import shap

explainer = shap.Explainer(model_prototype)
shap_values = explainer(X_test)

# visualize the first prediction's explanation
#shap.plots.waterfall(shap_values[0])

#pip install javascript

shap.initjs()
shap.plots.force(shap_values[0])

shap.initjs()
shap.plots.beeswarm(shap_values)

shap.initjs()
shap.plots.bar(shap_values)