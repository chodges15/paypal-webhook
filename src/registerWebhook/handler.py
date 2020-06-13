import json
import os
import boto3
from botocore.exceptions import ClientError
import paypalrestsdk

def get_secret(secret_name):
  secrets_namespace = os.environ['SECRETS_NAMESPACE']
  secret_id = secrets_namespace + secret_name
  try:
    response = client.get_secret_value(SecretId=secret_id)
  except ClientError as e:
    print("Error fetching secret")
    exit(1)
  else:
    return response['SecretString']


def handler(message, context):
  secretsRegion = os.environ['SECRETS_REGION']

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
    "url": "https://www.yeowza.com/paypal_webhook",
    "event_types": [
        {
            "name": "PAYMENT.AUTHORIZATION.CREATED"
        },
        {
            "name": "PAYMENT.AUTHORIZATION.VOIDED"
        }
    ]
  })


  return {}