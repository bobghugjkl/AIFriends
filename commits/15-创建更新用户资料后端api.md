# 第15次提交：创建更新用户资料后端API

**提交哈希**：`fc90606`  
**提交时间**：2026-02-03 20:26:52  
**提交者**：xuecan yan

---

## 一、这次提交做了什么

实现了**更新用户资料**的后端 API——修改用户名、个人简介、头像。同时创建了一个工具函数用于删除旧头像文件（节省磁盘空间）。

---

## 二、UpdateProfileView——更新资料接口

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
  - 两者分离是因为 Django 的文件上传机制不同（文件存临时目录，`FILES` 是文件描述符）

- `if username != user.username and User.objects.filter(username=username).exists():` —— 只有当用户**改了**用户名（和原来不同）且新名字被占用时才拒绝。不改用户名时允许提交

- `if photo:` —— 只有当用户上传了新头像才执行替换逻辑。不传照片 = 不换头像

- `remove_old_photo(user_profile.photo)` —— 删掉旧头像文件（见下文）。先删旧再设新

- `user_profile.save()` 和 `user.save()` —— 分别保存 UserProfile 和 User。用户名在 Django 内置 `User` 表里，简介和头像在 `UserProfile` 表里，所以要更新两张表

---

## 三、`remove_old_photo`——删除旧文件工具

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

## 四、路由

```python
path('api/user/profile/update/', UpdateProfileView.as_view()),
```

---

## 五、总结

| 新增 | 作用 |
|------|------|
| `UpdateProfileView` | 修改用户名+简介+头像（需登录），同一接口可部分更新 |
| `remove_old_photo` | 换头像时删除旧文件，防止磁盘被废弃图片堆满 |
