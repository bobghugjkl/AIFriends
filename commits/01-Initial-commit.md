# 第1次提交：Initial commit（项目初始化）

**提交哈希**：`bec716f`  
**提交时间**：2026-01-22 21:23:35  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

这是整个项目的**第一次提交**，搭建了项目的骨架。项目是一个"双端"项目——**backend（后端）**用 Django（Python Web 框架），**frontend（前端）**用 Vue 3（JavaScript 前端框架）+ Vite（打包工具）。两个端放在同一个文件夹里，通过 Vite 打包后输出到 Django 的静态文件目录，由 Django 统一提供服务。

---

## 二、使用了什么技术

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 后端框架 | Django | 6.0.1 | Python Web 框架，处理 HTTP 请求、ORM、模板渲染 |
| API 框架 | Django REST Framework (DRF) | — | 构建 RESTful API，序列化、认证、权限 |
| 认证 | djangorestframework-simplejwt | — | JWT 令牌认证（Access Token + Refresh Token） |
| 跨域 | django-cors-headers | — | 允许前端 localhost:5173 跨域请求后端 localhost:8000 |
| 数据库 | SQLite3 | — | 文件型数据库，零配置，适合开发和小项目 |
| 前端框架 | Vue 3 | 3.5.26 | 渐进式 JavaScript 框架，组件化开发 |
| 前端路由 | Vue Router | 4.6.4 | SPA 页面路由，History 模式（SPA是什么？简单说就是"单页应用"——整个网站只有一个HTML页面，点击链接时浏览器不刷新，而是用JavaScript偷偷换掉页面内容，体验像手机App一样流畅） |
| 状态管理 | Pinia | 3.0.4 | Vue 3 官方状态管理库 |
| 构建工具 | Vite | 7.3.0 | 极速开发服务器 + 生产打包 |
| 图标 | SVG 内联 | — | 各个 icon 用纯 SVG 写在 .vue 组件中 |

---

## 三、整体架构

### 3.1 前后端协作方式

```
开发阶段：
  浏览器 (localhost:5173) ──→ Vite Dev Server ──→ 代理 API 请求 ──→ Django (localhost:8000)
  
生产阶段：
  浏览器 ──→ Django (localhost:8000)
                ├── /api/*  → DRF 处理 JSON 响应
                ├── /admin/ → Django Admin 后台
                └── /*      → 返回 index.html → Vue 接管 → SPA 路由
```

### 3.2 Django 内部请求处理流程

```
浏览器请求
    │
    ▼
urls.py (根路由) ─── 匹配 URL ───┬── /admin/  → Django Admin
                                 ├── /api/*   → web/urls.py → 具体视图
                                 └── /*       → index 视图 → index.html
                                 
视图 (views/*.py)
    │
    ├── 解析请求 (request.data / request.FILES)
    ├── 查数据库 (Model.objects.filter/get/create)
    ├── 调用外部服务 (AI API、TTS、ASR)
    └── 返回 Response (JSON)
```

### 3.3 Vue 前端渲染流程

```
index.html 加载
    │
    ▼
main.js 执行
    ├── createApp(App.vue)    创建 Vue 实例
    ├── app.use(createPinia()) 安装状态管理
    ├── app.use(router)        安装路由
    └── app.mount('#app')      挂载到 DOM
            │
            ▼
        App.vue (根组件)
            ├── NavBar (导航栏，始终显示)
            └── <RouterView /> (根据 URL 动态渲染页面)
                    │
                    ├── / → HomepageIndex
                    ├── /friend/ → FriendIndex
                    ├── /create/ → CreateIndex
                    └── /user/... → LoginIndex / RegisterIndex / SpaceIndex / ProfileIndex
```

---

## 四、项目目录结构

```
项目根目录/
├── .gitignore                  # Git忽略规则
├── README.md                   # 项目说明
├── main.py                     # PyCharm自动生成的示例文件（无关紧要）
├── backend/                    # Django后端
│   ├── manage.py               # Django命令入口
│   ├── backend/                # Django项目配置目录
│   │   ├── __init__.py
│   │   ├── asgi.py             # ASGI配置（异步网关接口）
│   │   ├── wsgi.py             # WSGI配置（同步网关接口）
│   │   ├── settings.py         # 项目设置（数据库、中间件、认证等）
│   │   └── urls.py             # 总路由
│   └── web/                    # 'web'这个Django应用
│       ├── __init__.py
│       ├── admin.py            # Django后台管理注册
│       ├── apps.py             # 应用配置
│       ├── models.py           # 数据库模型（表定义）
│       ├── tests.py            # 测试
│       ├── urls.py             # web应用的路由
│       ├── views/              # 视图（处理请求）
│       │   ├── __init__.py
│       │   └── index.py        # 首页视图
│       ├── migrations/         # 数据库迁移目录
│       │   └── __init__.py
│       └── templates/          # HTML模板
│           └── index.html      # 首页模板
└── frontend/                   # Vue前端
    ├── .gitignore
    ├── .vscode/extensions.json
    ├── README.md
    ├── index.html              # Vite入口HTML
    ├── jsconfig.json
    ├── package.json            # Node.js依赖配置
    ├── package-lock.json       # 依赖锁定文件
    ├── public/favicon.ico
    ├── vite.config.js          # Vite打包配置
    └── src/                    # 源代码
        ├── main.js             # Vue入口
        ├── App.vue             # 根组件
        ├── assets/             # 静态资源（CSS、图片）
        │   ├── base.css
        │   ├── main.css
        │   └── logo.svg
        ├── components/         # 组件
        │   ├── HelloWorld.vue
        │   ├── TheWelcome.vue
        │   ├── WelcomeItem.vue
        │   └── icons/          # 图标组件
        ├── router/index.js     # 路由
        ├── stores/counter.js   # Pinia状态管理
        └── views/              # 页面
            ├── HomeView.vue
            └── AboutView.vue
```

