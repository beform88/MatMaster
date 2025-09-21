from typing import List

from agents.matmaster_agent.constant import JOB_RESULT_KEY


def get_frontend_job_result_data(job_result: List[dict]):
    return {
        'eventType': 1,
        'eventData': {
            'contentType': 1,
            'renderType': '@bohrium-chat/matmodeler/dialog-file',
            'content': {
                JOB_RESULT_KEY: [
                    item for item in job_result if item.get('status', None) is None
                ]
            },
        },
    }
