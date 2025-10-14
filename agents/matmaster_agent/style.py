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


def photon_consume_success(cost):
    return f"""
<div style="
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border: 2px solid #28a745;
    border-radius: 12px;
    padding: 15px 20px;
    margin: 15px 0;
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    text-align: left;
">

<p style="
    font-size: 16px;
    color: #155724;
    margin: 0;
    font-weight: bold;
    line-height: 1.4;
    display: flex;
    align-items: center;
    gap: 8px;
">
✅ 扣除成功 <span style="color: #27ae60; font-size: 22px; font-weight: 800;">{cost}</span> 光子
</p>

</div>
"""