---

## 三、后端文件逐个讲解

### 3.1 `backend/manage.py`——Django的命令入口

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

**逐行讲解：**

- `#!/usr/bin/env python` —— Shebang（谢邦行），告诉 Linux/Mac 系统用哪个 Python 解释器运行这个脚本。Windows 下这行不起作用但不碍事。
- `import os, sys` —— 导入两个 Python 标准库模块。`os` 用于操作环境变量，`sys` 用于获取命令行参数。
- `def main():` —— 定义一个函数，Django 标准做法，把所有逻辑包在函数里而不是直接写在全局。
- `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')` —— **最关键的一行**。设置环境变量，告诉 Django"配置文件在哪里"。`setdefault` 的意思是：如果环境变量已经设了就用已有的，没设就用 `backend.settings`。`backend.settings` 是 Python 模块路径，对应 `backend/backend/settings.py` 文件。
- `try: from django.core.management import execute_from_command_line` —— 尝试导入 Django 的命令执行器。如果 Django 没装（`ImportError`），就抛出一个友好的错误提示。
- `execute_from_command_line(sys.argv)` —— 把命令行参数（比如 `runserver`、`migrate`）传给 Django 执行。`sys.argv` 是一个列表，比如你在终端敲 `python manage.py runserver`，`sys.argv` 就是 `['manage.py', 'runserver']`。
- `if __name__ == '__main__': main()` —— Python 的入口判断。当你直接运行 `python manage.py` 时，`__name__` 变量被 Python 设为 `'__main__'`，于是调用 `main()`。如果这个文件是被别的文件 import 的，`__name__` 就是 `'manage'`，不会执行 `main()`。

**作用**：这是整个后端的入口，所有操作（启动服务器、创建数据库表、创建管理员账号等）都通过这个文件执行。

---

