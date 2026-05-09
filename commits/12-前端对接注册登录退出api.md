# 第12次提交：前端对接注册、登录、退出API

**提交哈希**：`53cf839`  
**提交时间**：2026-01-27 22:26:00  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

把前端的登录、注册、退出**从纯 UI 变成真正可用的功能**：引入 Axios 发 HTTP 请求、创建了自动处理 Token 刷新和认证的拦截器、表单绑定数据并实现提交逻辑。同时修复了后端登录接口的 bug。

---

## 二、使用了什么技术

| 技术/工具/库 | 用途 |
|-------------|------|
| Axios（create, interceptors, Promise） | HTTP 客户端，创建自定义实例，通过请求/响应拦截器自动处理 Token 注入、过期刷新和并发请求排队 |
| Pinia Store（useUserStore） | 在拦截器中读取/更新 accessToken，配合响应拦截器自动刷新 Token 后更新 Store |
| Vue v-model | 双向数据绑定，将登录/注册表单输入框的值与 JavaScript 响应式变量保持同步 |
| async/await | 异步处理 HTTP 请求，使登录、注册、退出流程代码像同步代码一样顺序可读 |
| FormData（构造函数） | 构造 multipart/form-data 格式请求体（后续用于文件上传） |
| router.push | 编程式导航，登录/注册成功后自动跳转到首页 |

## 三、整体架构 / 数据流

```
请求与 Token 刷新完整流程:

  前端请求                          后端
     │                                │
     │  api.post('/login/', data)      │
     ▼                                │
┌───────────────┐                     │
│ 请求拦截器      │                     │
│ (request)      │                     │
│ 检查 accessToken │                     │
│ 有 → 添加       │                     │
│ Authorization:  │                     │
│ Bearer xxx     │                     │
└───────┬───────┘                     │
        │ 带 Token 的请求              │
        ▼                             │
   ┌──────────┐                      │
   │  服务器   │                      │
   │  验证 JWT │                      │
   └──┬───────┘                      │
      │                               │
      ├─ Token 有效 ──→ 返回 200       │
      │                               │
      └─ Token 过期 ──→ 返回 401       │
                             │        │
                             ▼        │
                    ┌──────────────────────┐
                    │  响应拦截器 (response) │
                    │  检测 status === 401  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  isRefreshing 是否为 false? │
                    │  (防止并发刷新)        │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  发 refresh_token 请求 │
                    │  axios.post(         │
                    │  '/refresh_token/',  │
                    │  {}, {withCredentials}│
                    │  ) ← 用原始 axios 实例│
                    │  (避免死循环)          │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │ 成功            │                 │ 失败
              ▼                 │                 ▼
     ┌────────────────┐        │        ┌────────────────┐
     │ 更新 Store 中的  │        │        │ user.logout()  │
     │ accessToken    │        │        │ 清空用户状态     │
     │ onRefreshed()  │        │        │ onRefreshFailed│
     │ → 重试所有排队    │        │        │ → 所有排队请求失败│
     │   的原始请求     │        │        │                │
     └────────────────┘        │        └────────────────┘
                               │
                     并发 401 队列机制:

     ┌─────────────────────────────────────────┐
     │ 同时到达的 3 个请求都返回 401:             │
     │                                           │
     │  请求A ──→ 发现 401 ──→ 触发刷新 (isRefreshing=true) │
     │  请求B ──→ 发现 401 ──→ subscribeTokenRefresh(cb)  │
     │  请求C ──→ 发现 401 ──→ subscribeTokenRefresh(cb)  │
     │                                           │
     │  刷新成功后: onRefreshed(token)           │
     │  → 执行排队回调 → 请求B和C用新 Token 重试    │
     └─────────────────────────────────────────┘
```

---

## 四、后端修 bug

**文件**：`backend/web/views/user/account/login.py`

```diff
-                user_profile = UserProfile.objects.get(username=username)
+                user_profile = UserProfile.objects.get(user=user)
```

这就是我在第 10 次提交中指出的 bug。`UserProfile` 表没有 `username` 字段（它在关联的 `User` 表里），应该用 `user=user` 通过外键查询。

---

## 五、引入 Axios——`package.json`

```diff
+    "axios": "^1.13.2",
```

**Axios 是什么**：一个基于 Promise 的 HTTP 客户端库。虽然浏览器有内置的 `fetch()`，但 Axios 提供了更强大的功能：
- **拦截器**（Interceptors）——在请求发出前/响应返回后自动执行逻辑
- **自动 JSON 解析**——不用手动 `response.json()`
- **请求/响应超时**——内置 timeout 机制
- **取消请求**——可以中途取消正在进行的请求

---

## 六、核心文件：`frontend/src/js/http/api.js`——HTTP 拦截器

