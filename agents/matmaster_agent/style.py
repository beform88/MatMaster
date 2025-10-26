from toolsy.i8n import I18N


def get_job_complete_card(i18n: I18N, job_id):
    return f"""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    color: white;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <div style="
            background: rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            font-size: 12px;
            font-weight: bold;
        ">🚀 {i18n.t("JobStatus")}</div>
        <div style="
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
        ">{i18n.t("Job")}ID：{job_id}</div>
    </div>
    <div style="
        font-size: 16px;
        font-weight: 500;
        margin-top: 8px;
    ">✅ {i18n.t("JobCompleted")}</div>
    <div style="
        font-size: 14px;
        opacity: 0.9;
        margin-top: 6px;
    ">{i18n.t("ResultRetrieving")}...</div>
</div>
"""


def photon_consume_free_card():
    return """
<div style="
    background: linear-gradient(135deg, #d1ecf1, #bee5eb);
    border: 1.5px solid #17a2b8;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 12px 0;
    box-shadow: 0 3px 8px rgba(23, 162, 184, 0.25);
    text-align: left;
">

<p style="
    font-size: 15px;
    color: #0c5460;
    margin: 0;
    font-weight: bold;
    line-height: 1.3;
    display: flex;
    align-items: center;
    gap: 6px;
">
🎁 限时免费
</p>

</div>
"""


def photon_consume_notify_card(cost):
    return f"""
<div style="
    background: linear-gradient(135deg, #fff3cd, #ffeaa7);
    border: 1.5px solid #ffc107;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 12px 0;
    box-shadow: 0 3px 8px rgba(255, 193, 7, 0.25);
    text-align: left;
">

<p style="
    font-size: 15px;
    color: #856404;
    margin: 0;
    font-weight: bold;
    line-height: 1.3;
    display: flex;
    align-items: center;
    gap: 6px;
">
⚠️ 即将扣除 <span style="color: #e74c3c; font-size: 18px; font-weight: 800;">{cost}</span> 光子
</p>

</div>
"""


def photon_consume_success_card(cost):
    return f"""
<div style="
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border: 1.5px solid #28a745;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 12px 0;
    box-shadow: 0 3px 8px rgba(40, 167, 69, 0.25);
    text-align: left;
">

<p style="
    font-size: 15px;
    color: #155724;
    margin: 0;
    font-weight: bold;
    line-height: 1.3;
    display: flex;
    align-items: center;
    gap: 6px;
">
✅ 扣除成功 <span style="color: #27ae60; font-size: 18px; font-weight: 800;">{cost}</span> 光子
</p>

</div>
"""


def hallucination_card(i18n: I18N):
    def _inner_css():
        return """
    <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        @keyframes progress {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(250%); }
        }
    </style>
</div>
"""

    return (
        f"""
<div style="
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    max-width: 500px;
    width: 100%;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin: 20px auto;
">
    <div style="
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
    ">
        <div style="
            font-size: 28px;
            margin-right: 16px;
            animation: pulse 2s infinite;
        ">🔄</div>
        <div style="flex: 1;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 4px;
            ">{i18n.t("JobSubmitHallucination")}</div>
            <div style="
                font-size: 14px;
                opacity: 0.9;
            ">{i18n.t("JobSubmitHallucinationAction")}</div>
        </div>
    </div>
    <div style="
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 2px;
        margin-top: 16px;
        overflow: hidden;
    ">
        <div style="
            height: 100%;
            width: 60%;
            background: white;
            border-radius: 2px;
            animation: progress 2s ease-in-out infinite;
        "></div>
    </div>"""
        + _inner_css()
    )


def tool_hallucination_card(i18n: I18N):
    def _inner_css():
        return """
<style>
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    @keyframes progress {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(200%); }
    }
</style>
    """

    return (
        f"""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    width: 100%;
    text-align: center;
    box-sizing: border-box;
">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <div style="font-size: 16px; animation: pulse 1.5s infinite;">🔧</div>
        <div style="flex: 1; text-align: left;">
            <div style="font-size: 13px; font-weight: 600;">{i18n.t("ToolInvocateHallucinationAction")}</div>
        </div>
    </div>
    <div style="
        height: 1.5px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 1px;
        margin-top: 6px;
        overflow: hidden;
    ">
        <div style="
            height: 100%;
            width: 25%;
            background: white;
            animation: progress 1.2s ease-in-out infinite;
        "></div>
    </div>
</div>
"""
        + _inner_css()
    )


def tool_retry_failed_card(i18n: I18N):
    def _inner_css():
        return """
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-2px); }
    }
    </style>
        """

    return (
        f"""
    <div style="
    background: linear-gradient(135deg, #ffa502 0%, #ff7f50 100%);
    color: white;
    padding: 10px 18px;
    border-radius: 6px;
    box-shadow: 0 3px 10px rgba(255, 165, 2, 0.2);
    width: 100%;
    text-align: center;
    box-sizing: border-box;
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="font-size: 16px; animation: bounce 2s infinite;">🔄</div>
        <div style="flex: 1; text-align: left;">
            <div style="font-size: 13px; font-weight: 600;">{i18n.t('ToolInvocateHallucination')}</div>
            <div style="font-size: 11px; opacity: 0.9;">{i18n.t('ToolInvocateHallucinationRetryFailed')}</div>
        </div>
    </div>
</div>
    """
        + _inner_css()
    )


def tool_response_failed_card(i18n: I18N):
    return f"""
<div style="
    background: #dc3545;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    width: 100%;
    text-align: center;
    box-sizing: border-box;
">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="font-size: 14px;">⚡</div>
        <div style="flex: 1; text-align: left;">
            <div style="font-size: 13px; font-weight: 600;">{i18n.t('ToolResponseFailed')}</div>
        </div>
    </div>
</div>
"""