### 3.2 `backend/backend/settings.py`——项目配置文件

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-j6tt1_pel@3_6u(5sx_-+l#@tu3ubnz)!e_%rob$-fofhyq49i'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'web',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = 'http://127.0.0.1:8000/media/'
MEDIA_ROOT = BASE_DIR / 'media'

from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

**逐行/逐段讲解：**

- `from pathlib import Path` —— 导入 Python 的 `Path` 类，用于处理文件路径。比旧的 `os.path` 更好用，用 `/` 就能拼接路径。
- `BASE_DIR = Path(__file__).resolve().parent.parent` —— 确定项目根目录。`__file__` 是当前文件路径（`backend/backend/settings.py`）。`.resolve()` 转成绝对路径。`.parent` 取父目录，两次 `.parent` 就回到项目根目录（`backend/` 的上一级）。
- `SECRET_KEY = ...` —— Django 的密钥，用于加密 session、CSRF token 等。`django-insecure-` 前缀说明这是开发用的不安全密钥，Django 6.0 新特性，生产环境必须换掉。
- `DEBUG = True` —— 开启调试模式。代码报错时在浏览器直接显示详细错误信息，开发很方便。**生产环境必须关掉**，否则会泄露代码细节。
- `ALLOWED_HOSTS = []` —— 允许哪些域名访问。空列表表示只允许本机访问（`127.0.0.1` / `localhost`）。DEBUG=True 时自动允许 localhost。

**INSTALLED_APPS 段**：告诉 Django 哪些"应用"被激活了。
- `django.contrib.admin` —— Django 自带后台管理系统。
- `django.contrib.auth` —— 用户认证系统（注册、登录、权限）。
- `django.contrib.contenttypes` —— 内容类型框架，让不同模型之间可以建立通用关联。
- `django.contrib.sessions` —— 会话管理，记住用户登录状态。
- `django.contrib.messages` —— 消息框架，用于在页面显示"操作成功"之类的一次性提示。
- `django.contrib.staticfiles` —— 静态文件管理（CSS、JS、图片）。
- `rest_framework` —— **DRF（Django REST Framework）**，用于构建 API。这不是 Django 自带的，需要 `pip install djangorestframework`。
- `web` —— 我们自己的应用（`backend/web/` 目录）。
- `corsheaders` —— **django-cors-headers**，处理跨域请求。前端在 `localhost:5173`，后端在 `localhost:8000`，不同端口也算跨域。没有这个，前端请求后端会被浏览器拦截。（什么是跨域？简单说，浏览器有个安全规则叫"同源策略"——默认情况下，一个网站上的JavaScript只能请求同一个地址的数据。比如你在`localhost:5173`打开的页面上写代码请求`localhost:8000`，浏览器一看端口不一样（5173 vs 8000），就认为是"跨域"了，直接拦截掉。CORS就是服务器主动告诉浏览器："我允许5173那个端口来访问我"，浏览器收到这个许可才会放行。打个比方：你家的门禁（浏览器）默认不让陌生人进，CORS就是你在门上贴了张纸条"允许快递员进来"）

**MIDDLEWARE 段**：中间件是请求/响应处理管道中的一道道"关卡"，请求进来和响应出去都会依次经过这些中间件。（打个比方：就像工厂的流水线——一个产品（请求）从传送带一头进来，经过A工位（安全检查）→ B工位（贴标签）→ C工位（认证身份）→ 到达最终处理器→然后响应再沿着传送带原路返回。每个工位就是一层"中间件"，它们不负责生产产品本身，但在产品流通的过程中做辅助工作。中间件的顺序很重要——比如CORS中间件必须排第一，因为如果连跨域检查都没通过，后面的工位就没必要干活了）
- `CorsMiddleware` 放在最前面——跨域处理必须最先拦截请求。
- `SecurityMiddleware` —— 安全相关的 HTTP 头（HSTS、X-Content-Type-Options 等）。
- `SessionMiddleware` —— 为每个用户创建 session。
- `CommonMiddleware` —— 常见的处理（URL 尾部斜杠重定向、禁止某些 User-Agent 等）。
- `CsrfViewMiddleware` —— CSRF 保护，防止跨站请求伪造攻击。（CSRF是什么？假设你登录了银行网站，浏览器里存了登录cookie。这时候你打开另一个标签页，不小心点开了一个恶意网站。那个恶意网站在背后偷偷向银行网站发了一个"转账"请求——因为你的cookie还在，银行以为是你本人操作的，钱就转走了。CSRF保护就是在银行的表单里塞一个隐藏的随机令牌，恶意网站猜不到这个令牌，请求就会被拒绝。简单说：CSRF保护确保"提交到服务器的请求，一定是服务器自己发的表单产生的"，而不是别的网站伪造的）
- `AuthenticationMiddleware` —— 把用户对象附加到 request 上。
- `MessageMiddleware` —— 消息框架支持。
- `XFrameOptionsMiddleware` —— 防止页面被嵌入 iframe（防点击劫持）。

- `ROOT_URLCONF = 'backend.urls'` —— 指向根路由文件（`backend/backend/urls.py`）。
- `TEMPLATES` —— 模板引擎配置。`APP_DIRS: True` 表示会在每个应用的 `templates/` 目录下找 HTML 文件。
- `WSGI_APPLICATION = 'backend.wsgi.application'` —— WSGI 入口，用于生产环境部署。

**DATABASES 段**：数据库配置。
- `ENGINE: 'django.db.backends.sqlite3'` —— 使用 SQLite3 数据库。SQLite 是一个**文件型数据库**，不需要安装额外的数据库软件（不像 MySQL、PostgreSQL 需要单独安装和配置），适合开发和小型项目。
- `NAME: BASE_DIR / 'db.sqlite3'` —— 数据库文件路径，就在项目根目录下。`BASE_DIR / 'db.sqlite3'` 用了 `Path` 的 `/` 运算符来拼路径，比旧式 `os.path.join()` 更清爽。

**AUTH_PASSWORD_VALIDATORS**：密码强度验证规则。Django 自带的用户系统会自动用这些规则检查密码：
- 不能和用户名太相似
- 最小长度要求
- 不能太常见（如"123456"）
- 不能全是数字

- `LANGUAGE_CODE = 'en-us'` —— 默认语言是英语。以后可以改成 `'zh-hans'`（简体中文）。
- `TIME_ZONE = 'Asia/Shanghai'` —— **时区设为上海**（北京时间 UTC+8），这是从默认值改过的。
- `USE_TZ = True` —— 启用时区支持，存储时间会带时区信息。

**STATIC 和 MEDIA 配置**：
- `STATIC_URL = 'static/'` —— 静态文件的 URL 路径前缀。静态文件指 CSS、JS、图片等不变的文件。
- `STATICFILES_DIRS` —— 开发阶段告诉 Django 去哪里找静态文件。这里指向 `backend/static/` 目录。**开发阶段和生产阶段的静态文件处理方式不同**：开发阶段 Django 自己处理；生产阶段由 Nginx 等反向代理处理。
- `MEDIA_URL` —— 用户上传文件的 URL 前缀。`MEDIA_ROOT` 是文件实际存储位置。

**JWT 认证配置**：
- `REST_FRAMEWORK` 的 `DEFAULT_AUTHENTICATION_CLASSES` —— 配置 DRF 使用 JWT 认证。JWT（JSON Web Token）是一种**无状态**认证方式：用户登录后服务器返回一个加密 token，之后每次请求带上这个 token，服务器通过解析 token 来确认用户身份，不需要在服务器存 session。（什么是"无状态"？传统登录方式是服务器在内存里记一个"张三已登录"的小本本（这叫session，是有状态的），但服务器一重启小本本就丢了。JWT的思路不同——服务器不记小本本，而是给用户发一张"加密身份证"（token），用户每次来都揣着这张证，服务器看一眼证就能确认身份，不需要翻小本本。好处是服务器重启不受影响，多台服务器也不需要共享session。打个比方：传统session就像你去超市存包——超市给你一个号码牌，你凭牌取包，但超市要记录"这个号码对应哪个柜子"；JWT就像你随身带身份证——走到哪掏出来就行，不需要超市帮你存任何东西）
- `SIMPLE_JWT` 详细配置：
  - `ACCESS_TOKEN_LIFETIME` = 2 小时——登录令牌有效期。短有效期更安全。
  - `REFRESH_TOKEN_LIFETIME` = 7 天——刷新令牌有效期。Access Token 过期后用 Refresh Token 换新的，不用重新登录。
  - `ROTATE_REFRESH_TOKENS = True` —— 每次刷新 Access Token 时，Refresh Token 也更新，进一步降低被窃取后的风险。
  - `AUTH_HEADER_TYPES: ('Bearer',)` —— HTTP 头里带的认证前缀。请求头会长这样：`Authorization: Bearer <token>`

**CORS 配置**（跨域资源共享）：
- `CORS_ALLOW_CREDENTIALS = True` —— 允许跨域请求携带 Cookie 和认证信息。
- `CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]` —— 只允许来自 5173 端口（Vite 开发服务器）的请求。5173 是 Vite 的默认端口。

---

### 3.3 `backend/backend/urls.py`——根路由

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
]

