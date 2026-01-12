import asyncio
import sys
from typing import Iterable, Optional, Tuple

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import (
    ABACUS_CALCULATOR_URL,
)
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexServerUrl
from agents.matmaster_agent.sub_agents.chembrain_agent.unielf_agent.constant import (
    UNIELF_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_MCPServerUrl,
)
from agents.matmaster_agent.sub_agents.convexhull_agent.constant import (
    ConvexHullServerUrl,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserServerUrl,
)
from agents.matmaster_agent.sub_agents.doe_agent.constant import DOE_SERVER_URL
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPAMCPServerUrl,
)
from agents.matmaster_agent.sub_agents.Electron_Microscope_agent.constant import (
    Electron_Microscope_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.constant import (
    FinetuneDPAServerUrl,
)
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.constant import (
    HEA_assistant_agent_ServerUrl,
)
from agents.matmaster_agent.sub_agents.HEACalculator_agent.constant import (
    HEACALCULATOR_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.HEAkb_agent.constant import HEA_SERVER_URL
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import LAMMPS_URL
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.constant import (
    BOHRIUMPUBLIC_URL,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.constant import (
    MOFDB_URL,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.constant import (
    OPENLAM_URL,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.constant import (
    OPTIMADE_URL,
)
from agents.matmaster_agent.sub_agents.NMR_agent.constant import NMR_MCP_SERVER_URL
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.constant import (
    PEROVSKITE_RESEARCH_URL,
    UNIMOL_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.Physical_adsorption_agent.constant import (
    Physical_Adsorption_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.constant import (
    POLYMER_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.constant import SSE_SERVER_URL
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.constant import (
    STEEL_PREDICT_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.constant import STEEL_SERVER_URL
from agents.matmaster_agent.sub_agents.structure_generate_agent.constant import (
    StructureGenerateServerUrl,
)
from agents.matmaster_agent.sub_agents.superconductor_agent.constant import (
    SuperconductorServerUrl,
)
from agents.matmaster_agent.sub_agents.thermoelectric_agent.constant import (
    ThermoelectricServerUrl,
)
from agents.matmaster_agent.sub_agents.TPD_agent.constant import TPD_MCP_SERVER_URL
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisMCPServerUrl,
)
from agents.matmaster_agent.sub_agents.visualizer_agent.constant import (
    VisualizerServerUrl,
)
from agents.matmaster_agent.sub_agents.XRD_agent.constant import XRD_MCP_SERVER_URL

MCP_SERVER_URLS = [
    ABACUS_CALCULATOR_URL,
    ApexServerUrl,
    UNIELF_SERVER_URL,
    COMPDART_MCPServerUrl,
    ConvexHullServerUrl,
    DocumentParserServerUrl,
    DOE_SERVER_URL,
    DPAMCPServerUrl,
    Electron_Microscope_MCP_SERVER_URL,
    FinetuneDPAServerUrl,
    HEA_assistant_agent_ServerUrl,
    HEACALCULATOR_SERVER_URL,
    HEA_SERVER_URL,
    LAMMPS_URL,
    BOHRIUMPUBLIC_URL,
    MOFDB_URL,
    OPENLAM_URL,
    OPTIMADE_URL,
    NMR_MCP_SERVER_URL,
    ORGANIC_REACTION_SERVER_URL,
    PEROVSKITE_RESEARCH_URL,
    UNIMOL_SERVER_URL,
    Physical_Adsorption_MCP_SERVER_URL,
    PILOTEYE_SERVER_URL,
    POLYMER_SERVER_URL,
    SCIENCE_NAVIGATOR_MCP_SERVER_URL,
    SSE_SERVER_URL,
    STEEL_PREDICT_SERVER_URL,
    STEEL_SERVER_URL,
    StructureGenerateServerUrl,
    SuperconductorServerUrl,
    ThermoelectricServerUrl,
    TrajAnalysisMCPServerUrl,
    VisualizerServerUrl,
    XRD_MCP_SERVER_URL,
    TPD_MCP_SERVER_URL,
]

# ---- 颜色工具（ANSI），非 TTY 自动禁用 ----
USE_COLOR = sys.stdout.isatty()


def c(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(text: str) -> str:
    return c(text, '32')


def red(text: str) -> str:
    return c(text, '31')


def yellow(text: str) -> str:
    return c(text, '33')


def cyan(text: str) -> str:
    return c(text, '36')


def dim(text: str) -> str:
    return c(text, '2')


def bold(text: str) -> str:
    return c(text, '1')


async def check_one(url: str, timeout_s: float = 10.0) -> Tuple[str, bool, str]:
    try:
        async with asyncio.timeout(timeout_s):
            if 'sse' in url:
                async with sse_client(url) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        await session.list_tools()
            else:
                async with streamablehttp_client(url) as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        await session.list_tools()
        return url, True, 'Success'
    except BaseException as err:
        error_type, error_message = '', ''
        if isinstance(err, BaseExceptionGroup):
            exceptions: Optional[Iterable[BaseException]] = err.exceptions
        else:
            error_type = type(err).__name__
            error_message = str(err)
            exceptions = None

        if exceptions:
            for exc in exceptions:
                # 取最后一个/或你也可以 break 取第一个
                error_type = type(exc).__name__
                error_message = str(exc).split('\n')[0]
        return url, False, f"{error_type}: {error_message}"


async def main() -> int:
    tasks = [check_one(url) for url in MCP_SERVER_URLS]
    results = await asyncio.gather(*tasks)

    failed = []
    for url, ok, msg in results:
        if ok:
            status = green('OK')
            msg_s = dim(msg)
        else:
            status = red('FAIL')
            msg_s = yellow(msg)

        print(f"[{status}] {cyan(url)} -> {msg_s}")

        if not ok:
            failed.append((url, msg))

    if failed:
        print(
            bold(
                red(
                    f"\nSome MCP servers are unavailable. ({len(failed)}/{len(results)})"
                )
            )
        )
        return 1

    print(
        bold(green(f"\nAll MCP servers are available. ({len(results)}/{len(results)})"))
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