这是本次提交最重要的文件，共 92 行。它创建了一个经过封装的 Axios 实例，自动处理 Token 注入和过期刷新。

### 4.1 创建实例

```javascript
import axios from "axios"
import {useUserStore} from "@/stores/user.js";

const BASE_URL = 'http://127.0.0.1:8000'

const api = axios.create({
    baseURL: BASE_URL,
    withCredentials: true,
})
```

**逐行讲解**：

- `import axios from "axios"` —— 导入 Axios 库
- `import {useUserStore} from "@/stores/user.js"` —— 导入用户 Store 来读取/设置 Token
- `BASE_URL = 'http://127.0.0.1:8000'` —— 后端地址。后续写路径时可以省略前缀，如直接用 `/api/xxx`，Axios 会自动拼接
- `axios.create({...})` —— 创建一个**自定义的 Axios 实例**。不直接用 `axios`（全局单例），而是创建一个独立的实例，方便配置
- `withCredentials: true` —— 关键配置。让 Axios 在**跨域请求**中自动携带 Cookie。因为 Refresh Token 存在 HttpOnly Cookie 里，必须设置这个，否则浏览器不会附带 Cookie

### 4.2 请求拦截器——自动添加 Bearer Token

```javascript
api.interceptors.request.use(config => {
    const user = useUserStore()
    if (user.accessToken) {
        config.headers.Authorization = `Bearer ${user.accessToken}`
    }
    return config
})
```

**讲解**：

- `api.interceptors.request.use(callback)` —— **请求拦截器**。每一个通过 `api` 发出的 HTTP 请求，在真正发出前都会先经过这个回调函数。（什么是"拦截器"？就像机场安检——每个旅客（请求）在登机（发往服务器）之前都要过安检门（拦截器），安检员检查你的登机牌、帮你贴标签。响应拦截器则是出机场时的海关——旅客回来也要过一遍检查。Axios的拦截器就是让你在所有请求发出前/所有响应回来后，自动执行一段自定义逻辑，不用在每个请求里重复写"检查token、附加token"这些代码。打个比方：拦截器就像流水线上的自动贴标机——产品（请求）经过时自动贴上标签（Authorization头），工人（业务代码）不用管贴标的事，只管把产品放上传送带就行）
- `config` —— 请求配置对象，包含 URL、method、headers 等
- `const user = useUserStore()` —— 在拦截器中调用 Pinia Store。Pinia 内部已经初始化过，可以随时调用
- `if (user.accessToken)` —— 如果有 Token，就附加到请求头。Bearer 是 JWT 认证的标准前缀，后端 `simplejwt` 的 `AUTH_HEADER_TYPES = ('Bearer',)` 期望的就是这个格式
- `return config` —— 必须返回 config（可能是修改后的），否则请求被中止

**效果**：开发者只需写 `api.post('/login/', data)`，拦截器自动把当前有效的 Access Token 附加到 Authorization 头里。

### 4.3 Token 刷新机制（响应拦截器）

这是最复杂的部分——当 Access Token 过期（后端返回 401）时，自动用 Refresh Token 换新的，然后重试原请求。

#### 缓存变量

```javascript
let isRefreshing = false
let refreshSubscribers = []
```

- `isRefreshing` —— 标志位。同时只能有一个刷新请求在飞行中，防止多个 401 响应同时触发多个刷新
- `refreshSubscribers` —— **回调队列**。当刷新正在进行时，其他遇到 401 的请求不直接重试，而是把重试逻辑注册为回调，等刷新完成后统一执行

**为什么要用队列**：假设用户打开一个页面，同时发起了 3 个 API 请求。Access Token 刚好在这时过期，后端给 3 个请求都返回了 401。不用队列的话，3 个 401 会触发 3 次 Token 刷新——浪费资源，且第二次刷新可能因为第一次已经刷新过而失败。用队列后：第一个 401 触发刷新，后面两个 401 的回调排队等待，刷新成功后三个请求一起重试。

#### 回调管理函数

```javascript
function subscribeTokenRefresh(callback) {
    refreshSubscribers.push(callback)
}

function onRefreshed(token) {
    refreshSubscribers.forEach(cb => cb(token))
    refreshSubscribers = []
}

function onRefreshFailed(err) {
    refreshSubscribers.forEach(cb => cb(null, err))
    refreshSubscribers = []
}
```

- `subscribeTokenRefresh(callback)` —— 把回调函数放入队列
- `onRefreshed(token)` —— 刷新成功后，依次执行所有回调，传入新 Token。然后清空队列
- `onRefreshFailed(err)` —— 刷新失败后，依次执行所有回调传入错误。然后清空队列。所有等待的请求都会因为 Token 刷新失败而一起失败

#### 响应拦截器主体

