# 第31次提交：修复上节课的bug

**提交哈希**：`5733448`  
**提交时间**：2026-03-03 20:09:05  
**提交者**：xuecan yan

---

## 一、修复：个人空间切换用户不刷新

**文件**：`SpaceIndex.vue`

**问题**：用户在个人空间 `/user/space/1/` → 点击别的角色的作者 → 跳转到 `/user/space/2/`。URL 变了，但组件没有重新加载数据——页面还显示用户 1 的信息和角色。这是因为 Vue Router 复用了同一个组件，`onMounted` 不会重新执行。

**修复**：

```javascript
watch(() => route.params.user_id, () => {
  reset()
})

function reset() {
  userProfile.value = null
  characters.value = []
  isLoading.value = false
  hasCharacters.value = true
  loadMore()
}
```

监听 `route.params.user_id` 变化 → 清空所有状态 → 重新加载。`userProfile` 要先设为 `null`，让 `UserInfoField` 的 `v-if` 隐藏旧信息，防止"闪烁旧数据"。


## 二、使用了什么技术

| 技术 | 用途 |
|------|------|
| Vue `watch` on `route.params` | 监听路由参数变化，检测用户切换 |
| 响应式状态重置模式 | 清空所有状态数据后重新加载，避免显示旧数据 |

## 三、整体架构 / 数据流

```
URL change (/user/space/1 → /user/space/2)
       │
       ▼
Vue Router reuses same component (onMounted won't re-run)
       │
       ▼
watch(route.params.user_id) fires
       │
       ▼
reset()
       │
       ├── userProfile = null         ← hides old user info via v-if
       ├── characters = []
       ├── isLoading = false
       ├── hasCharacters = true
       └── loadMore()                 ← fetch data for new user
       │
       ▼
Component displays fresh data for user 2
```

---

## 四、Rollup 版本升级

`package-lock.json` 中 Rollup 从 4.56.0 → 4.59.0。这是 Vite 的底层打包工具的版本更新，不影响代码。
