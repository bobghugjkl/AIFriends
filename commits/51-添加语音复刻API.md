# 第51次提交：添加语音复刻API

**提交哈希**：`19c307f`  
**提交时间**：2026-03-17 22:01:14  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

添加了**语音复刻（Voice Enrollment）**功能的工具函数——用户可以上传一段音频作为模板，创建自己的"定制音色"。这在阿里云百炼中叫 `voice-enrollment` 模型。

---

## 二、三个工具函数

**文件**：`backend/web/views/create/character/voice/custom/`（新建包）

### `create_voice`——创建自定义音色

```python
def create_voice(voice_url, prefix):
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            "target_model": "cosyvoice-v3-flash",
            "prefix": prefix,           # 音色名前缀
            "url": voice_url,           # 音频样本URL（一段.wav）
        }
    }
    response = requests.post(os.getenv('VOICE_URL'), headers=headers, json=data)
    return response.json()
```

上传一段音频（`voice_url`），给音色起个前缀名，AI 学习后返回一个 `voice_id`——之后 TTS 就能用这个定制音色说话了。

### `list_voice`——列出所有定制音色

```python
data = {
    "model": "voice-enrollment",
    "input": {
        "action": "list_voice",
        "page_size": 100,
    }
}
```

### `delete_voice`——删除定制音色

```python
data = {
    "model": "voice-enrollment",
    "input": {
        "action": "delete_voice",
        "voice_id": voice_id,
    }
}
```

---

## 三、配置切到云端

```javascript
// config.js
-const platform = 'vue'
+const platform = 'cloud'
```

准备部署到 `app7492.acapp.acwing.com.cn`。

---

## 四、总结

三个函数都是对阿里云百炼 `voice-enrollment` API 的封装，提供了音色复刻的完整管理能力（创建、列表、删除）。目前只有后端工具函数，前端界面要对接时可直接调用。