```javascript
api.interceptors.response.use(
    response => response,
    async error => {
        const user = useUserStore()
        const originalRequest = error?.config
        if (!originalRequest) {
            return Promise.reject(error)
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            return new Promise((resolve, reject) => {
                subscribeTokenRefresh((token, error) => {
                    if (error) {
                        reject(error)
                    } else {
                        originalRequest.headers.Authorization = `Bearer ${token}`
                        resolve(api(originalRequest))
                    }
                })

                if (!isRefreshing) {
                    isRefreshing = true
                    axios.post(
                        `${BASE_URL}/api/user/account/refresh_token/`,
                        {},
                        {withCredentials: true, timeout: 5000}
                    ).then(res => {
                        user.setAccessToken(res.data.access)
                        onRefreshed(res.data.access)
                    }).catch(error => {
                        user.logout()
                        onRefreshFailed(error)
                        reject(error)
                    }).finally(() => {
                        isRefreshing = false
                    })
                }
            })
        }

        return Promise.reject(error)
    }
)
```

**逐段讲解**：

- `api.interceptors.response.use(response => response, async error => {...})` —— **响应拦截器**。第一个参数是成功回调（直接返回 response），第二个参数是错误回调

- `const originalRequest = error?.config` —— `?.` 是**可选链操作符**。如果 `error` 是 `null` 或 `undefined`，不会报错而是返回 `undefined`。从 error 中取出原始请求配置

- `if (!originalRequest) return Promise.reject(error)` —— 没有原始请求（比如网络断开导致的错误），直接抛出

- `if (error.response?.status === 401 && !originalRequest._retry)` —— 核心判断：
  - `error.response?.status === 401` —— 后端返回 401（未授权），说明 Access Token 过期
  - `!originalRequest._retry` —— `_retry` 是我们自定义的标志位，防止无限重试（如果刷新后的新 Token 发出去又 401，不再重试，直接失败）

- `return new Promise((resolve, reject) => {...})` —— **把异步刷新包装成一个 Promise 返回**。这是关键技巧——Axios 的拦截器期望返回 Promise，这样调用 `api.post()` 的代码就不用额外处理重试逻辑。（什么是Promise？JavaScript中处理异步操作的核心机制。简单说，Promise就是一个"承诺"——"我现在还不知道结果，但我承诺未来一定会给你一个答复"。比如你打电话订外卖就是异步的：你打电话下单（发起请求），餐厅说"好的，我们承诺30分钟后送到"，你挂了电话继续看电视（代码继续执行），30分钟后外卖到了（Promise完成），你开门取餐（处理结果）。你不需要一直举着电话等30分钟。在代码里，`new Promise((resolve, reject) => {...})`创建了一个承诺——内部操作成功时调用`resolve(结果)`通知外面"搞定了"，失败时调用`reject(错误)`通知外面"出问题了"。`.then(res => ...)`就是"等承诺兑现后做什么"，`.catch(err => ...)`就是"等承诺失败后做什么"）

- 回调内部 `resolve(api(originalRequest))` —— 用新 Token 重新执行原始请求，成功后 resolve 给原始调用者

- `axios.post('.../refresh_token/', {}, {withCredentials: true, timeout: 5000})` —— 用**原始的全局 `axios`**（不是 `api` 实例）发刷新请求。如果用 `api` 实例，刷新请求也会经过同一个拦截器——如果它又触发 401，就会死循环
  - `{}` —— 空的请求体（Refresh Token 从 Cookie 读取，不需要传参数）
  - `timeout: 5000` —— 5 秒超时，防止请求卡住

- `.then(res => {...})` —— 刷新成功后，更新 Store 中的 Token，调用 `onRefreshed` 通知所有排队的请求

- `.catch(error => {...})` —— 刷新失败（Refresh Token 也过期了），调用 `user.logout()` 清空用户状态，通知所有排队请求失败

- `.finally(() => { isRefreshing = false })` —— 不管成功失败，重置标志位

- 最后的 `return Promise.reject(error)` —— 非 401 错误（如 404、500）直接传给调用者处理

---

## 七、Store 初始值改为空

**文件**：`stores/user.js`

```diff
-    const id = ref(1)
-    const username = ref('yxc')
-    const photo = ref('http://127.0.0.1:8000/media/user/photos/default.png')
-    const profile = ref('111')
-    const accessToken = ref('111')
+    const id = ref(0)
+    const username = ref('')
+    const photo = ref('')
+    const profile = ref('')
+    const accessToken = ref('')
```

之前的值是硬编码的假数据（用于在对接 API 前跑通 UI）。现在 API 已经就绪，初始值改为空——用户没登录时，Store 的状态就是"空"。

---

## 八、登录页——`LoginIndex.vue`

**新增 Script**：

