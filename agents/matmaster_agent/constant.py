import os

from dotenv import load_dotenv

load_dotenv()

FRONTEND_STATE_KEY = "frontend_state"
TMP_FRONTEND_STATE_KEY = "tmp_frontend_state"

# Matmaster Constants
MATMASTER_AGENT_NAME = "matmaster_agent"

# Agent Constant
ModelRole = "model"

# DB
DBUrl = os.getenv("SESSION_API_URL")

# Bohrium Constant
BohriumStorge = {
    "type": "https",
    "plugin": {
        "type": "bohrium",
        "access_key": "",
        "project_id": -1,
        "app_key": "agent"
    }
}
LOCAL_EXECUTOR = {
    "type": "local"
}

BohriumExecutor = {
    "type": "dispatcher",
    "machine": {
        "batch_type": "OpenAPI",
        "context_type": "OpenAPI",
        "remote_profile": {
        "access_key": "",
        "project_id": -1,
            "app_key": "agent",
            "image_address": "registry.dp.tech/dptech/dp/native/prod-19853/dpa-mcp:0.0.0",
            "platform": "ali",
            "machine_type": "c32_m64_cpu"
        }
    },
    "resources": {
        "envs": {}
    }
}

OPENAPI_HOST = ""
DFLOW_HOST = ""
DFLOW_K8S_API_SERVER = ""
BOHRIUM_API_URL = ""

CURRENT_ENV = os.getenv("OPIK_PROJECT_NAME", "prod")
if CURRENT_ENV == "test":
    OPENAPI_HOST = "https://openapi.test.dp.tech"
    DFLOW_HOST = "https://lbg-workflow-mlops.test.dp.tech"
    DFLOW_K8S_API_SERVER = "https://lbg-workflow-mlops.test.dp.tech"
    BOHRIUM_API_URL = "https://bohrium-api.test.dp.tech"
elif CURRENT_ENV == "uat":
    OPENAPI_HOST = "https://openapi.uat.dp.tech"
    BOHRIUM_API_URL = "https://bohrium-api.uat.dp.tech"
elif CURRENT_ENV == "prod":
    OPENAPI_HOST = "https://openapi.dp.tech"
    DFLOW_HOST = "https://workflows.deepmodeling.com"
    DFLOW_K8S_API_SERVER = "https://workflows.deepmodeling.com"
    BOHRIUM_API_URL = "https://bohrium-api.dp.tech"

DFlowExecutor = {
    "type": "local",
    "dflow": True,
    "env": {
        "DFLOW_HOST": DFLOW_HOST,
        "DFLOW_K8S_API_SERVER": DFLOW_K8S_API_SERVER,
        "DFLOW_S3_REPO_KEY": "oss-bohrium",
        "DFLOW_S3_STORAGE_CLIENT": "dflow.plugins.bohrium.TiefblueClient",
        "BOHRIUM_ACCESS_KEY": "",
        "BOHRIUM_PROJECT_ID": "",
        "BOHRIUM_APP_KEY": "agent"
    }
}


def get_BohriumExecutor():
    return BohriumExecutor


def get_DFlowExecutor():
    return DFlowExecutor


def get_BohriumStorage():
    return BohriumStorge


Transfer2Agent = "transfer_to_agent"

LOADING_STATE_KEY = "loading_state"
LOADING_START = "loading_start"
LOADING_END = "loading_end"
LOADING_DESC = "loading_desc"
LOADING_TITLE = "loading_title"

JOB_RESULT_KEY = "job_result"
JOB_LIST_KEY = "job_list"
