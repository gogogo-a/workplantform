# RAG 智能问答平台 - 前端项目

基于 Vue 3 + Element Plus 的现代化 RAG 智能问答系统前端界面，采用大屏设计风格，炫酷的视觉效果和流畅的用户体验。

## ✨ 特性

### 🎨 视觉设计
- ✅ **暗色主题**：深色背景配合霓虹色彩，营造科技感
- ✅ **粒子背景**：动态粒子效果，自动连接和移动
- ✅ **霓虹特效**：蓝色、紫色、粉色霓虹灯效果
- ✅ **流畅动画**：淡入、滑动、发光等过渡动画
- ✅ **毛玻璃效果**：背景模糊效果提升视觉层次
- ✅ **渐变按钮**：彩色渐变按钮，悬停发光效果

### 💬 聊天功能
- ✅ **多会话管理**：创建和切换多个对话会话
- ✅ **流式响应**：实时显示 AI 回复，Token-by-Token 输出
- ✅ **思考过程可视化**：可选显示 AI 的推理过程
- ✅ **消息历史**：完整的对话历史记录
- ✅ **文件上传**：支持上传文档到知识库
- ✅ **快捷键支持**：Enter 发送，Shift+Enter 换行
- ✅ **消息操作**：复制、重新生成等功能

### 👤 用户系统
- ✅ **多种登录方式**：昵称+密码、邮箱验证码
- ✅ **用户注册**：邮箱验证码注册
- ✅ **角色管理**：普通用户和管理员
- ✅ **权限控制**：基于角色的页面访问控制

### 🛠️ 管理后台（仅管理员）
- ✅ **用户管理**：查看、搜索、删除用户，设置管理员
- ✅ **文档管理**：上传、查看、删除知识库文档
- ✅ **分页和搜索**：支持关键词搜索和分页浏览

## 🏗️ 技术栈

- **框架**: Vue 3.5（Composition API）
- **构建工具**: Vite 7
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 请求**: Axios
- **动画效果**: 
  - Canvas 粒子背景
  - CSS3 动画
  - Anime.js
- **工具库**: @vueuse/core

## 📁 项目结构

```
plantform_vue/
├── public/                     # 静态资源
│   └── favicon.ico
├── src/
│   ├── api/                    # API 接口封装
│   │   ├── request.js          # Axios 封装
│   │   ├── user.js             # 用户相关 API
│   │   ├── document.js         # 文档相关 API
│   │   ├── session.js          # 会话相关 API
│   │   ├── message.js          # 消息相关 API（含 SSE）
│   │   └── index.js            # API 统一导出
│   ├── assets/                 # 资源文件
│   │   ├── css/
│   │   │   └── global.css      # 全局样式（暗色主题、动画）
│   │   ├── img/
│   │   └── js/
│   ├── components/             # 组件
│   │   ├── public/             # 公共组件
│   │   │   ├── ParticleBackground.vue    # 粒子背景
│   │   │   ├── AppHeader.vue             # 顶部导航栏
│   │   │   ├── LoadingSpinner.vue        # 加载动画
│   │   │   └── EmptyState.vue            # 空状态
│   │   ├── chat/               # 聊天页面组件
│   │   │   ├── SessionList.vue           # 会话列表
│   │   │   ├── ChatMessage.vue           # 聊天消息
│   │   │   └── MessageInput.vue          # 消息输入框
│   │   ├── login/              # 登录注册组件
│   │   │   ├── LoginForm.vue             # 登录表单
│   │   │   └── RegisterForm.vue          # 注册表单
│   │   └── admin/              # 管理员页面组件（未来扩展）
│   ├── router/                 # 路由配置
│   │   └── index.js            # 路由定义和守卫
│   ├── store/                  # 状态管理
│   │   ├── user.js             # 用户状态
│   │   ├── chat.js             # 聊天状态
│   │   └── index.js            # Store 导出
│   ├── utils/                  # 工具函数
│   ├── views/                  # 页面视图
│   │   ├── chat/
│   │   │   └── ChatView.vue              # 聊天页面
│   │   ├── login/
│   │   │   ├── LoginView.vue             # 登录页面
│   │   │   └── RegisterView.vue          # 注册页面
│   │   └── admin/
│   │       ├── AdminLayout.vue           # 管理后台布局
│   │       ├── UserManagement.vue        # 用户管理
│   │       └── DocumentManagement.vue    # 文档管理
│   ├── App.vue                 # 根组件
│   └── main.js                 # 应用入口
├── .env.development            # 开发环境配置
├── .env.production             # 生产环境配置
├── index.html                  # HTML 入口
├── package.json                # 项目依赖
├── vite.config.js              # Vite 配置
└── README.md                   # 本文件
```

## 🚀 快速开始

### 1. 环境要求

- **Node.js**: >= 20.19.0 或 >= 22.12.0
- **npm**: >= 9.0.0

### 2. 安装依赖

```bash
cd web/plantform_vue
npm install
```

### 3. 配置环境变量

开发环境默认配置（`.env.development`）：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

生产环境配置（`.env.production`）：

```bash
VITE_API_BASE_URL=http://your-production-domain.com
```

### 4. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

### 5. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 6. 预览生产构建

```bash
npm run preview
```

## 🎯 开发规范

### 组件组织规范

