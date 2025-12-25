def separate_card(msg):
    return f"""
<div style="
    background-color: #f0f8ff;
    border: 1px solid #d4e3fc;
    border-left: 4px solid #1890ff;
    border-radius: 4px;
    padding: 6px 10px;
    margin: 4px 0;
    font-family: sans-serif;
    color: #096dd9;
    line-height: 1.3;
    display: inline-block;
">
  <strong>{msg}</strong>
</div>
"""


def all_summary_card(i18n):
    return f"""
<div style="
    background-color: #f0f9eb;
    border: 1px solid #e1f3d8;
    border-left: 4px solid #67c23a;
    border-radius: 4px;
    padding: 6px 10px;
    margin: 4px 0;
    font-family: sans-serif;
    color: #529b2e;
    line-height: 1.3;
    display: inline-block;
">
  <strong>{i18n.t('PlanSummary')}</strong>
</div>
"""
