from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, field_validator


class JobStatus(str, Enum):
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'


class JobResultType(str, Enum):
    RegularFile = 'RegularFile'
    MatModelerFile = 'MatModelerFile'
    Value = 'Value'


class JobResult(BaseModel):
    name: str
    data: Union[int, float, str]
    url: Optional[str] = ''
    type: JobResultType


class BohrJobInfo(BaseModel):
    origin_job_id: str
    job_id: int
    job_detail_url: str
    job_status: JobStatus
    job_name: str
    job_result: Optional[List[JobResult]] = None
    job_in_ctx: bool = False

    @field_validator('job_detail_url')
    @classmethod
    def validate_job_detail_url(cls, v: str) -> str:
        if '.dp.tech/jobs/detail' not in v:
            raise ValueError(f"Job Detail Url Invalid")
        return v


class DFlowJobInfo(BaseModel):
    origin_job_id: str
    job_name: str
    job_status: JobStatus
    workflow_id: str
    workflow_uid: str
    workflow_url: str
    job_result: Optional[List[JobResult]] = None
    job_in_ctx: bool = False


class TransferCheck(BaseModel):
    is_transfer: bool
    target_agent: str


class UserContent(BaseModel):
    language: str
