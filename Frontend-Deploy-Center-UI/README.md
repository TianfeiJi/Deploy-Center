#  Deploy Center UI

Deploy Center UI 是一个基于 [Quasar Framework](https://quasar.dev) 和 Vue 3 构建的现代化前端项目，提供部署自动化平台的交互式界面。项目支持打包为 Web 应用和 Electron 桌面应用，适用于跨平台运行和多场景部署。

---

##  技术栈

-  **Vue 3** + **Quasar 2**
-  状态管理：Pinia
-  网络请求：Axios
-  可视化：Quasar Components、ECharts、Cytoscape、Element Plus
-  桌面应用打包：Electron（通过 Quasar 集成）

---

##  项目结构

```bash
├── public/                   # 公共静态资源（如图标、HTML模板等）
├── src/                      # 主源码目录
│   ├── api/                    # 封装所有后端 API 接口方法
│   ├── assets/                 # 静态资源（如图片、SVG、字体等）
│   ├── boot/                   # Quasar boot 文件（初始化逻辑，如 axios、权限等）
│   ├── components/             # 通用组件库
│   ├── css/                    # 全局样式文件（如变量、reset 样式等）
│   ├── i18n/                   # 国际化配置与语言包
│   ├── layout/                 # 页面布局组件（如导航栏、侧边栏等）
│   ├── pages/                  # 页面级组件（每个视图页面）
│   ├── router/                 # 路由定义与守卫配置
│   ├── stores/                 # Pinia 状态管理模块
│   ├── types/                  # 全局 TypeScript 类型定义
│   └── utils/                  # 通用工具函数与辅助方法
├── .env.development          # 开发环境变量配置
├── .env.production           # 生产环境变量配置
├── quasar.config.js          # Quasar 项目主配置文件
└── package.json              # 项目信息及依赖声明
```

---

##  快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
quasar dev
```

---

##  构建 Web 应用

```bash
quasar build
```

构建输出位于 `dist/spa` 目录。

---

##  打包 Electron 应用

### 步骤 1：添加 Electron 模式（仅首次）

```bash
quasar mode add electron
```

### 步骤 2：构建 Electron 应用

```bash
quasar build -m electron
```

构建完成后，应用位于 `dist/electron` 目录，可直接运行。

---

##  Node.js 要求

由于部分依赖（如 Quasar Vite 插件）要求较高的 Node.js 环境，推荐使用以下版本：

- **Node.js ≥ 18.x**（建议 18.x LTS 或 20.x LTS）
- **npm ≥ 8.x**

---

##  注意事项

- 若需生成 `.exe`、`.dmg` 等安装包，请使用 [electron-builder](https://www.electron.build/) 进行进一步打包。
- 若在中国大陆使用 Electron，请设置镜像源或预下载。
- Electron 打包过程可能涉及系统权限，需在部分平台授予文件访问或执行权限。

---