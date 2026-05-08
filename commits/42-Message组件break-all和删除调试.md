# 第42次提交：Message组件添加break-all；删除调试信息

**提交哈希**：`670a272`  
**提交时间**：2026-03-05 21:43:20  
**提交者**：xuecan yan

---

## 一、Message 组件加 `break-all`

**文件**：`Message.vue`

```diff
-<div class="chat-bubble whitespace-pre-wrap">{{ message.content }}</div>
+<div class="chat-bubble whitespace-pre-wrap break-all">{{ message.content }}</div>
```

`break-all` 强制在任何字符处换行（包括长英文单词或 URL）。不加的话，一条超长无空格的英文文本（如 AI 输出的代码片段或 URL）会撑爆消息气泡，超出屏幕。

---

## 二、删除 `pprint` 调试代码

**文件**：`graph.py`

```diff
-from pprint import pprint
 pprint(state['messages'])     # 删除
```

在 `model_call` 中每次调用 LLM 都打印整个消息列表到服务器终端。调试期间有用，但会暴露用户聊天内容到服务器日志，且高并发时会刷屏。代码稳定后要删除。

---

## 三、.gitignore 多余空行清理

删了一个尾部的多余空行。
