# 第38次提交：实现 Function Call

**提交哈希**：`8e678ea`  
**提交时间**：2026-03-05 20:41:17  
**提交者**：xuecan yan

---

## 一、什么是 Function Call

AI 大模型不仅仅是"打字机"，还能**主动调用函数**。比如用户问"现在几点了"，AI 不知道当前时间（它的训练数据是去年的），但它可以调用一个 `get_time()` 函数获取真实时间，然后把结果融入回复中。

**流程**：用户问 → AI 决定"我需要调用函数" → AI 返回函数调用请求（不是回复文字）→ 系统执行函数 → 把结果传回 AI → AI 基于结果生成最终回复。

---

## 二、代码改动

**文件**：`backend/web/views/friend/message/chat/graph.py`

### 2.1 定义工具函数

```python
@tool
def get_time() -> str:
    """当需要查询精确时间时，调用此函数。返回格式为：[年-月-日 时:分:秒]"""
    return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

tools = [get_time]
```

- `@tool` —— LangChain 的装饰器，把普通 Python 函数变成 AI 可调用的"工具"
- **docstring 是关键**：`"""当需要查询精确时间时，调用此函数..."""` —— 这段描述会发送给 AI，告诉它"什么时候该用这个工具"。AI 根据 docstring 决定是否调用
- `tools = [get_time]` —— 工具列表。目前只有"查时间"，后续可以加更多（搜索知识库、计算器等）

### 2.2 绑定工具到 LLM

```python
llm = ChatOpenAI(...).bind_tools(tools)
```

`.bind_tools()` 告诉 LLM"你有这些工具可用"。AI 在每次回复前会判断：是否需要调工具？需要的话输出 tool_calls 而不是文字。

### 2.3 条件路由

```python
def should_continue(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "tools"    # AI想调工具 → 跳到工具节点
    return "end"          # AI直接回复了 → 结束

tool_node = ToolNode(tools)

graph.add_conditional_edges(
    'agent',
    should_continue,
    {'tools': 'tools', 'end': END}
)
graph.add_edge('tools', 'agent')  # 工具执行完 → 回到agent继续思考
```

**LangGraph 工作流（改造后）**：

```
START → agent (调用LLM)
          │
          ├── AI 想调工具？ → tools (执行函数) → agent (基于结果再思考)
          │                                              │
          │                                        AI 直接回复 → END
          │
          └── AI 直接回复 → END
```

`tools → agent` 这条边形成了**循环**——AI 调一次工具后可以再决定是否调更多工具。比如用户同时问了时间和天气，AI 能连续调用多个函数。

---

## 三、例子

用户："现在几点了？"

1. `agent` 节点调用 LLM → AI 看到 `get_time` 工具的 docstring → 决定调用工具
2. `should_continue` 检测到 `tool_calls` → 返回 `"tools"`
3. `tool_node` 执行 `get_time()` → 返回 `"2026-03-05 20:41:17"`
4. 回到 `agent` → LLM 收到函数返回值 → 生成回复 "现在是北京时间 2026 年 3 月 5 日晚上 8 点 41 分"
5. `should_continue` 发现没有 tool_calls → 返回 `"end"`

---

## 四、总结

| 概念 | 作用 |
|------|------|
| `@tool` | 把 Python 函数设为 AI 可调用的工具 |
| `.bind_tools()` | 向 LLM 注册工具列表 |
| `should_continue` | LangGraph 条件路由——AI 要调工具还是直接结束 |
| `ToolNode` | LangGraph 内置节点——执行工具并把结果格式化 |
| `tools → agent` 循环 | 支持多轮工具调用 |