# 仅限开发阶段使用。生产阶段需要在nginx里配置。
if settings.DEBUG:
    urlpatterns += static(
        '/assets/',
        document_root=settings.BASE_DIR / 'static/frontend/assets'
    )
    urlpatterns += static(
        '/media/',
        document_root=settings.MEDIA_ROOT
    )
```

**逐行讲解：**

- `path('admin/', admin.site.urls)` —— 访问 `/admin/` 时进入 Django 后台管理系统。
- `path('', include('web.urls'))` —— 其他所有 URL 交给 `web` 应用的路由去处理。`include` 的作用是"转发"：把请求转给子路由。比如用户访问 `/api/token/`，先到这里匹配，然后进入 `web.urls` 继续匹配。
- `if settings.DEBUG:` —— 只在开发阶段生效。`DEBUG=True` 时，Django 自己处理静态文件和媒体文件的访问。生产阶段这些由 Nginx 处理，不走 Django。
- `static('/assets/', ...)` —— 把 `/assets/` URL 映射到 `backend/static/frontend/assets/` 目录（Vite 打包输出在这里）。
- `static('/media/', ...)` —— 把 `/media/` URL 映射到 `MEDIA_ROOT` 目录（用户上传的文件）。

**为什么这样写**：Django 的设计理念是"不要把静态文件交给 Django 处理"——在生产阶段，Nginx 处理静态文件比 Django 快很多。所以这段代码加了 `if settings.DEBUG` 保护，只在开发阶段让 Django 处理，防止不小心上到生产环境。

---

### 3.4 `backend/backend/asgi.py` 和 `wsgi.py`——服务器网关

```python
# asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_asgi_application()
```

```python
# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_wsgi_application()
```

**讲解：**

- ASGI（Asynchronous Server Gateway Interface）和 WSGI（Web Server Gateway Interface）是 Python Web 应用和 Web 服务器之间的**通信协议**。
- **WSGI 是同步的**：一个请求处理完才能处理下一个。适合传统的请求-响应模式。
- **ASGI 是异步的**：支持 WebSocket、长轮询等需要长连接的场景。
- `application` 变量就是服务器要调用的入口。无论是 Gunicorn（WSGI）还是 Daphne（ASGI），都从这个变量启动。
- 两个文件的写法几乎一模一样，唯一的区别是 `get_asgi_application` vs `get_wsgi_application`。**为什么两个文件都需要**：开发阶段用 `manage.py runserver`（WSGI），后续可能引入 WebSocket（需要 ASGI），两个都先建好省得后面再改。

---

### 3.5 `backend/web/admin.py`——后台管理注册

```python
from django.contrib import admin

