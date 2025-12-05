def plan_ask_confirm_card():
    return """
<div style="
  background-color: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-left: 4px solid #0066cc;
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0;
  font-family: sans-serif;
  color: #004085;
  line-height: 1.4;
">
  <strong>请确认是否执行上述计划？</strong>
</div>
"""


def step_card(index):
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
  <strong>步骤 {index}</strong>
</div>
"""


def all_summary_card():
    return """
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
  <strong>计划汇总概要</strong>
</div>
"""
