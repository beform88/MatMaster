import requests

from agents.matmaster_agent.model import JobStatus, BohrJobInfo


def mapping_status(status):
    return {
        -1: "Failed",
        0: "Pending",
        1: "Running",
        2: "Finished",
        3: "Scheduling",
        4: "Stopping",
        5: "Stopped",
        6: "Terminating",
        7: "Killing",
        8: "Uploading",
        9: "Wait"
    }.get(status, "Unknown")


def get_job_status(job_query_url, access_key):
    response = requests.request("GET", job_query_url, headers={"accessKey": access_key})
    return mapping_status(response.json()['data']["status"])


def has_job_running(jobs_dict: BohrJobInfo) -> bool:
    """检查是否有任何作业处于运行状态"""
    return any(job['job_status'] == JobStatus.Running for job in jobs_dict.values())


def get_running_jobs_detail(jobs_dict: BohrJobInfo):
    return [(job["origin_job_id"], job["job_id"], job["job_query_url"], job["agent_name"]) for job in jobs_dict.values()
            if job['job_status'] == JobStatus.Running]