# Register your models here.
```

**讲解**：目前是空的，只有一个 import 和一个注释。`admin.py` 的作用是注册数据模型到 Django 后台，注册后就能在 `/admin/` 页面里增删改查数据。**为什么放在这**：Django 会自动查找每个应用下的 `admin.py` 并执行，这是 Django 的约定。

---

### 3.6 `backend/web/tests.py`——测试文件

```python
from django.test import TestCase

# Create your tests here.
```

目前只包含 Django 自动生成的模板代码，没有任何实际测试逻辑。后续提交中会逐渐添加真实测试。

---

### 3.8 `backend/web/apps.py`——应用配置

```python
from django.apps import AppConfig

class WebConfig(AppConfig):
    name = 'web'
```

**讲解**：Django 应用的配置类。`name = 'web'` 指定应用名。Django 通过这个类了解应用的基本信息。`INSTALLED_APPS` 里的 `'web'` 和这里的 `name` 对应。

---

### 3.9 `backend/web/models.py`——数据库模型

```python
from django.db import models

# Create your models here.
```

**讲解**：目前是空的。`models.py` 是定义数据库表的地方。Django 的 ORM（对象关系映射，Object-Relational Mapping）允许你用 Python 类来描述数据库表，Django 会自动生成对应的 SQL。（什么是ORM？简单说就是一个"翻译官"——你不用学SQL语言（`CREATE TABLE users(...)`、`SELECT * FROM users WHERE ...`这些），你用Python写`class User(models.Model): name = models.CharField(...)`，ORM自动帮你翻译成数据库能听懂的SQL语句去执行。好处有两个：一是你不用写又臭又长的SQL字符串，二是换数据库（比如从SQLite换成MySQL）时几乎不用改代码——ORM帮你处理了不同数据库的语法差异）

---

### 3.10 `backend/web/urls.py`——Web 应用路由

```python
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from web.views.index import index

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', index),
]
```

**逐行讲解：**

- `from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView` —— 从 `djangorestframework-simplejwt` 库导入两个 JWT 视图。这是第三方库提供的开箱即用的登录接口。
- `path('api/token/', TokenObtainPairView.as_view(), ...)` —— POST 到 `/api/token/` 即登录。前端发来用户名+密码，服务器返回 Access Token 和 Refresh Token。`as_view()` 是把类视图转成 Django 可调用的函数视图的方法。
- `path('api/token/refresh/', TokenRefreshView.as_view(), ...)` —— POST 到 `/api/token/refresh/` 即刷新令牌。前端发来过期的 Access Token + Refresh Token，服务器返回新的 Access Token。
- `path('', index)` —— 根路径（`/`）访问时调用 `index` 函数，返回首页 HTML。

**为什么 JWT 路由放在这里而不是根路由**：JWT 认证是 `web` 这个应用负责的，放在自己的路由里更内聚。这是软件工程中"关注点分离"的体现。

---

### 3.11 `backend/web/views/index.py`——首页视图

```python
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
```

**逐行讲解：**

- `from django.shortcuts import render` —— 导入 `render` 函数。`render` 接收一个请求对象和一个模板名，返回渲染好的 HTML 响应。
- `def index(request):` —— 视图函数。`request` 是 Django 传入的请求对象，包含用户信息、请求方法、请求头等。
- `return render(request, 'index.html')` —— 渲染 `index.html` 模板并返回。Django 会去 `templates/` 目录找到 `index.html`，处理里面的模板语法（如 `{% static %}`），生成纯 HTML 返回给浏览器。

---

### 3.12 `backend/web/templates/index.html`——首页模板

```html
{% load static %}

<!DOCTYPE html>
<html lang="">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="{% static 'frontend/favicon.ico' %}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vite App</title>
    <script type="module" crossorigin src="{% static 'frontend/assets/index-DM0D-WOo.js' %}"></script>
    <link rel="stylesheet" crossorigin href="{% static 'frontend/assets/index-X3LBb3Aa.css' %}">
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

**逐行讲解：**

- `{% load static %}` —— Django 模板标签，加载静态文件处理功能。必须先有这个才能用 `{% static %}`。
- `{% static 'frontend/favicon.ico' %}` —— Django 模板标签，生成静态文件的 URL。Django 会把 `frontend/favicon.ico` 替换成 `/static/frontend/favicon.ico`。
- `<div id="app"></div>` —— Vue 的挂载点。Vue 应用会接管这个 div，在里面渲染所有页面内容。
- `<script type="module" crossorigin src="...">` —— 加载 Vite 打包后的 JavaScript 文件。`type="module"` 表示 ES Module 方式加载。
- `<link rel="stylesheet" crossorigin href="...">` —— 加载 Vite 打包后的 CSS 文件。

