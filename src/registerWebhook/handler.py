import json
import os
import boto3
import botocore.exceptions
import logging
import json
import paypalrestsdk

session = boto3.session.Session()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret(secret_name):
  secretsRegion = os.environ['SECRETS_REGION']
  client = session.client(
      service_name='secretsmanager',
      region_name=secretsRegion
  )
  secrets_namespace = os.environ['SECRETS_NAMESPACE']
  secret_id = secrets_namespace + secret_name
  try:
    response = client.get_secret_value(SecretId=secret_id)
  except botocore.exceptions.ClientError as e:
    logger.error(f"Error fetching secret: {e}")
    return ''
  else:
    return response['SecretString']

def get_default_response(message):
    # format documented in https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-responses.html
    return {
      "Status" : "FAILED",
      "Reason" : "unknown",
      "PhysicalResourceId" : message.get("PhysicalResourceId", default = ""),
      "StackId" : message.get("StackId", default = ""),
      "RequestId" : message.get("RequestId", default = ""),
      "LogicalResourceId" : message.get("LogicalResourceId", default="")
  }

def handle_create(response):
  create_response = response
  paypalrestsdk.configure({
    "mode": "sandbox" if os.environ['SECRETS_NAMESPACE'] == "development" else "live",
    "client_id": get_secret('paypal_client_id'),
    "client_secret": get_secret('paypal_secret') 
  })
  api_url = os.environ.get('API_URL')
  webhook = paypalrestsdk.Webhook({
    "url": api_url, # stackery magic requires this to be connected to HTTP API as resource
    "event_types": [
        {
            "name": "*"
        },
    ]
  })

  if webhook.create():
    create_response.Status = "SUCCESS"
    logger.info(f"Webhook[{webhook.id}] created successfully")
  else:
    create_response.Reason = f"Failed to register webhook with paypal: {webhook.error}"
    logger.error(webhook.error)

  return create_response



def handler(message, context):

  logger.info(f'Message: {message}')
  logger.info(f'Context: {context}')
  response = get_default_response(message)

  if message.RequestType == 'Create':
    logger.info('Create called')
    response = handle_create(response)

  if message.RequestType == 'Update':
    logger.info('Update called')
    response['Status'] == 'SUCCESS'

  if message.RequestType == 'Delete':
    logger.info('Delete called')
    response['Status'] == 'SUCCESS'


  return json.dumps(response)