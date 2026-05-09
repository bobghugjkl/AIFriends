# 第38次提交：实现 Function Call

**提交哈希**：`8e678ea`  
**提交时间**：2026-03-05 20:41:17  
**提交者**：xuecan yan

---

## 一、什么是 Function Call

AI 大模型不仅仅是"打字机"，还能**主动调用 Python 函数**。比如用户问"现在几点了"，AI 不知道当前时间，但它可以调用 `get_time()` 获取真实时间，把结果融入回复。

**流程**：用户问 → AI 决定"我需要调函数" → AI 输出 tool_calls（JSON 格式，包含函数名和参数）→ 系统执行函数 → 结果传回 AI → AI 基于结果生成最终回复。

---

## 二、源码改动

**单文件**：`backend/web/views/friend/message/chat/graph.py`（31 行新增，2 行删除，4 行修改）

### import 新增

```diff
+from pprint import pprint
+from django.utils.timezone import localtime, now
+from langchain_core.tools import tool
+from langgraph.prebuilt import ToolNode
```

### 定义 `get_time` 工具

```python
        @tool
        def get_time() -> str:
            """当需要查询精确时间时，调用此函数。返回格式为：[年-月-日 时:分:秒]"""
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        tools = [get_time]
```

- `@tool` —— LangChain 装饰器。把普通 Python 函数变成 AI 可调用的"工具"。LangChain 根据函数签名和 **docstring** 生成 tool schema 发送给 AI。（什么是装饰器？Python中`@xxx`写在函数定义上方的语法，意思是"把这个函数传给xxx，用xxx的返回值替换原函数"。可以理解为给函数"穿了一件外套"——原来的函数功能不变，但在外面包了一层额外的能力。`@tool`这层外套做的事：读取函数名（`get_time`）、参数列表、docstring说明文字，打包成AI能理解的"工具描述"，当AI调用时自动把参数传给原函数并返回结果。你写`def get_time()`，`@tool`让它变成"AI能调用的get_time"）
- docstring `"""当需要查询精确时间时，调用此函数..."""` —— **这段文字决定 AI 什么时候用它**。AI 读到这段描述后，当用户问时间相关问题时就会自动调用
- `localtime(now())` —— `now()` 返回 UTC 时间，`localtime()` 转为上海时区本地时间
- `tools = [get_time]` —— 工具列表，后续可追加更多工具

### LLM 绑定工具

```diff
-        )
+        ).bind_tools(tools)
```

`.bind_tools()` 向 LLM 注册可用工具列表。LLM 每次回复前判断：需要调工具吗？需要 → 输出 `tool_calls`；不需要 → 直接回复文字。

### 条件路由函数

```python
        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"
```

- `last_message = state['messages'][-1]` —— 取 agent 刚生成的消息
- `last_message.tool_calls` —— AI 是否请求了函数调用
- `return "tools"` → 路由到 tools 节点
- `return "end"` → 路由到 END

### ToolNode + 新图结构

```python
        tool_node = ToolNode(tools)

        graph.add_node('tools', tool_node)

        graph.add_conditional_edges(
            'agent',
            should_continue,
            {'tools': 'tools', 'end': END}
        )
        graph.add_edge('tools', 'agent')
```

- `ToolNode(tools)` —— LangGraph 内置节点，接收 AI 的 tool_calls，执行对应函数，返回 `ToolMessage`（函数返回值）
- `add_conditional_edges('agent', should_continue, {...})` —— 从 agent 出发的条件边。`should_continue` 返回值决定下一步
- `add_edge('tools', 'agent')` —— tools 执行完**回到 agent**，AI 拿到函数结果后再次思考。这条边形成循环

### 调试代码

```diff
+            pprint(state)
```

在 `model_call` 中打印完整状态。后续提交删除。

---

## 三、改造后的 LangGraph 工作流

```
START → agent (llm.bind_tools.invoke)
           │
           ▼
     should_continue
           │
    ┌──────┴──────┐
    │              │
 tool_calls    无 tool_calls
    │              │
    ▼              ▼
  tools          END
 (ToolNode)
    │
    └──→ agent (循环：可连续调多个工具)
```

**实例**："现在几点了？"
1. agent → LLM 读到 `get_time` docstring → 输出 `tool_calls=[{name:"get_time", args:{}}]`
2. should_continue → return "tools"
3. tools → 执行 `get_time()` → 返回 `ToolMessage("2026-03-05 20:41:17")`
4. 回到 agent → LLM 收到函数结果 → 生成回复"现在是北京时间2026年3月5日晚上8点41分"
5. should_continue → `tool_calls` 为空 → return "end" → END