**这个文件的作用**：这是生产环境的入口。Django 收到用户请求后，返回这个 HTML；HTML 加载了 Vite 打包好的 JS 和 CSS；Vue 应用启动，接管 `<div id="app">`，渲染出完整的页面。**开发阶段不需要这个文件**——Vite 有自己的开发服务器和 index.html（在 `frontend/index.html`）。

---

### 3.13 `main.py`——PyCharm 自动生成的示例脚本

```python
# 这是一个示例 Python 脚本。

def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':
    print_hi('PyCharm')
```

这个文件是 PyCharm IDE 创建项目时自动生成的，与项目实际功能无关。它在第一次提交时被 `git add -A` 意外包含进来，后面会在提交 06 中被删除。

---

## 四、前端文件逐个讲解

### 4.1 `frontend/package.json`——Node.js 项目配置

```json
{
  "name": "frontend",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "engines": {
    "node": "^20.19.0 || >=22.12.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "pinia": "^3.0.4",
    "vue": "^3.5.26",
    "vue-router": "^4.6.4"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^6.0.3",
    "vite": "^7.3.0",
    "vite-plugin-vue-devtools": "^8.0.5"
  }
}
```

**逐项讲解：**

- `"private": true` —— 标记为私有项目，防止意外发布到 npm 仓库。
- `"type": "module"` —— Node.js 默认使用 CommonJS 模块（`require`），设为 `module` 后可以使用 ES Module（`import` / `export`）。
- `"engines"` —— 要求 Node.js 版本在 20.19+ 或 22.12+，低于这个版本会报警告。
- `"scripts"` —— 快捷命令：
  - `npm run dev` → 启动 Vite 开发服务器（热更新，改代码浏览器自动刷新）。
  - `npm run build` → 打包生产版本，输出到 Django 的 static 目录。
  - `npm run preview` → 预览打包后的效果。
- **dependencies（生产依赖）**：
  - `pinia` —— Vue 3 官方状态管理库，相当于 Vue 2 的 Vuex。
  - `vue` —— Vue 3 框架核心。
  - `vue-router` —— Vue 官方路由库，用于前端页面跳转（不需要刷新浏览器）。
- **devDependencies（开发依赖，只在开发时用，不打包到最终代码）**：
  - `@vitejs/plugin-vue` —— Vite 的 Vue 插件，让 Vite 能编译 `.vue` 文件。
  - `vite` —— 构建工具本身。
  - `vite-plugin-vue-devtools` —— Vue DevTools 集成。

**dependencies 和 devDependencies 的区别**：`dependencies` 会打包到用户访问的 JS 中；`devDependencies` 只在开发构建阶段使用，比如 Vite 本身用户不需要下载。

---

### 4.2 `frontend/vite.config.js`——Vite 构建配置

```javascript
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  build: {
    outDir: path.resolve(__dirname, '../backend/static/frontend'),
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
```

**逐行讲解：**

- `import { fileURLToPath, URL } from 'node:url'` —— 从 Node.js 内置模块导入 URL 处理工具。
- `import { defineConfig } from 'vite'` —— `defineConfig` 是 Vite 的类型辅助函数，提供配置智能提示。
- `plugins: [vue(), vueDevTools()]` —— 启用的插件：Vue 编译 + DevTools。
- **`build.outDir`** 是关键配置：`path.resolve(__dirname, '../backend/static/frontend')` 表示打包结果输出到 `backend/static/frontend/`。这样 Django 就能直接按 static 文件访问了。`__dirname` 是当前文件（`vite.config.js`）所在目录，即 `frontend/`；`../backend/static/frontend` 跳回上一级再进入 Django 的目录。
- `emptyOutDir: true` —— 每次打包先清空输出目录，防止旧文件残留。
- `resolve.alias` —— 设置路径别名。`'@'` 指向 `src/` 目录，写代码时 `import '@/components/xxx.vue'` 等价于 `import './src/components/xxx.vue'`，不用写一长串相对路径（`../../../` 这种噩梦）。

---

### 4.3 `frontend/index.html`——Vite 开发服务器入口

```html
<!DOCTYPE html>
<html lang="">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vite App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

**讲解**：
- 这是给 **Vite 开发服务器**用的入口。和 Django 模板里的 `index.html` 是两套：开发时用这个（Vite 自己处理 `main.js` 的编译）；生产时用 Django 的版本（加载打包好的 JS）。
- `<script type="module" src="/src/main.js">` —— Vite 会拦截这个请求，自动编译 Vue 文件、注入热更新代码等。`/src/main.js` 不是真实文件路径，是 Vite 开发服务器的内部路由。

---

### 4.4 `frontend/src/main.js`——Vue 应用入口

```javascript
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

**逐行讲解：**

