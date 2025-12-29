# AWS Lambda Deployment Guide

This document describes the process used to deploy the wx-api FastAPI application to AWS Lambda using a zip file deployment.

## Prerequisites

- AWS CLI installed and configured
- AWS credentials configured (`aws login` or `aws configure`)
- uv package manager installed
- Python 3.13

## Deployment Steps

### 1. Add Mangum Adapter

Mangum is an adapter that allows ASGI applications (like FastAPI) to run on AWS Lambda.

```bash
uv add mangum
```

**Update main.py:**
```python
from mangum import Mangum

# ... existing FastAPI app code ...

# AWS Lambda handler
handler = Mangum(app)
```

### 2. Export Dependencies

Generate a requirements.txt file from locked dependencies (production only, no dev dependencies):

```bash
uv export --frozen --no-dev --no-editable -o requirements.txt
```

### 3. Install Packages for Lambda Environment

Install dependencies targeting the AWS Lambda runtime environment (x86_64 Linux):

```bash
uv pip install \
  --no-installer-metadata \
  --no-compile-bytecode \
  --python-platform x86_64-manylinux2014 \
  --python 3.13 \
  --target packages \
  -r requirements.txt
```

**Key flags:**
- `--no-installer-metadata`: Reduces package size
- `--no-compile-bytecode`: Skips .pyc compilation (Lambda does this)
- `--python-platform`: Targets Lambda's Linux environment
- `--target packages`: Installs to a local directory

### 4. Create Deployment Package

Create a zip file with dependencies and application code:

```bash
# Package all dependencies
cd packages
zip -r ../package.zip .
cd ..

# Add application code
zip package.zip *.py
zip -r package.zip services/
```

**Result:** `package.zip` (~3.6 MB) ready for deployment

### 5. Create IAM Execution Role

Lambda functions require an IAM role with permissions to execute and write logs:

```bash
# Create the role with Lambda trust policy
aws iam create-role \
  --role-name wx-api-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach basic execution policy (CloudWatch Logs)
aws iam attach-role-policy \
  --role-name wx-api-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Wait for IAM propagation
sleep 10
```

### 6. Create Lambda Function

Deploy the function with the zip package:

```bash
aws lambda create-function \
  --function-name wx-api \
  --runtime python3.13 \
  --zip-file fileb://package.zip \
  --handler main.handler \
  --role arn:aws:iam::<ACCOUNT_ID>:role/wx-api-lambda-role \
  --timeout 30 \
  --memory-size 512 \
  --description "Weather API using FastAPI and Open-Meteo"
```

**Configuration notes:**
- `--handler main.handler`: Points to `handler` variable in `main.py`
- `--timeout 30`: 30 seconds (external API calls need time)
- `--memory-size 512`: 512 MB (adjust based on usage)

### 7. Create Function URL (Public HTTPS Endpoint)

Enable direct HTTPS access without API Gateway:

```bash
aws lambda create-function-url-config \
  --function-name wx-api \
  --auth-type NONE \
  --cors '{
    "AllowOrigins":["*"],
    "AllowMethods":["GET"],
    "AllowHeaders":["*"],
    "MaxAge":86400
  }'
```

### 8. Add Public Access Permission

Allow unauthenticated invocation via the function URL:

```bash
aws lambda add-permission \
  --function-name wx-api \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type NONE
```

## Testing the Deployment

```bash
# Get the function URL
aws lambda get-function-url-config --function-name wx-api

# Test the endpoint
curl "https://<FUNCTION_URL>/weather?location=Denver"
```

**Expected response:**
```json
{
  "location": "Denver",
  "latitude": 39.73915,
  "longitude": -104.9847,
  "country": "United States",
  "area_1": "Colorado",
  "area_2": "Denver",
  "temperature_fahrenheit": 36.2,
  "precipitation_inch": 0.0
}
```

We can also use the OpenAPI UI to verify. Visit `https://<FUNCTION_URL>/docs` and
click through the UI to make requests.

## DDoS Protection and Cost Controls

Lambda functions can scale infinitely, which poses a risk of unexpected costs from DDoS attacks or abuse. Implement these protective measures:

### 1. Set Reserved Concurrency (Hard Limit)

Limit the maximum number of concurrent executions to prevent runaway costs:

```bash
# Limit to 10 concurrent executions
# At 30s timeout, this caps throughput at ~20 req/sec
aws lambda put-function-concurrency \
  --function-name wx-api \
  --reserved-concurrent-executions 10
```

**Impact:**
- Maximum 10 Lambda instances running simultaneously
- Excess requests receive HTTP 429 (throttled) instead of spawning new instances
- Worst case cost: ~$0.03/hour if all instances run continuously

