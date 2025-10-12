import os

import requests
from dotenv import find_dotenv, load_dotenv

from agents.matmaster_agent.constant import OPENAPI_JOB_CREATE_API

load_dotenv(find_dotenv())

MATERIALS_ACCESS_KEY = os.getenv('MATERIALS_ACCESS_KEY')
MATERIALS_PROJECT_ID = os.getenv('MATERIALS_PROJECT_ID')

request_body_json = {'projectId': MATERIALS_PROJECT_ID, 'name': 'demo_job'}
request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}

response = requests.post(
    OPENAPI_JOB_CREATE_API, json=request_body_json, params=request_query_string
)
print(response)