- `import './assets/main.css'` —— 导入全局 CSS。在 JavaScript 里导入 CSS 是 Vite 的特性（打包时会把 CSS 抽出来）。
- `import { createApp } from 'vue'` —— 导入 Vue 3 的 `createApp` 函数，用于创建 Vue 应用实例。
- `import { createPinia } from 'pinia'` —— 导入 Pinia 的创建函数。
- `import App from './App.vue'` —— 导入根组件。
- `import router from './router'` —— 导入路由配置（`./router/index.js`）。
- `const app = createApp(App)` —— 创建一个 Vue 应用实例，以 `App.vue` 为根组件。**注意**：`createApp` 不会自动挂载到 DOM。
- `app.use(createPinia())` —— 安装 Pinia 状态管理插件。`createPinia()` 创建一个 Pinia 实例。
- `app.use(router)` —— 安装路由插件。
- `app.mount('#app')` —— 把 Vue 应用挂载到 `<div id="app">` 上。执行后 Vue 接管这个 div，开始渲染页面。

**为什么用 `app.use()` 而不是直接 `import` 后就用**：`use()` 是 Vue 的插件安装机制。插件可以增强 Vue 应用的能力——比如 Pinia 让所有组件都能用 `useStore()`，Router 让所有组件都能用 `useRouter()`。`use()` 内部会调用插件的 `install` 方法做初始化工作。

---

### 4.5 `frontend/src/App.vue`——根组件

```vue
<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
```

**逐行讲解：**

- `<script setup>` —— Vue 3 的"语法糖"，简化组件脚本写法。比传统的 `<script>` + `export default` 更简洁。
- `import { RouterLink, RouterView } from 'vue-router'` —— `RouterLink` 是导航链接组件（类似 `<a>` 但不会刷新浏览器）；`RouterView` 是页面内容占位符，根据当前 URL 显示对应的页面组件。
- `<RouterLink to="/">Home</RouterLink>` —— 一个导航链接，点击后 URL 变成 `/`，`RouterView` 显示 `HomeView` 组件。Vue Router 会拦截点击事件，通过 History API 改变 URL，不会触发浏览器刷新。
- `<RouterView />` —— **关键**。当前 URL 是 `/` 就渲染 `HomeView`，是 `/about` 就渲染 `AboutView`。这个组件的存在让页面能在不刷新浏览器的情况下切换内容（SPA）。

**Vue 单文件组件的结构**：`.vue` 文件有三个区域——`<script>`（逻辑）、`<template>`（结构）、`<style>`（样式），三者写完就是一个完整的组件。

---

### 4.6 `frontend/src/router/index.js`——前端路由

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
```

**逐行讲解：**

- `createWebHistory(import.meta.env.BASE_URL)` —— 使用 HTML5 History 模式的路由。URL 是真实的（如 `/about`），不是丑陋的 hash 模式（`/#/about`）。`import.meta.env.BASE_URL` 是 Vite 的环境变量，默认是 `/`。
- `routes` 数组定义了 URL 和组件的映射关系。
- `path: '/'` → `HomeView` 组件。`HomeView` 在文件顶部直接 import，所以打包时会**立即加载**（首页的 JS 包里包含它）。
- `path: '/about'` → `() => import('../views/AboutView.vue')` —— **懒加载**（Lazy Loading）。用箭头函数 `() => import(...)` 动态导入，`AboutView` 的代码会被拆成单独的 JS 文件，只有用户访问 `/about` 时才从服务器下载。这叫 **code-splitting（代码分割）**，能减小首页的下载量，让页面加载更快。

**为什么首页直接 import，关于页却用动态 import**：首页是用户打开的第一屏，直接加载用户肯定需要它；关于页可能只有部分用户会访问，等需要时再加载可以节省初始带宽和加载时间。这是一个常见的优化策略。

---

### 4.7 `frontend/src/stores/counter.js`——Pinia 状态管理

```javascript
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }
  return { count, doubleCount, increment }
})
```

**逐行讲解：**

- `defineStore('counter', () => {...})` —— 定义一个名叫 `'counter'` 的 Store。Pinia 把这个 Store 注册到全局，任何组件都能调用。
- `ref(0)` —— Vue 3 的**响应式**值。`ref` 把普通值包一层后，当值变化时所有使用了这个值的组件会自动重新渲染。`.value` 才是实际值。（什么是响应式？简单说就是"数据变了，页面自动跟着变"。想象一个电子表格——你在A1格写了`=B1+C1`，当B1或C1变化时A1会自动重新计算。Vue的`ref`就是类似的效果：你用`ref(0)`声明一个"会变的值"，然后在模板里写`{{ count }}`显示它，当`count.value`变成`1`时，页面上显示的数字自动从0变成1，你不需要手动操作DOM去更新页面。没有响应式的话，你需要写`document.getElementById('xxx').innerText = count`这种繁琐的DOM操作代码）
- `computed(() => count.value * 2)` —— **计算属性**。`doubleCount` 自动等于 `count` 的两倍。`computed` 有缓存，依赖不变时不重新计算。
- `return { count, doubleCount, increment }` —— 暴露给外部使用的方法和值。

