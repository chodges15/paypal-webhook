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


def handler(message, context):
  secretsRegion = os.environ['SECRETS_REGION']
  status = "error"
  session = boto3.session.Session()
  client = session.client(
      service_name='secretsmanager',
      region_name=secretsRegion
  )

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
    status = "success"
    logger.info("Webhook[%s] created successfully" % (webhook.id))
  else:
    logger.error(webhook.error)


  return { 
    'status' : status
  }