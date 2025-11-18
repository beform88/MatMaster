from enum import Enum


class PlanStepStatusEnum(str, Enum):
    PLAN = 'plan'
    PROCESS = 'process'
    SUBMITTED = 'submitted'
    SUCCESS = 'success'
    FAILED = 'failed'