**什么是 Pinia/状态管理**：如果两个不在同一页面的组件需要共享数据（比如用户登录信息、购物车），传统做法是在组件间层层传递 props，很麻烦。Pinia 提供一个**全局仓库**，任何组件都能读写同一个数据源。

---

### 4.8 其他 Vue 组件

除了前述的核心文件，这个初始提交还包含以下由 Vue CLI / create-vue 工具自动生成的**示例代码**，用于展示 Vue 的基本功能。它们在后续提交 04 中会被全部删除。

#### `HelloWorld.vue`——展示组件属性

```vue
<script setup>
defineProps({
  msg: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      You've successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 { font-weight: 500; font-size: 2.6rem; position: relative; top: -10px; }
h3 { font-size: 1.2rem; }
.greetings h1, .greetings h3 { text-align: center; }
@media (min-width: 1024px) {
  .greetings h1, .greetings h3 { text-align: left; }
}
</style>
```

#### `HomeView.vue`——首页页面

```vue
<script setup>
import TheWelcome from '../components/TheWelcome.vue'
</script>

<template>
  <main>
    <TheWelcome />
  </main>
</template>
```

#### `AboutView.vue`——关于页面

```vue
<template>
  <div class="about">
    <h1>This is an about page</h1>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about { min-height: 100vh; display: flex; align-items: center; }
}
</style>
```

#### `TheWelcome.vue`——欢迎内容容器

该组件使用 `WelcomeItem` 和 5 个图标组件构建了完整的欢迎页面布局，展示了 Vue 的插槽（slot）机制。

#### `WelcomeItem.vue`——列表项容器

使用具名插槽 `icon` 和 `heading` 以及默认插槽，展示了 Vue 组件的组合模式。

#### `icons/` 下的 5 个 SVG 图标组件

`IconCommunity.vue`、`IconDocumentation.vue`、`IconEcosystem.vue`、`IconSupport.vue`、`IconTooling.vue`——每个都是一个内联 SVG 封装为 Vue 组件，展示图标复用模式。

这些示例代码在提交 04 中被完整删除，其全部源代码详见 `04-删除示例代码.md`。

---

### 4.9 `frontend/src/assets/base.css` 和 `main.css`——全局样式

**`base.css`** 定义了 CSS 变量（自定义颜色、间距），支持深色模式（`@media (prefers-color-scheme: dark)`），以及全局的排版重置样式。

**`main.css`** 导入 `base.css`，定义了 `#app` 容器的布局和链接样式。

CSS 变量（如 `--color-background`、`--color-text`）的作用是**统一样式主题**：在 `base.css` 里改一次颜色，所有用了这个变量的组件都跟着变，不用每个文件去手动改。

---

## 五、怎么跑起来

**后端**：
```bash
cd backend
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
python manage.py runserver
# 访问 http://localhost:8000
```

**前端（开发模式）**：
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

**前端（生产打包）**：
```bash
cd frontend
npm run build   # 输出到 backend/static/frontend/
# 然后只启动后端就能访问，因为 Django 会直接提供打包后的静态文件
```

---

## 六、总结

| 文件 | 是什么 | 为什么存在 |
|------|--------|-----------|
| `manage.py` | Django 命令行入口 | 启动服务器、执行迁移、创建管理员等 |
| `settings.py` | 项目全局配置 | 数据库、认证方式、中间件、CORS 等都在这里 |
| `urls.py`（根） | URL→视图的映射 | 根据不同 URL 路径分发给不同处理器 |
| `asgi.py / wsgi.py` | 服务器网关 | Web 服务器（Nginx/Gunicorn）通过它们启动 Django |
| `admin.py` | 后台管理注册 | 让管理员在网页上操作数据库 |
| `models.py` | 数据库表定义 | 用 Python 类描述表结构，Django 自动建表 |
| `views/index.py` | 首页视图 | 处理 HTTP 请求，返回 HTML 页面 |
| `templates/index.html` | 首页模板 | 生产环境入口，加载打包好的 Vue 应用 |
| `package.json` | Node 依赖声明 | 告诉 npm 这个项目需要哪些库 |
| `vite.config.js` | Vite 构建配置 | 控制打包方式、输出路径、路径别名 |
| `main.js` | Vue 入口 | 创建 Vue 应用、安装插件、挂载 DOM |
| `App.vue` | Vue 根组件 | 定义页面整体布局和导航 |
| `router/index.js` | 前端路由 | URL ↔ 页面组件的映射，实现 SPA |
| `stores/counter.js` | Pinia Store 示例 | 演示状态管理用法 |

这次提交虽然代码量大，但**大多是脚手架自动生成的**。真正的业务逻辑从后续提交开始逐步添加。
