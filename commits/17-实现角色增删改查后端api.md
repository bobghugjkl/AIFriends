# 第17次提交：实现角色增删改查后端API

**提交哈希**：`b22636c`  
**提交时间**：2026-02-03 21:41:30  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

创建了**Character（AI 虚拟角色）模型**及其完整的 CRUD（增删改查）后端 API。这是项目的核心业务——用户可以创建 AI 角色（设定名字、头像、背景图、人设介绍），之后和这些角色聊天。

---

## 二、使用了什么技术

| 技术/工具/库 | 用途 |
|-------------|------|
| Django ForeignKey（多对一关系） | Character 模型通过 author 外键关联到 UserProfile，建立"一个用户可以创建多个角色"的关系 |
| Django ImageField + upload_to 回调 | 角色头像和背景图的文件上传字段，通过自定义回调函数生成唯一文件名（uuid + 用户ID）并分目录存储 |
| Django ORM CRUD（.create / .get / .filter / .delete） | 增删改查四个 API 分别使用对应的 ORM 方法操作数据库 |
| Django 跨表查询（author__user=request.user） | 使用双下划线语法跨越 ForeignKey 链（Character → UserProfile → User）进行权限隔离查询 |
| remove_old_photo 工具函数 | 更新角色头像/背景图时删除磁盘上的旧文件，复用之前为 UpdateProfileView 创建的工具函数 |

## 三、整体架构 / 数据流

```
角色 CRUD 架构与权限隔离:

作者隔离机制（所有查询都附加 author__user=request.user）:

  ┌────────────┐      ┌──────────────┐      ┌────────────┐
  │   User     │      │  UserProfile │      │ Character  │
  │  (Django)  │      │  (自定义)     │      │  (自定义)   │
  │            │      │              │      │            │
  │  id: 1     │──1:1→│  user_id: 1  │──1:N→│ author_id:1│
  │  username  │      │  profile     │      │  name      │
  │            │      │  photo       │      │  photo     │
  └────────────┘      └──────────────┘      │  background │
                                            │  profile   │
                                            └────────────┘

  权限校验: author__user=request.user
  用户 A 不能查询/修改/删除用户 B 的角色
```

## 四、完整源代码

### 4.1 `models/character.py`——Character 模型

**文件**：`backend/web/models/character.py`（新文件，完整内容）

```python
import uuid

from django.db import models
from django.utils.timezone import now, localtime

from web.models.user import UserProfile


def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'character/photos/{instance.author.user_id}_{filename}'


def background_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'character/background_images/{instance.author.user_id}_{filename}'


class Character(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to=photo_upload_to)
    profile = models.TextField(max_length=100000)
    background_image = models.ImageField(upload_to=background_image_upload_to)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.author.user.username} - {self.name} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"
```

**逐字段讲解**：

- `author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)` —— **多对一外键**。每个角色属于一个创建者；一个创建者可以有多个角色。`on_delete=CASCADE` 表示创建者被删时他的所有角色也删除
- `name = models.CharField(max_length=50)` —— 角色名，最长 50 字符
- `photo = models.ImageField(upload_to=photo_upload_to)` —— 角色头像。上传路径：`character/photos/{作者user_id}_{随机10位uuid}.{扩展名}`
- `profile = models.TextField(max_length=100000)` —— 角色设定/人设介绍。最长 10 万字——角色设定可以非常详细
- `background_image = models.ImageField(upload_to=background_image_upload_to)` —— 聊天背景图。上传到 `character/background_images/` 目录

### 4.2 `views/create/character/create.py`——创建角色

**文件**：`backend/web/views/create/character/create.py`（新文件，完整内容）

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character
from web.models.user import UserProfile


class CreateCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            name = request.data.get('name').strip()
            profile = request.data.get('profile').strip()[:100000]
            photo = request.FILES.get('photo', None)
            background_image = request.FILES.get('background_image', None)

            if not name:
                return Response({
                    'result': '名字不能为空'
                })
            if not profile:
                return Response({
                    'result': '角色介绍不能为空'
                })
            if not photo:
                return Response({
                    'result': '头像不能为空'
                })
            if not background_image:
                return Response({
                    'result': '聊天背景不能为空'
                })

            Character.objects.create(
                author=user_profile,
                name=name,
                profile=profile,
                photo=photo,
                background_image=background_image,
            )
            return Response({
                'result': 'success',
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
```

- 四个字段全为必填：名字、人设、头像、背景图
- `Character.objects.create(...)` —— 一次性创建并保存，等价于 `c = Character(...); c.save()`
- `author=user_profile` —— 设创建者为"当前用户的 UserProfile"，不是直接存 User

### 4.3 `views/create/character/get_single.py`——查询单个角色

**文件**：`backend/web/views/create/character/get_single.py`（新文件，完整内容）

```python
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character


class GetSingleCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            character_id = request.query_params.get('character_id')
            character = Character.objects.get(id=character_id, author__user=request.user)
            return Response({
                'result': 'success',
                'character': {
                    'id': character.id,
                    'name': character.name,
                    'profile': character.profile,
                    'photo': character.photo.url,
                    'background_image': character.background_image.url,
                }
            })
        except:
            return Response({
                'reuslt': '系统异常，请稍后重试'
            })
```

**`request.query_params`** vs `request.data`：
- `query_params` —— URL 查询参数（如 `?character_id=5`），用于 GET 请求
- `data` —— 请求体（JSON 或表单），用于 POST/PUT 请求

- `author__user=request.user` —— **跨表查询**。`author` 是 `UserProfile` 的外键，`author__user` 是 `UserProfile` → `User` 的外键。双下划线 `__` 是 Django ORM 的"跨越关联关系"语法。这确保用户只能查**自己创建的角色**

### 4.4 `views/create/character/update.py`——更新角色

**文件**：`backend/web/views/create/character/update.py`（新文件，完整内容）

```python
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character
from web.views.utils.photo import remove_old_photo


class UpdateCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            character_id = request.data['character_id']
            character = Character.objects.get(id=character_id, author__user=request.user)
            name = request.data['name'].strip()
            profile = request.data['profile'].strip()[:100000]
            photo = request.FILES.get('photo', None)
            background_image = request.FILES.get('background_image', None)

            if not name:
                return Response({
                    'result': "名字不能为空"
                })
            if not profile:
                return Response({
                    'result': '角色介绍不能为空'
                })
            if photo:
                remove_old_photo(character.photo)
                character.photo = photo
            if background_image:
                remove_old_photo(character.background_image)
                character.background_image = background_image
            character.name = name
            character.profile = profile
            character.update_time = now()
            character.save()
            return Response({
                'result': 'success',
            })
        except:
            Response({
                'result': '系统异常，请稍后重试'
            })
```

更新逻辑和 UpdateProfileView 几乎相同：
- 名字和简介必填
- 头像和背景图可选（不传就不换），换新图时用 `remove_old_photo` 删旧图
- 更新 `update_time` → `character.save()`

**注意**：这里 except 分支缺少 `return`，是第18次提交修复的 bug。

### 4.5 `views/create/character/remove.py`——删除角色

**文件**：`backend/web/views/create/character/remove.py`（新文件，完整内容）

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character


class RemoveCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            character_id = request.data['character_id']
            Character.objects.filter(pk=character_id, author__user=request.user).delete()
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
```

- `.filter(...).delete()` —— 先过滤再删除。这里只用了一句 ORM 链式调用，没有先 `.get()` 再 `.delete()`
- `pk=character_id` —— `pk`（Primary Key）是 Django 的万能主键别名，等价于 `id=character_id`
- 如果角色不存在或不属于当前用户 → `.filter()` 返回空 QuerySet → `.delete()` 删 0 行 → 不报错，静默成功。这是一种"幂等"设计

**注意**：这里缺少删除成功后的 `return Response`，是第18次提交修复的 bug。

### 4.6 `admin.py`——Admin 注册

**文件**：`backend/web/admin.py`（完整内容）

```python
from django.contrib import admin
from web.models.user import UserProfile
from web.models.character import Character


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)  #逗号千万不要删！！！！


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
```

### 4.7 `urls.py`——路由注册

**文件**：`backend/web/urls.py`（路由部分）

```python
from django.urls import path, re_path

from web.views.create.character.create import CreateCharacterView
from web.views.create.character.get_single import GetSingleCharacterView
from web.views.create.character.remove import RemoveCharacterView
from web.views.create.character.update import UpdateCharacterView
from web.views.index import index
from web.views.user.account.get_user_info import GetUserInfoView
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.register import RegisterView
from web.views.user.profile.update import UpdateProfileView

urlpatterns = [
    path('api/user/account/register/', RegisterView.as_view()),
    path('api/user/account/login/', LoginView.as_view()),
    path('api/user/account/logout/', LogoutView.as_view()),
    path('api/user/account/get_user_info/', GetUserInfoView.as_view()),
    path('api/user/profile/update/', UpdateProfileView.as_view()),

    path('api/create/character/create/', CreateCharacterView.as_view()),
    path('api/create/character/update/', UpdateCharacterView.as_view()),
    path('api/create/character/remove/', RemoveCharacterView.as_view()),
    path('api/create/character/get_single/', GetSingleCharacterView.as_view()),

    path('', index),

    re_path(r'^(?!media/|static/|assets/).*$', index)
]
```

---

## 五、总结

| 操作 | URL | 方法 | 权限隔离 |
|------|-----|------|---------|
| 创建角色 | `/api/create/character/create/` | POST | 自动绑到当前用户 |
| 查单个角色 | `/api/create/character/get_single/` | GET | `author__user=request.user` |
| 更新角色 | `/api/create/character/update/` | POST | 同上 |
| 删除角色 | `/api/create/character/remove/` | POST | 同上 |

核心设计原则：**每个用户只能操作自己创建的角色**。所有查询都加了 `author__user=request.user` 条件，这是后端安全的基础。