> **重要：分组件、模块化开发，避免代码耦合！**

1. **公共组件** (`components/public/`)
   - 全局通用的组件（如背景、导航栏、加载动画等）
   - 可被任何页面复用
   - 示例：`ParticleBackground.vue`, `AppHeader.vue`

2. **页面专属组件** (`components/{page}/`)
   - 特定页面的组件，放在对应页面目录下
   - 示例：
     - `components/chat/` - 聊天页面组件
     - `components/login/` - 登录注册组件
     - `components/admin/` - 管理页面组件

3. **组件命名规范**
   - 使用 PascalCase 命名（如 `ChatMessage.vue`）
   - 名称要清晰描述功能
   - 避免缩写，除非是通用缩写

4. **组件拆分原则**
   - 单个组件不超过 300 行代码
   - 功能独立、职责单一
   - 可复用的逻辑提取为 composables

### 代码风格

1. **Vue 3 Composition API**
   - 优先使用 `<script setup>` 语法
   - 使用 `ref` 和 `reactive` 管理状态
   - 使用 `computed` 定义计算属性

2. **样式规范**
   - 使用 `scoped` 样式避免污染
   - 使用 CSS 变量（在 `global.css` 中定义）
   - 避免内联样式

3. **API 调用**
   - 统一使用 `src/api/` 中的封装
   - 错误处理要完善
   - 显示加载状态和错误提示

## 🎨 主题定制

全局 CSS 变量定义在 `src/assets/css/global.css`：

```css
:root {
  --bg-primary: #0a0e27;        /* 主背景色 */
  --bg-secondary: #151932;      /* 次要背景色 */
  --bg-tertiary: #1e2139;       /* 三级背景色 */
  --text-primary: #e2e8f0;      /* 主文本色 */
  --text-secondary: #94a3b8;    /* 次要文本色 */
  --text-tertiary: #64748b;     /* 三级文本色 */
  --border-color: #2d3250;      /* 边框颜色 */
  --primary-color: #6366f1;     /* 主题色 */
  --neon-blue: #00d9ff;         /* 霓虹蓝 */
  --neon-purple: #a855f7;       /* 霓虹紫 */
  --neon-pink: #ec4899;         /* 霓虹粉 */
}
```

## 📱 页面说明

### 1. 登录页 (`/login`)
- 支持昵称+密码登录
- 支持邮箱验证码登录
- 表单验证
- 60秒验证码倒计时

### 2. 注册页 (`/register`)
- 邮箱验证码注册
- 密码强度验证
- 确认密码验证

### 3. 聊天页 (`/chat`)
- 左侧：会话列表，支持创建新会话和切换
- 中间：聊天消息区域，流式显示 AI 回复
- 底部：消息输入框，支持文件上传
- 思考过程可视化（可选）

### 4. 管理后台 (`/admin`)
#### 用户管理 (`/admin/users`)
- 查看所有用户
- 搜索用户
- 设置管理员
- 删除用户

#### 文档管理 (`/admin/documents`)
- 上传文档
- 查看文档列表
- 搜索文档
- 删除文档

## 🔧 核心功能实现

### SSE 流式消息

使用 Fetch API 实现 Server-Sent Events：

```javascript
const response = await fetch(`${baseURL}/messages`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(data)
})

const reader = response.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  
  const chunk = decoder.decode(value, { stream: true })
  // 处理 SSE 事件
}
```

### 路由守卫

自动检查登录状态和权限：

```javascript
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/chat')
    return
  }
  
  next()
})
```

## 🐛 常见问题

### 1. 页面空白
- 检查后端 API 是否启动
- 检查 `.env.development` 中的 API 地址是否正确
- 打开浏览器控制台查看错误信息

### 2. 登录失败
- 确认用户已注册
- 检查网络请求是否成功
- 查看后端日志

### 3. 流式消息不显示
- 确认后端支持 SSE
- 检查网络请求的 Content-Type 是否为 `text/event-stream`
- 查看浏览器控制台的网络请求

### 4. 文件上传失败
- 检查文件大小（限制 10MB）
- 检查文件格式（仅支持 PDF、DOC、DOCX、TXT）
- 确认后端接口正常

## 📦 依赖说明

### 核心依赖
- `vue`: ^3.5.22 - Vue 3 框架
- `vue-router`: ^4 - 路由管理
- `pinia`: - 状态管理
- `axios`: - HTTP 请求库
- `element-plus`: - UI 组件库
- `@element-plus/icons-vue`: - Element Plus 图标

### 开发依赖
- `vite`: ^7.1.11 - 构建工具
- `@vitejs/plugin-vue`: ^6.0.1 - Vue 插件
- `vite-plugin-vue-devtools`: ^8.0.3 - Vue DevTools

### 动画和特效
- `@vueuse/core`: - Vue 工具集
- `particles.vue3`: - 粒子背景效果
- `animejs`: - 动画库

## 🔄 更新日志

### v1.0.0 (2024-10-24)
- ✅ 初始版本发布
- ✅ 完成用户登录注册功能
- ✅ 完成聊天页面（流式消息）
- ✅ 完成管理后台（用户管理、文档管理）
- ✅ 实现炫酷的粒子背景特效
- ✅ 实现暗色主题和霓虹灯效果

## 📄 License

MIT

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请联系开发团队。