```javascript
const username = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  if (!username.value.trim()) {
    errorMessage.value = '用户名不能为空'
  } else if (!password.value.trim()) {
    errorMessage.value = '密码不能为空'
  } else {
    try {
      const res = await api.post('/api/user/account/login/', {
        username: username.value,
        password: password.value,
      })
      const data = res.data
      if (data.result === 'success') {
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        await router.push({ name: 'homepage-index' })
      } else {
        errorMessage.value = data.result
      }
    } catch (err) {
      console.log(err)
    }
  }
}
```

**逐行讲解**：

- `const username = ref('')` —— 定义响应式变量，和输入框绑定
- `username.value.trim()` —— `trim()` 去掉首尾空白字符。`"  "` → `""`
- `async function handleLogin()` —— `async` 表示函数内部可以用 `await` 等待异步操作。（什么是async/await？这是Promise的"语法糖"——让异步代码读起来像同步代码一样流畅。没有async/await时，你要写`api.post(...).then(res => { ... }).catch(err => { ... })`这种链式调用，嵌套多了很难读。有了async/await，你写`const res = await api.post(...)`——看起来就像普通赋值语句，但`await`的实际意思是"暂停这个函数的执行，等Promise出结果了再继续往下走"。函数外的代码不受影响，继续运行。`async`标志告诉JavaScript"这个函数里有await，请按异步模式处理我"。注意：`await`只能在`async`函数内部使用，普通函数里写`await`会报语法错误）
- `await api.post('/api/user/account/login/', {username: ..., password: ...})` —— 发 POST 请求。`api` 是我们封装的 Axios 实例，自动走拦截器；第二个参数是请求体（JSON 格式）
- `user.setAccessToken(data.access)` —— 把 Access Token 存到 Store
- `user.setUserInfo(data)` —— 把用户信息存到 Store
- `await router.push({name: 'homepage-index'})` —— 登录成功后跳转到首页。`router.push` 是编程式导航，在 JavaScript 逻辑中跳转页面。`await` 等待导航完成

**新增 Template**：

```html
<form @submit.prevent="handleLogin" class="fieldset ...">
  <input v-model="username" type="text" class="input" placeholder="用户名" />
  <input v-model="password" type="password" class="input" placeholder="密码" />
  <p v-if="errorMessage" class="text-sm text-red-500 mt-1">{{ errorMessage }}</p>
  <button class="btn btn-neutral mt-4">登录</button>
</form>
```

- `@submit.prevent="handleLogin"` —— 监听表单的 submit 事件。`.prevent` 是 Vue 的**事件修饰符**，调用 `event.preventDefault()` 阻止表单的默认提交行为（浏览器默认会刷新页面）。这样表单提交完全由 `handleLogin` 函数控制
- `v-model="username"` —— Vue 的**双向数据绑定**。输入框的值和 JavaScript 变量 `username` 保持同步：用户输入 → 变量自动更新；变量变化 → 输入框自动更新
- `<p v-if="errorMessage">` —— 有错误信息时才显示红色提示条
- `<fieldset>` → `<form>` —— 语义化 HTML。`<form>` 正确表达了"这是一个表单"的语义，同时支持按 Enter 键提交、浏览器自动填充等表单特性

---

## 九、注册页——`RegisterIndex.vue`

与登录页几乎一样，多了：
- `const passwordConfirmed = ref('')` —— 确认密码变量
- `if (password.value.trim() !== passwordConfirmed.value.trim())` —— 两次密码不一致验证
- 注册请求 URL 改为 `'/api/user/account/register/'`

---

## 十、退出登录——`UserMenu.vue`

```javascript
async function handleLogout() {
  try {
    const res = await api.post('/api/user/account/logout/')
    if (res.data.result === 'success') {
      user.logout()
      await router.push({ name: 'homepage-index' })
    }
  } catch (err) {
    console.log(err)
  }
}
```

退出流程：发 POST 到后端 → 后端删除 Refresh Token Cookie → 前端清空 Store 中用户数据 → 跳转到首页。

---

## 十一、总结

| 新增/修改 | 作用 |
|-----------|------|
| `api.js`（新） | Axios 实例 + 拦截器，自动附加 Token、自动刷新过期 Token、并发请求排队 |
| `LoginIndex.vue`（改） | 用 `v-model` 绑定表单 + `async/await` 发登录请求 |
| `RegisterIndex.vue`（改） | 同上，增加确认密码验证 |
| `UserMenu.vue`（改） | 退出按钮对接后端 API |
| `user.js`（改） | 清空硬编码数据，改为空初始值 |
| `login.py`（改） | 修复 `UserProfile.objects.get()` 的查询条件bug |

**这个 `api.js` 文件是整个前端的 HTTP 通信基石**。后续所有与后端的通信都通过这个 `api` 实例进行，Token 管理和自动刷新对业务代码完全透明。
