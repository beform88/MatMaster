import os

from dotenv import load_dotenv

load_dotenv()

# Constants from app.utils.constants of f5157ebd1c037940ddf896fa14e01af9106f6e29 at dev/matmodeler
DEFAULT_AGENT_NAME = "chat_agent"
SCHOLAR_DEEP_SEARCH_AGENT = "scholar_deep_search_agent"
CHEMBRAIN_AGENT = "chembrain_agent"
SN_DEEP_RESEARCH_AGENT = "sn_deep_research_agent"

ADK_SESSION_ID_KEY = "adk_session_id"
ADK_AGENT_ID_KEY = "adk_agent_id"
ADK_USER_ID_KEY = "adk_user_id"
FRONTEND_STATE_KEY = "frontend_state"
TMP_FRONTEND_STATE_KEY = "tmp_frontend_state"

# Matmaster Constants
MATMASTER_AGENT_NAME = "matmaster_agent"
DPA_CALCULATIONS_AGENT_NAME = "dpa_calculator_agent"

# Agent Constant
SystemRole = "system"
ModelRole = "model"

# Runner
AppName = "matmodeler"
UserId = "matmodeler_user"

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
    }
}

OpenAPIHost = ""
DFLOW_HOST = ""
DFLOW_K8S_API_SERVER = ""

CurrentEnv = os.getenv("OPIK_PROJECT_NAME", None)
if CurrentEnv == "test":
    OpenAPIHost = "https://openapi.test.dp.tech"
    DFLOW_HOST = "https://lbg-workflow-mlops.test.dp.tech"
    DFLOW_K8S_API_SERVER = "https://lbg-workflow-mlops.test.dp.tech"
elif CurrentEnv == "uat":
    OpenAPIHost = "https://openapi.uat.dp.tech"
elif CurrentEnv == "prod":
    OpenAPIHost = "https://openapi.dp.tech"
    DFLOW_HOST = "https://workflows.deepmodeling.com"
    DFLOW_K8S_API_SERVER = "https://workflows.deepmodeling.com"

DFlowExecutor = {
    "type": "local",
    "dflow": True,
    "env": {
        "DFLOW_HOST": DFLOW_HOST,
        "DFLOW_K8S_API_SERVER": DFLOW_K8S_API_SERVER,
        "DFLOW_S3_REPO_KEY": "oss-bohrium",
        "DFLOW_S3_STORAGE_CLIENT": "dflow.plugins.bohrium.TiefblueClient",
        "BOHRIUM_ACCESS_KEY": "",
        "BOHRIUM_PROJECT_ID": -1,
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
