# 第51次提交：添加语音复刻API

**提交哈希**：`19c307f`  
**提交时间**：2026-03-17 22:01:14  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

添加了**语音复刻（Voice Enrollment）**功能的工具函数——用户可以上传一段音频作为模板，创建自己的"定制音色"。这在阿里云百炼中叫 `voice-enrollment` 模型。

---

## 二、使用了什么技术

| 技术/工具 | 用途 |
|-----------|------|
| `requests` 库 | 向阿里云百炼 `voice-enrollment` API 发送 HTTP 请求 |
| `voice-enrollment` 模型 | 阿里云百炼的语音复刻/音色克隆模型 |
| `cosyvoice-v3-flash` | TTS 目标模型，复刻后的音色用于此模型合成 |
| `requests.post().json()` | 解析 API 返回的 JSON 响应 |

---

## 三、整体架构 / 数据流

```
Voice Enrollment Flow:

create_voice(voice_url, prefix)：
  用户上传 .wav 音频样本
       │
       ▼
  POST → 阿里云百炼 voice-enrollment API
    model: "voice-enrollment"
    action: "create_voice"
    target_model: "cosyvoice-v3-flash"   ← 复刻的音色将用于此 TTS 模型
    url: 音频样本地址
    prefix: 音色名前缀
       │
       ▼
  返回 voice_id ← AI 学习音频特征后生成的定制音色标识
       │
       ▼
  TTS 时使用此 voice_id → cosyvoice-v3-flash 以定制音色合成语音

list_voice()：
  请求 voice-enrollment API, action: "list_voice"
  page_size: 100
       │
       ▼
  返回所有已创建的自定义音色列表

delete_voice(voice_id)：
  请求 voice-enrollment API, action: "delete_voice"
  voice_id: 指定要删除的音色 ID
       │
       ▼
  删除该定制音色
```

---

## 四、新增文件：`create_voice.py` —— 创建自定义音色

**路径**：`backend/web/views/create/character/voice/custom/create_voice.py`

**完整源码：**

```python
import os

import requests


def create_voice(voice_url, prefix):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            "target_model": "cosyvoice-v3-flash",
            "prefix": prefix,
            "url": voice_url,
        }
    }
    response = requests.post(os.getenv('VOICE_URL'), headers=headers, json=data)
    return response.json()
```

**讲解：**
- `create_voice(voice_url, prefix)` —— 上传一段音频样本（`voice_url`），给音色起个前缀名（`prefix`）
- `model: "voice-enrollment"` —— 阿里云百炼的语音复刻模型
- `target_model: "cosyvoice-v3-flash"` —— 复刻后的音色将用于这个 TTS 模型
- `prefix` —— 音色名前缀，用户自定义
- `url` —— 音频样本的 URL 地址（一段 `.wav` 格式的录音）
- `response.json()` —— 返回 API 的 JSON 响应，包含 `voice_id`（定制音色标识）

---

## 五、新增文件：`delete_voice.py` —— 删除定制音色

**路径**：`backend/web/views/create/character/voice/custom/delete_voice.py`

**完整源码：**

```python
import os

import requests


def delete_voice(voice_id):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "delete_voice",
            "voice_id": voice_id,
        }
    }
    response = requests.post(os.getenv('VOICE_URL'), headers=headers, json=data)
    return response.json()
```

**讲解：**
- `delete_voice(voice_id)` —— 根据 `voice_id` 删除指定的定制音色
- 相同的 `headers` 和 `VOICE_URL` 端点，不同的 `action` 参数

---

## 六、新增文件：`list_voice.py` —— 列出所有定制音色

**路径**：`backend/web/views/create/character/voice/custom/list_voice.py`

**完整源码：**

```python
import os

import requests


def list_voice():
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "list_voice",
            "page_size": 100,
            "page_index": 0
        }
    }
    response = requests.post(os.getenv('VOICE_URL'), headers=headers, json=data)
    return response.json()
```

**讲解：**
- `list_voice()` —— 列出该账户下所有已创建的自定义音色
- `page_size: 100` —— 每页最多返回 100 条记录
- `page_index: 0` —— 从第 0 页开始（第一页）

---

## 七、总结

| 函数 | 文件 | 用途 |
|------|------|------|
| `create_voice(voice_url, prefix)` | `create_voice.py` | 上传音频样本，创建定制音色 |
| `delete_voice(voice_id)` | `delete_voice.py` | 删除指定 ID 的定制音色 |
| `list_voice()` | `list_voice.py` | 列出所有已创建的定制音色 |

三个函数都是对阿里云百炼 `voice-enrollment` API 的封装，提供了音色复刻的完整管理能力（创建、列表、删除）。目前只有后端工具函数，前端界面要对接时可直接调用。
