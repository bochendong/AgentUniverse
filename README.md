# AgentUniverse

[English](README_EN.md) | 中文

<h4 align="center">🤖 你的智能笔记生成助手</h4>

<p align="center">
  <a href="https://github.com/bochendong/AgentUniverse/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square" alt="License" /></a>
  <a href="https://github.com/bochendong/AgentUniverse/blob/main/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome" /></a>
  <a href="https://github.com/bochendong/AgentUniverse"><img src="https://img.shields.io/github/stars/bochendong/AgentUniverse?style=flat-square&logo=github" alt="GitHub Stars" /></a>
  <a href="https://github.com/bochendong/AgentUniverse"><img src="https://img.shields.io/github/forks/bochendong/AgentUniverse?style=flat-square&logo=github" alt="GitHub Forks" /></a>
  <a href="https://github.com/bochendong/AgentUniverse/issues"><img src="https://img.shields.io/github/issues/bochendong/AgentUniverse?style=flat-square&logo=github" alt="GitHub Issues" /></a>
  <br>
  <a href="https://discord.gg/your-invite-link"><img src="https://img.shields.io/discord/your-server-id?label=Discord&logo=discord&style=flat-square&color=5865F2" alt="Discord" /></a>
  <a href="https://twitter.com/yourusername"><img src="https://img.shields.io/twitter/follow/yourusername?style=flat-square&logo=twitter&color=1DA1F2" alt="Twitter Follow" /></a>
  <a href="https://github.com/bochendong/AgentUniverse"><img src="https://img.shields.io/github/last-commit/bochendong/AgentUniverse?style=flat-square&logo=git" alt="Last Commit" /></a>
</p>


<div align="center">
  <img src="imgs/cover.png" alt="AgentUniverse Cover" width="100%">
</div>



<p align="center">
  <strong>基于多层级 AI Agent 架构的智能笔记生成与管理平台</strong>
</p>

<p align="center">
  让 AI Agent 协作，自动生成高质量的结构化学习笔记，从文件解析到内容优化，全流程智能化。
</p>

## ✨ 核心亮点

### 🎯 智能笔记生成
- **多源输入**：支持从文件（Markdown、Word）、论文、PPT 或纯主题描述生成笔记
- **结构化输出**：自动生成包含定义、概念、例子、练习题、证明、总结的完整学习笔记
- **质量保证**：自动优化内容，补充缺失信息，确保笔记完整性和准确性

### 🧠 多层级 Agent 协作
采用创新的三层 Agent 架构，实现智能任务分发和内容管理：

```
TopLevelAgent → MasterAgent → NotebookAgent
```

每个层级各司其职，协同工作，实现复杂任务的智能分解和执行。

### 🔄 模块化设计
- **章节创建器**：根据不同输入类型（文件、论文、从零生成）自动选择最优策略
- **内容优化器**：自动识别并优化练习题、证明等内容的完整性
- **内容修改器**：通过自然语言交互，轻松修改和调整笔记内容

### 💬 自然语言交互
- 用自然语言描述需求，系统自动理解并执行
- 支持对话式修改，无需手动编辑
- 智能识别用户意图，提供最佳处理方案

## 🚀 快速开始

### 环境要求
- Python 3.13+
- Node.js 18+
- npm (通常随 Node.js 一起安装)
- OpenAI API Key

> **⚠️ 如果未安装 Node.js 和 npm：**
> 
> 运行 `./scripts/start_frontend.sh` 时，如果检测到 Node.js 或 npm 未安装，脚本会提示错误。请先按照下面的说明安装 Node.js 和 npm，然后再启动前端服务。

### 安装依赖

#### 安装 Node.js 和 npm

如果您的系统尚未安装 Node.js 和 npm，请按照以下步骤安装：

**macOS:**
```bash
# 使用 Homebrew 安装（推荐）
brew install node

# 或从官网下载安装包
# 访问 https://nodejs.org/ 下载并安装
```

**Linux (Ubuntu/Debian):**
```bash
# 使用 apt 安装
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 或使用 nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Windows:**
- 访问 [Node.js 官网](https://nodejs.org/) 下载 Windows 安装包
- 运行安装程序，按照提示完成安装
- npm 会随 Node.js 一起自动安装

**验证安装:**
```bash
node --version  # 应显示 v18.x.x 或更高版本
npm --version   # 应显示 9.x.x 或更高版本
```

#### 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 一键启动

```bash
# 克隆项目
git clone https://github.com/bochendong/AgentUniverse.git
cd AgentUniverse

# 后端设置
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量（添加 OpenAI API Key）
cp .env.example .env

# 启动服务
./scripts/start_backend.sh

