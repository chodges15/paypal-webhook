import json
import os
import boto3
import paypalrestsdk
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret(secret_name):
  secrets_namespace = os.environ['SECRETS_NAMESPACE']
  secret_id = secrets_namespace + secret_name
  try:
    response = client.get_secret_value(SecretId=secret_id)
  except ClientError as e:
    logger.error("Error fetching secret")
    return ''
  else:
    return response['SecretString']

def get_default_response(message):
    # format documented in https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-responses.html
    return {
      "Status" : "FAILED",
      "Reason" : "unknown",
      "PhysicalResourceId" : message.PhysicalResourceId,
      "StackId" : message.StackId,
      "RequestId" : message.RequestId,
      "LogicalResourceId" : message.LogicalResourceId,
  }

def handle_create(response):
  create_response = response
  paypalrestsdk.configure({
    "mode": "sandbox" if os.environ['SECRETS_NAMESPACE'] == "development" else "live",
    "client_id": get_secret('paypal_client_id'),
    "client_secret": get_secret('paypal_secret') 
  })

  webhook = Webhook({
    "url": os.environ['API_URL'], # stackery magic requires this to be connected to HTTP API as resource
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
  secretsRegion = os.environ['SECRETS_REGION']
  session = boto3.session.Session()
  client = session.client(
      service_name='secretsmanager',
      region_name=secretsRegion
  )

  response = get_default_response(message)

  if message.RequestType == 'Create':
    logger.info('Create called')
    response = create_response(response)
  else if message.RequestType == 'Update':
    logger.info('Update called')
    response.status == 'SUCCESS'
  else if message.RequestType == 'Delete':
    logger.info('Delete called')
    response.status == 'SUCCESS'
  else:
    logger.error(f"Unexpected RequestType: {message.RequestType}")


  return json.dump(response)