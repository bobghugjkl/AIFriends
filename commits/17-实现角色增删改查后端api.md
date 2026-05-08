# 第17次提交：实现角色增删改查后端API

**提交哈希**：`b22636c`  
**提交时间**：2026-02-03 21:41:30  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

创建了**Character（AI 虚拟角色）模型**及其完整的 CRUD（增删改查）后端 API。这是项目的核心业务——用户可以创建 AI 角色（设定名字、头像、背景图、人设介绍），之后和这些角色聊天。

---

## 二、Character 模型

**文件**：`backend/web/models/character.py`（新文件）

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

- `profile = models.TextField(max_length=100000)` —— 角色设定/人设介绍。最长 10 万字——角色设定可以非常详细，比如"你是一个傲娇的猫娘，说话带喵尾，喜欢吐槽..."，这些会被作为 System Prompt 发给 AI

- `background_image = models.ImageField(upload_to=background_image_upload_to)` —— 聊天背景图。上传到 `character/background_images/` 目录

**注意迁移文件**：`0003` 和 `0004` 两条迁移：先 `photo` → `photo2`，再 `photo2` → `photo`。这是因为开发过程中作者改了模型（可能是字段类型或顺序），Django 生成了一次 rename + 改回的操作。两条迁移一起执行等效于什么都没做，但这是 Django 迁移链的要求——每一步都不可跳过。

---

## 三、四个 API 接口

### 3.1 CreateCharacterView——创建角色

```python
class CreateCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        name = request.data.get('name').strip()
        profile = request.data.get('profile').strip()[:100000]
        photo = request.FILES.get('photo', None)
        background_image = request.FILES.get('background_image', None)

        # 四个字段都不能为空
        Character.objects.create(
            author=user_profile, name=name, profile=profile,
            photo=photo, background_image=background_image,
        )
```

**讲解**：

- 四个字段全为必填：名字、人设、头像、背景图
- `Character.objects.create(...)` —— 一次性创建并保存，等价于 `c = Character(...); c.save()`
- `author=user_profile` —— 设创建者为"当前用户的 UserProfile"，不是直接存 User。这个外键链：`Character → UserProfile → User`

### 3.2 GetSingleCharacterView——查询单个角色

```python
class GetSingleCharacterView(APIView):
    def get(self, request):
        character_id = request.query_params.get('character_id')
```

**`request.query_params`** vs `request.data`：
- `query_params` —— URL 查询参数（如 `?character_id=5`），用于 GET 请求
- `data` —— 请求体（JSON 或表单），用于 POST/PUT 请求

```python
        character = Character.objects.get(id=character_id, author__user=request.user)
```

- `author__user=request.user` —— **跨表查询**。`author` 是 `UserProfile` 的外键，`author__user` 是 `UserProfile` → `User` 的外键。双下划线 `__` 是 Django ORM 的"跨越关联关系"语法。这确保用户只能查**自己创建的角色**——即使知道别人角色的 id，查询也会返回"找不到"（权限隔离）

返回格式包含了 `character` 嵌套对象，和注册/登录返回的用户信息结构类似。

### 3.3 UpdateCharacterView——更新角色

```python
character_id = request.data['character_id']   # 必传
character = Character.objects.get(id=character_id, author__user=request.user)
```

更新逻辑和 UpdateProfileView 几乎相同：
- 名字和简介必填
- 头像和背景图可选（不传就不换），换新图时用 `remove_old_photo` 删旧图
- 更新 `update_time` → `character.save()`

### 3.4 RemoveCharacterView——删除角色

```python
class RemoveCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        character_id = request.data['character_id']
        Character.objects.filter(pk=character_id, author__user=request.user).delete()
```

**讲解**：

- `.filter(...).delete()` —— 先过滤再删除。这里只用了一句 ORM 链式调用，没有先 `.get()` 再 `.delete()`
- `pk=character_id` —— `pk`（Primary Key）是 Django 的万能主键别名，等价于 `id=character_id`
- 如果角色不存在或不属于当前用户 → `.filter()` 返回空 QuerySet → `.delete()` 删 0 行 → 不报错，静默成功。这是一种"幂等"设计——删一个不存在的角色和删一个存在的角色结果一样

---

## 四、Admin 注册

```python
@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
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