# 在另一个终端
./scripts/start_frontend.sh
```

访问 http://localhost:3001 开始使用！

## 💡 使用示例

### 从文件生成笔记
```
用户：请为我生成一份关于"群论"的笔记
[上传 group.md 文件]

系统：分析文件 → 生成大纲 → 创建结构化笔记本 ✅
```

### 从零生成笔记
```
用户：能否为我生成一份PPO（强化学习）方面的笔记？

系统：生成详细大纲 → 等待确认 → 生成完整笔记内容 ✅
```

### 智能修改内容
```
用户：请修改第一章的定义，让它更清晰一些

系统：识别内容 → 调用修改 Agent → 更新笔记 ✅
```

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI** - 高性能 API 框架
- **OpenAI Agents SDK** - AI Agent 核心框架
- **SQLite** - 轻量级数据持久化
- **Pydantic** - 数据验证和序列化

### 前端技术栈
- **React 18** - 现代化 UI 框架
- **Material-UI** - 精美的 UI 组件
- **React Markdown** - Markdown 渲染
- **KaTeX** - 数学公式支持

## 📦 项目结构

```
AgentUniverse/
├── backend/              # 后端核心代码
│   ├── agent/           # 多层级 Agent 实现
│   ├── tools/           # 工具和 Agent-as-Tool
│   ├── api/             # RESTful API
│   └── models/          # 数据模型
├── frontend/            # React 前端应用
├── export/              # 笔记导出工具
└── scripts/             # 启动脚本
```

## 🎨 功能特性

### 📝 笔记生成
- ✅ 支持多种输入格式（Markdown、Word、论文等）
- ✅ 自动识别内容质量，选择最优处理策略
- ✅ 生成结构化的学习笔记（定义、例子、练习题、证明等）
- ✅ 自动优化内容完整性

### 🔧 内容管理
- ✅ 智能任务分发到合适的 Agent
- ✅ 支持多笔记本并行管理
- ✅ 自动保存和版本管理

### 🎯 内容优化
- ✅ 自动识别题目类型并补充缺失内容
- ✅ 优化证明步骤，补充中间过程
- ✅ 提升笔记整体质量

### 💬 交互式修改
- ✅ 自然语言修改笔记内容
- ✅ 支持添加、删除、修改各类内容
- ✅ 实时更新和保存

## 📊 系统优势

1. **智能化**：AI Agent 自动理解用户意图，选择最优处理策略
2. **模块化**：清晰的架构设计，易于扩展和维护
3. **用户友好**：自然语言交互，无需学习复杂操作
4. **高质量**：自动优化和补充，确保笔记完整性
5. **可扩展**：插件化设计，轻松添加新功能

## 🔮 未来规划

- [ ] 支持更多文件格式（PDF、PPT 等）
- [ ] 多语言支持
- [ ] 协作功能（多人编辑）
- [ ] 笔记模板系统
- [ ] 知识图谱可视化

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[添加许可证信息]

## 👥 参与者

<table>
  <tbody>
    <tr>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/bochendong">
          <img src="https://github.com/bochendong.png?size=128" />
          <br>
          Bochen Dong
        </a>
        <br>
        <sub><sup>Team Leader</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/zhangenzhi">
          <img src="https://github.com/zhangenzhi.png?size=128" />
          <br>
          Zhangen Zhi
        </a>
        <br>
        <sub><sup>Team Leader</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/Audreyz7">
          <img src="https://github.com/Audreyz7.png?size=128" />
          <br>
          Audreyz7
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/elenayyy-1218">
          <img src="https://github.com/elenayyy-1218.png?size=128" />
          <br>
          Elena
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/Superb-947">
          <img src="https://github.com/Superb-947.png?size=128" />
          <br>
          Yolo
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
    </tr>
    <tr>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/kirisssss">
          <img src="https://github.com/kirisssss.png?size=128" />
          <br>
          kirisssss
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/LuyifeiMi">
          <img src="https://github.com/LuyifeiMi.png?size=128" />
          <br>
          LuyifeiMi
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/wangpenghan66-boop">
          <img src="https://github.com/wangpenghan66-boop.png?size=128" />
          <br>
          Shark
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/Zhirui920">
          <img src="https://github.com/Zhirui920.png?size=128" />
          <br>
          Zhirui
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
      <td align="center" valign="middle" width="128">
        <a href="https://github.com/wangyeyu1129">
          <img src="https://github.com/wangyeyu1129.png?size=128" />
          <br>
          wangyeyu1129
        </a>
        <br>
        <sub><sup>Team Member</sup></sub>
      </td>
    </tr>
  </tbody>
</table>

---

**让 AI 成为你的学习助手，让笔记生成变得简单高效！** 🚀
