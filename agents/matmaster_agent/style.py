from toolsy.i8n import I18N


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
    <!-- 信息提示图标 -->
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
        <path d="M12 16H12.01M12 8V12M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
              stroke="#856404" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    即将扣除 <span style="color: #e74c3c; font-size: 18px; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">{cost}</span> 光子
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
    background: #ff6b6b;
    color: white;
    padding: 10px 18px;
    border-radius: 6px;
    box-shadow: 0 3px 10px rgba(255, 107, 107, 0.3);
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
</div>"""
        + _inner_css()
    )


def tool_response_failed_card(i18n: I18N):
    return f"""
<div style="
    background: linear-gradient(135deg, #f1aeb5, #ea868f);
    border: 1.5px solid #e6858f;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 12px 0;
    box-shadow: 0 3px 8px rgba(241, 174, 181, 0.35);
    text-align: left;
">
    <p style="
        font-size: 15px;
        color: #721c24;
        margin: 0;
        font-weight: bold;
        line-height: 1.3;
        display: flex;
        align-items: center;
        gap: 6px;
    ">
        ⚡ {i18n.t('ToolResponseFailed')}
    </p>
</div>
"""


def no_found_structure_card(i18n: I18N):
    return f"""
<div style="
    background: linear-gradient(135deg, #fff3cd, #ffeaa7);
    border: 1.5px solid #ffc107;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 12px 0;
    box-shadow: 0 3px 8px rgba(255, 193, 7, 0.2);
    text-align: left;
    border-left: 4px solid #ff9800;
">
    <div style="
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    ">
        <span style="
            font-size: 18px;
            color: #ff9800;
        ">
            ⚠
        </span>
        <p style="
            font-size: 16px;
            color: #856404;
            margin: 0;
            font-weight: bold;
            line-height: 1.3;
        ">
            {i18n.t('NoFoundStructure')}
        </p>
    </div>
</div>
"""
