#!/bin/bash

# Function to prompt for and set AWS credentials
setup_aws() {
    read -p "Enter your AWS Access Key ID: " AWS_ACCESS_KEY_ID
    read -s -p "Enter your AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
    echo
    read -p "Enter your AWS Default Region: " AWS_DEFAULT_REGION

    echo "Configuring AWS credentials..."
    aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
    aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
    aws configure set default.region $AWS_DEFAULT_REGION
}

# Function to prompt for and set GCP credentials
setup_gcp() {
    read -p "Enter the path to your GCP service account JSON file: " GCP_CREDENTIALS_FILE
    export GOOGLE_CLOUD_KEYFILE_JSON=$GCP_CREDENTIALS_FILE
    gcloud auth activate-service-account --key-file $GCP_CREDENTIALS_FILE
}

# Function to prompt for and set Azure credentials
setup_azure() {
    read -p "Enter your Azure Client ID: " AZURE_CLIENT_ID
    read -s -p "Enter your Azure Client Secret: " AZURE_CLIENT_SECRET
    echo
    read -p "Enter your Azure Tenant ID: " AZURE_TENANT_ID
    read -p "Enter your Azure Subscription ID: " AZURE_SUBSCRIPTION_ID

    echo "Configuring Azure credentials..."
    az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
    az account set --subscription $AZURE_SUBSCRIPTION_ID
}

read -p "Type y to set up AWS credentials. Or press Enter to skip: " YES_AWS
if [ "$YES_AWS" = "y" ]; then
    setup_aws
fi

read -p "Type y to set up GCP credentials. Or press Enter to skip: " YES_GCP
if [ "$YES_GCP" = "y" ]; then
    setup_gcp
fi

read -p "Type y to set up Azure credentials. Or press Enter to skip: " YES_AZURE
if [ "$YES_AZURE" = "y" ]; then
    setup_gcp
fi