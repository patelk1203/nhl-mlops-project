import pandas as pd
import boto3
import time
import os

# 1. Variables
# S3 bucket Name
BUCKET_NAME = 'nhl-mlops-data-kp-2026' 
# IAM ARN 
ROLE_ARN = 'arn:aws:iam::097848836609:role/nhl-sagemaker-role' 

def prepare_and_train():
    print("1. Preparing data for XGBoost...")
    # Load the local CSV we made earlier
    df = pd.read_csv('data/model_ready_data.csv')

    # XGBoost Quirk 1: No strings allowed. Convert team abbreviations to numbers (Label Encoding)
    df['home_team'] = df['home_team'].astype('category').cat.codes
    df['away_team'] = df['away_team'].astype('category').cat.codes

    # XGBoost Quirk 2: The Target column (home_win) MUST be the very first column.
    cols = ['home_win', 'season', 'home_team', 'away_team']
    df = df[cols]

    # XGBoost Quirk 3: No header rows allowed.
    df.to_csv('data/xgboost_ready.csv', index=False, header=False)

    # 2. Upload the fixed CSV to S3
    print("2. Uploading formatted training data to S3...")
    boto3.Session().resource('s3').Bucket(BUCKET_NAME).Object('xgboost_ready.csv').upload_file('data/xgboost_ready.csv')

    # 3. Configure the SageMaker Remote Control (Direct Boto3 Method)
    print("3. Configuring AWS SageMaker (Bypassing SDK to avoid Mac environment errors)...")
    
    # We use the raw boto3 client instead of the buggy sagemaker library
    sm_client = boto3.client('sagemaker', region_name='us-east-1')
    
    # The official AWS XGBoost container URL specifically for us-east-1
    container = '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.5-1'
    
    # Create a unique job name using the current timestamp
    job_name = f'nhl-xgboost-training-{int(time.time())}'

    # 4. Fire the command!
    print("4. Sending START command to AWS. SageMaker is turning on...")
    
    # This raw JSON payload tells AWS exactly how to build the server and run the math
    sm_client.create_training_job(
        TrainingJobName=job_name,
        AlgorithmSpecification={
            'TrainingImage': container,
            'TrainingInputMode': 'File'
        },
        RoleArn=ROLE_ARN,
        InputDataConfig=[{
            'ChannelName': 'train',
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',
                    'S3Uri': f's3://{BUCKET_NAME}/xgboost_ready.csv',
                    'S3DataDistributionType': 'FullyReplicated'
                }
            },
            'ContentType': 'csv'
        }],
        OutputDataConfig={
            'S3OutputPath': f's3://{BUCKET_NAME}/model_output'
        },
        ResourceConfig={
            'InstanceType': 'ml.m5.large', # Free tier eligible server
            'InstanceCount': 1,
            'VolumeSizeInGB': 5
        },
        StoppingCondition={
            'MaxRuntimeInSeconds': 3600
        },
        # The tuning knobs for the algorithm
        HyperParameters={
            'max_depth': '5',
            'eta': '0.2',
            'objective': 'binary:logistic', # Predicting 1 (win) or 0 (loss)
            'num_round': '50'
        }
    )
    
    print("Success! The training server has been ordered.")
    print(f"Job Name: {job_name}")
    print("You can watch the progress in your browser:")
    print("Log into AWS -> Search 'SageMaker' -> Click 'Training Jobs' on the left sidebar.")
    print("It will run for about 3-4 minutes, output the file to S3, and then safely self-destruct!")

if __name__ == "__main__":
    prepare_and_train()