**Adjust the limit** based on expected traffic:
- 5 = ~10 req/sec max
- 10 = ~20 req/sec max (recommended for this API)
- 25 = ~50 req/sec max

### 2. Create SNS Topic for Alerts

Set up a notification channel for all alerts:

```bash
# Create SNS topic
aws sns create-topic --name wx-api-alerts

# Subscribe your email to receive alerts
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:<ACCOUNT_ID>:wx-api-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription via email link
```

### 3. CloudWatch Alarms

Monitor function health and usage patterns:

**High Invocations Alarm** (>1000 requests in 5 minutes):
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name wx-api-high-invocations \
  --alarm-description "Alert when wx-api receives >1000 invocations in 5 minutes" \
  --metric-name Invocations \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=wx-api \
  --alarm-actions arn:aws:sns:us-east-1:<ACCOUNT_ID>:wx-api-alerts
```

**High Error Rate Alarm** (>10% errors over 5 minutes):
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name wx-api-high-errors \
  --alarm-description "Alert when wx-api error rate >10% over 5 minutes" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 0.1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=wx-api \
  --alarm-actions arn:aws:sns:us-east-1:<ACCOUNT_ID>:wx-api-alerts \
  --treat-missing-data notBreaching
```

**Throttle Alarm** (concurrency limit reached):
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name wx-api-throttles \
  --alarm-description "Alert when wx-api is being throttled (concurrency limit reached)" \
  --metric-name Throttles \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=wx-api \
  --alarm-actions arn:aws:sns:us-east-1:<ACCOUNT_ID>:wx-api-alerts \
  --treat-missing-data notBreaching
```

### 4. Budget Alert

Set a monthly cost limit for Lambda with automatic alerts:

```bash
aws budgets create-budget \
  --account-id <ACCOUNT_ID> \
  --budget '{
    "BudgetName": "wx-api-monthly-budget",
    "BudgetLimit": {
      "Amount": "5",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {
      "Service": ["AWS Lambda"]
    }
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {
          "SubscriptionType": "SNS",
          "Address": "arn:aws:sns:us-east-1:<ACCOUNT_ID>:wx-api-alerts"
        }
      ]
    },
    {
      "Notification": {
        "NotificationType": "FORECASTED",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 100,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {
          "SubscriptionType": "SNS",
          "Address": "arn:aws:sns:us-east-1:<ACCOUNT_ID>:wx-api-alerts"
        }
      ]
    }
  ]'
```

**Alerts triggered:**
- At 80% of $5/month budget (~$4)
- When forecasted to exceed 100% of budget

### 5. Monitor Usage

View current metrics in CloudWatch:

```bash
# View invocations in the last hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=wx-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# View concurrent executions
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=wx-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum
```

### Emergency Response

If under attack or experiencing unexpected costs:

```bash
# Option 1: Disable the function URL (503 errors for all requests)
aws lambda delete-function-url-config --function-name wx-api

# Option 2: Reduce concurrency to 1 (severe rate limiting)
aws lambda put-function-concurrency \
  --function-name wx-api \
  --reserved-concurrent-executions 1

# Option 3: Delete the function entirely
aws lambda delete-function --function-name wx-api
```

## Updating the Function

To deploy code changes:

```bash
# Recreate the zip package (steps 2-4)
uv export --frozen --no-dev --no-editable -o requirements.txt
uv pip install --no-installer-metadata --no-compile-bytecode \
  --python-platform x86_64-manylinux2014 --python 3.13 \
  --target packages -r requirements.txt
cd packages && zip -r ../package.zip . && cd ..
zip package.zip *.py
zip -r package.zip services/

# Update function code
aws lambda update-function-code \
  --function-name wx-api \
  --zip-file fileb://package.zip
```

## Cost Considerations

AWS Lambda pricing (as of 2024):
- **Free tier**: 1M requests/month, 400,000 GB-seconds compute
- **After free tier**: ~$0.20 per 1M requests + compute time
- **Function URL**: No additional charge

For this low-traffic API (~10 req/min), costs should remain within free tier.

## Cleanup

To remove the deployment:

```bash
# Delete function
aws lambda delete-function --function-name wx-api

# Delete IAM role
aws iam detach-role-policy \
  --role-name wx-api-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name wx-api-lambda-role
```

## Reference

- [uv AWS Lambda Example](https://github.com/astral-sh/uv-aws-lambda-example)
- [Mangum Documentation](https://mangum.fastapiexpert.com)
- [AWS Lambda Python Deployment](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
- [Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
