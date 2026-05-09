# 第15次提交：创建更新用户资料后端API

**提交哈希**：`fc90606`  
**提交时间**：2026-02-03 20:26:52  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

实现了**更新用户资料**的后端 API——修改用户名、个人简介、头像。同时创建了一个工具函数用于删除旧头像文件（节省磁盘空间）。

---

## 二、使用了什么技术

| 技术/工具/库 | 用途 |
|-------------|------|
| DRF APIView | 继承 APIView 创建 RESTful 接口，利用 IsAuthenticated 权限类和 request.FILES 文件解析 |
| request.FILES（multipart/form-data） | 从请求中提取上传的文件（头像照片），与 request.data（文本字段）分离处理 |
| Django ImageField | 存储用户头像图片，自动处理文件保存和 URL 生成 |
| os.remove / os.path.exists | 文件系统操作，替换头像时删除磁盘上的旧图片文件，防止磁盘空间被废弃文件占满 |
| FormData | 前端构造 multipart 请求体，同时携带文本字段（username, profile）和文件字段（photo） |
| Django ORM (User / UserProfile) | Django 对象关系映射模型，User 存储认证数据，UserProfile 一对一关联存储头像和简介 |
| Django MEDIA_ROOT / MEDIA_URL | 配置文件中的媒体根目录路径和 URL，ImageField 上传的文件存储在 MEDIA_ROOT，通过 MEDIA_URL 访问 |
| RESTful API 设计规范 | POST 方法用于修改资源，路径按功能命名（profile/update/），响应以统一 JSON 格式返回 result 状态码 |

## 三、整体架构 / 数据流

```
用户资料更新流程:

┌──────────────────┐
│  前端 ProfileIndex │
│                   │
│  new FormData()   │
│  append('username')│
│  append('profile')│
│  append('photo')  │  ← 仅当用户选了新头像时
│                   │
│  api.post('/update/', formData) │
└────────┬─────────┘
         │ POST multipart/form-data
         ▼
┌──────────────────────────┐
│  UpdateProfileView        │
│  (APIView, IsAuthenticated)│
│                           │
│  1. 验证用户名/简介非空      │
│  2. 检查用户名是否被占用     │
│  3. 检查是否上传了新头像     │
│                           │
│  ┌─ 有新头像? ─────────┐   │
│  │   │                    │   │
│  │   ▼                    │   │
│  │  remove_old_photo()    │   │
│  │  → 删除磁盘旧文件        │   │
│  │  → 设置新 photo        │   │
│  └───────────────────────┘   │
│                           │
│  4. 更新 UserProfile:     │
│     profile + photo       │
│  5. 更新 User:            │
│     username              │
│  6. 返回更新后的用户信息     │
└──────────┬───────────────┘
           │ Response JSON
           ▼
┌──────────────────┐
│  前端更新 Store     │
│  user.setUserInfo() │
│  → 导航栏/页面同步    │
└──────────────────┘

文件清理流程:

  用户上传新头像
        │
        ▼
  remove_old_photo(user_profile.photo)
        │
        ├── photo 为 None? ──→ 跳过
        ├── 是 default.png? ──→ 跳过 (保留默认图)
        └── 其他文件:
              ├── 拼接 MEDIA_ROOT + photo.name
              ├── os.path.exists() 检查存在
              └── os.remove() 删除
```


---

**User / UserProfile 模型关系**:

```
┌───────────────────────┐        ┌───────────────────────────┐
│   User (Django 内置)   │  1:1   │   UserProfile (自定义扩展)  │
│───────────────────────│────────│───────────────────────────│
│  id (PK)              │        │  id (PK)                  │
│  username  ← 修改      │◄───────│  user (FK → User.id)     │
│  password              │        │  photo (ImageField) ← 修改 │
│  email                 │        │  profile (TextField) ← 修改│
│  ...                   │        │  update_time              │
└───────────────────────┘        └───────────────────────────┘

更新操作涉及两张独立的数据库表:
  user.username 修改        → user.save()            (Django auth_user 表)
  user_profile.photo 修改   → user_profile.save()    (web_userprofile 表)
  user_profile.profile 修改 → user_profile.save()    (web_userprofile 表)
```

**文件存储路径结构**:

```
MEDIA_ROOT = /path/to/media/              (配置于 settings.py)
   │
   └── user/
        └── photos/
             ├── default.png              (新建用户共用默认头像)
             ├── photo_abc123.png         (用户上传的头像文件)
             └── photo_def456.png         (更新头像后生成的新文件)
                                            (旧文件被 remove_old_photo 删除)

上传时 Django ImageField 的处理流程:
  request.FILES['photo'] → Django 自动保存到 MEDIA_ROOT/user/photos/
  → ImageField.url 返回 /media/user/photos/filename.png
```

## 四、UpdateProfileView——更新资料接口

**文件**：`backend/web/views/user/profile/update.py`（新文件）

```python
from django.contrib.auth.models import User
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.user import UserProfile
from web.views.utils.photo import remove_old_photo


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            username = request.data.get('username').strip()
            profile = request.data.get('profile').strip()[:500]
            photo = request.FILES.get('photo', None)

            if not username:
                return Response({'result': '用户名不能为空'})
            if not profile:
                return Response({'result': '简介不能为空'})
            if username != user.username and User.objects.filter(username=username).exists():
                return Response({'result': '用户名已存在'})

            if photo:
                remove_old_photo(user_profile.photo)
                user_profile.photo = photo
            user_profile.profile = profile
            user_profile.update_time = now()
            user_profile.save()
            user.username = username
            user.save()
            return Response({...})
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

**逐段讲解**：

- `request.data.get('username').strip()` —— 用户可能不传这个字段（只想改头像），`.get()` 返回 `None`→`.strip()` 会报 `AttributeError`。这是个潜在 bug：如果只传 `photo` 不传 `username`，代码会在 `.strip()` 处崩溃。后续应该会修复

- `request.FILES.get('photo', None)` —— **`request.FILES`** 和 `request.data` 是不同的属性：
  - `request.data` —— JSON 或表单文本数据
  - `request.FILES` —— 上传的文件（图片等）
  - 两者分离是因为 Django 的文件上传机制不同（文件存临时目录，`FILES` 是文件描述符）。（为什么要分离？这和HTTP的`multipart/form-data`格式有关。普通的POST请求体是`key1=value1&key2=value2`这种文本格式；但上传文件时，请求体被切成多个"部分"（multipart），每个部分有独立的类型标记——文本部分标为`text/plain`，图片部分标为`image/png`并附带文件的二进制数据。所以服务器收到后要把文本和文件分开解析，Django帮你做好了这件事——文本进`request.data`，文件进`request.FILES`。前端用`FormData`对象构造这种混合请求体，Django自动分拣到两个属性里）

- `if username != user.username and User.objects.filter(username=username).exists():` —— 只有当用户**改了**用户名（和原来不同）且新名字被占用时才拒绝。不改用户名时允许提交

- `if photo:` —— 只有当用户上传了新头像才执行替换逻辑。不传照片 = 不换头像

- `remove_old_photo(user_profile.photo)` —— 删掉旧头像文件（见下文）。先删旧再设新

- `user_profile.save()` 和 `user.save()` —— 分别保存 UserProfile 和 User。用户名在 Django 内置 `User` 表里，简介和头像在 `UserProfile` 表里，所以要更新两张表

---

## 五、`remove_old_photo`——删除旧文件工具

**文件**：`backend/web/views/utils/photo.py`（新文件）

```python
import os
from django.conf import settings

def remove_old_photo(photo):
    if photo and photo.name != 'user/photos/default.png':
        old_path = settings.MEDIA_ROOT / photo.name
        if os.path.exists(old_path):
            os.remove(old_path)
```

**逐行讲解**：

- `photo and ...` —— 如果 `photo` 为 None（新用户可能没头像），跳过
- `photo.name != 'user/photos/default.png'` —— 默认头像不能删！所有新用户共用这张图，删了所有人头像都变成空白
- `settings.MEDIA_ROOT / photo.name` —— 拼接出旧文件在磁盘上的绝对路径
- `os.path.exists(old_path)` —— 文件可能已经被手动清理了，检查存在再删，不然 `os.remove` 会异常
- `os.remove(old_path)` —— 真正删除文件

**为什么不放在 UserProfile model 里**：Django 的 `ImageField` 上传新文件时**不会自动删除旧文件**。必须手动处理。放在单独的 utils 文件里是为了复用——后面角色的头像、背景图更换也会用这个函数。

---

## 六、路由

```python
path('api/user/profile/update/', UpdateProfileView.as_view()),
```

---

## 七、总结

| 新增 | 作用 |
|------|------|
| `UpdateProfileView` | 修改用户名+简介+头像（需登录），同一接口可部分更新 |
| `remove_old_photo` | 换头像时删除旧文件，防止磁盘被废弃图片堆满 |
