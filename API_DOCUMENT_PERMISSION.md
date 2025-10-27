# 文档上传权限控制 API 文档

## 📝 更新说明

为文档上传接口新增了 **权限控制** 功能，支持设置文档的访问权限（普通用户可见 / 仅管理员可见）。

---

## 🔥 接口变更

### POST `/api/v1/documents` - 上传文档

#### 变更内容
- **新增参数**: `permission` 
- **请求格式**: 改为 `multipart/form-data`

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|------|------|--------|
| `file` | File | 是 | 文档文件（支持 .pdf, .docx, .txt） | - |
| `permission` | int | 否 | 文档权限：<br>• `0` = 普通用户可见<br>• `1` = 仅管理员可见 | `0` |

#### 请求示例

```javascript
// JavaScript (使用 FormData)
const formData = new FormData();
formData.append('file', fileObject);  // 文件对象
formData.append('permission', 0);     // 0=普通用户可见, 1=仅管理员可见

const response = await fetch('/api/v1/documents', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,  // JWT token
  },
  body: formData
});

const result = await response.json();
```

```javascript
// Vue 3 + Axios 示例
const uploadDocument = async (file, permission = 0) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('permission', permission);
  
  try {
    const response = await axios.post('/api/v1/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('上传失败:', error);
    throw error;
  }
};

// 使用示例
// 上传普通文档
await uploadDocument(file, 0);

// 上传管理员专属文档
await uploadDocument(file, 1);
```

#### 响应格式

**成功响应** (200 OK)
```json
{
  "message": "上传成功",
  "ret": 0,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "example.pdf",
    "size": 1024000,
    "page": 0,
    "url": "/uploads/550e8400-e29b-41d4-a716-446655440000.pdf",
    "content": "...",
    "content_length": 5000,
    "status": 1,
    "status_text": "处理中",
    "permission": 0,  // 🔥 新增字段
    "message": "文档已提交处理，后台正在进行 Embedding"
  }
}
```

**失败响应** (200 OK, ret != 0)
```json
{
  "message": "不支持的文件类型: .exe，支持的类型: .pdf, .docx, .doc, .txt",
  "ret": -2
}
```

---

## 🔐 权限说明

### 权限级别

| permission 值 | 说明 | 可见范围 |
|--------------|------|---------|
| `0` | 普通文档 | 所有用户（包括普通用户和管理员） |
| `1` | 管理员专属文档 | 仅管理员用户 |

### 权限控制逻辑

1. **上传文档**
   - 任何用户都可以上传文档
   - 设置 `permission=1` 后，该文档只对管理员可见

2. **查询文档**
   - **普通用户** (`is_admin=0`)：
     - AI 回答时，只会检索 `permission=0` 的文档
     - 无法查询到 `permission=1` 的管理员文档
   
   - **管理员** (`is_admin=1`)：
     - AI 回答时，可以检索所有文档（`permission=0` 和 `permission=1`）
     - 拥有完整的知识库访问权限

3. **旧文档兼容**
   - 之前上传的文档（没有 `permission` 字段）自动视为 `permission=0`
   - 所有用户都能正常访问旧文档

---

## 🎨 前端建议实现

### 1. 上传表单添加权限选择

```vue
<template>
  <div class="upload-form">
    <el-upload
      :before-upload="handleBeforeUpload"
      :http-request="handleUpload"
      :show-file-list="false"
    >
      <el-button type="primary">选择文件</el-button>
    </el-upload>
    
    <!-- 🔥 权限选择器 -->
    <el-radio-group v-model="permission" class="permission-selector">
      <el-radio :label="0">
        <el-icon><User /></el-icon>
        普通文档（所有用户可见）
      </el-radio>
      <el-radio :label="1">
        <el-icon><Lock /></el-icon>
        管理员文档（仅管理员可见）
      </el-radio>
    </el-radio-group>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const permission = ref(0);  // 默认为普通文档

const handleUpload = async ({ file }) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('permission', permission.value);
  
  // 调用上传接口
  const response = await api.uploadDocument(formData);
  // 处理响应...
};
</script>
```

### 2. 文档列表显示权限标识

```vue
<template>
  <div class="document-item">
    <span class="doc-name">{{ doc.name }}</span>
    
    <!-- 🔥 权限标识 -->
    <el-tag v-if="doc.permission === 1" type="warning" size="small">
      <el-icon><Lock /></el-icon>
      仅管理员
    </el-tag>
    <el-tag v-else type="success" size="small">
      <el-icon><User /></el-icon>
      所有用户
    </el-tag>
  </div>
</template>
```

### 3. API 封装

```javascript
// api/document.js
import request from '@/utils/request';

/**
 * 上传文档
 * @param {FormData} formData - 包含 file 和 permission
 * @returns {Promise}
 */
export const uploadDocument = (formData) => {
  return request({
    url: '/api/v1/documents',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 快捷方法：上传普通文档
 */
export const uploadPublicDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('permission', 0);
  return uploadDocument(formData);
};

/**
 * 快捷方法：上传管理员文档
 */
export const uploadAdminDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('permission', 1);
  return uploadDocument(formData);
};
```

---

## ⚠️ 注意事项

1. **权限参数是可选的**
   - 如果不传 `permission`，默认为 `0`（普通用户可见）
   - 建议在 UI 上明确让用户选择

2. **管理员判断**
   - 用户的管理员身份由后端 JWT token 中的 `is_admin` 字段决定
   - 前端不需要额外处理权限逻辑，只需要传递 `permission` 参数

3. **旧文档兼容**
   - 之前上传的文档会自动视为 `permission=0`
   - 前端无需做任何特殊处理

4. **文件类型限制**
   - 支持的格式：`.pdf`, `.docx`, `.doc`, `.txt`
   - 不支持的格式会返回 `ret=-2` 错误

---

## 📊 完整的用户体验流程

```
用户上传文档 → 选择权限（0/1） → 提交
    ↓
后端处理 → 保存到 MongoDB + 提交 Kafka 任务
    ↓
后台 Embedding → 存储到 Milvus（metadata 包含 permission）
    ↓
用户发起对话
    ↓
AI 检索知识库 → 根据用户的 is_admin 自动过滤文档
    ↓
返回符合权限的搜索结果
```

---

## 🔗 相关接口（无变更）

以下接口保持不变，无需修改：

- `GET /api/v1/documents` - 获取文档列表
- `GET /api/v1/documents/{document_id}` - 获取文档详情
- `DELETE /api/v1/documents/{document_id}` - 删除文档

---

## 📞 联系方式

如有疑问，请联系后端开发团队。

**更新时间**: 2025-10-26
**版本**: v1.1.0

