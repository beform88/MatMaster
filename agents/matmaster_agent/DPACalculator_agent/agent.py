import asyncio
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.genai import types

load_dotenv()

# Global Configuration
BOHRIUM_EXECUTOR = {
        "type": "dispatcher",
        "machine": {
            "batch_type": "OpenAPI",
            "context_type": "OpenAPI",
            "remote_profile": {
                "access_key": os.getenv("AK"),
                "project_id":int(os.getenv("BOHRIUM_PROJECT_ID")),
                "image_address": "registry.dp.tech/dptech/dpa-calculator:85b4fe74",
                "job_type": "container",
                "platform": "ali",
                "machine_type": "1 * NVIDIA V100_32g"
            }
        }
}
LOCAL_EXECUTOR = {
    "type": "local"
}
BOHRIUM_STORAGE = {
    "type": "bohrium",
    "username": os.getenv("BOHRIUM_EMAIL"),
    "password": os.getenv("BOHRIUM_PASSWORD"),
    "project_id": int(os.getenv("BOHRIUM_PROJECT_ID"))
}

HTTPS_STORAGE = {
  "type": "https",
  "plugin": {
        "type": "bohrium",
        "username": os.getenv("BOHRIUM_EMAIL"),
        "password": os.getenv("BOHRIUM_PASSWORD"),
        "project_id": int(os.getenv("BOHRIUM_PROJECT_ID"))
    }
}
print('-----', HTTPS_STORAGE)


mcp_tools_dpa = CalculationMCPToolset(
    connection_params=SseServerParams(url="https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=fa66cc76b6724d5590a89546772963fd"),
    storage=HTTPS_STORAGE,
    executor=BOHRIUM_EXECUTOR,
    executor_map={
        "build_bulk_structure": None,
        "build_molecule_structure": None,
        "build_surface_slab": None,
        "build_surface_adsorbate": None
    }
)

root_agent = LlmAgent(
    model=LiteLlm(model="azure/gpt-4o"),
    # model=LiteLlm(model="deepseek/deepseek-chat"),
    name="dpa_calculations_agent",
    description="An agent specialized in computational research using Deep Potential",
    instruction=(
        "You are an expert in materials science and computational chemistry. "
        "Help users perform Deep Potential calculations including structure optimization, molecular dynamics and property calculations. "
        "Use default parameters if the users do not mention, but let users confirm them before submission. "
        "In multi-step workflows involving file outputs, always use the URI of the previous step's file as the input for the next tool. "
        "Always verify the input parameters to users and provide clear explanations of results."
    ),
    tools=[
        mcp_tools_dpa,
    ],
)