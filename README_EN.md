# AgentUniverse

English | [中文](README.md)

<h4 align="center">🤖 Your Intelligent Note Generation Assistant</h4>

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
  <strong>Intelligent Note Generation and Management Platform Based on Multi-Layer AI Agent Architecture</strong>
</p>

<p align="center">
  Let AI Agents collaborate to automatically generate high-quality structured learning notes, from file parsing to content optimization, fully intelligent workflow.
</p>

## ✨ Core Highlights

### 🎯 Intelligent Note Generation
- **Multiple Input Sources**: Support generating notes from files (Markdown, Word), research papers, PPTs, or pure topic descriptions
- **Structured Output**: Automatically generate complete learning notes including definitions, concepts, examples, exercises, proofs, and summaries
- **Quality Assurance**: Automatically optimize content, supplement missing information, ensuring note completeness and accuracy

### 🧠 Multi-Layer Agent Collaboration
Adopting an innovative three-layer Agent architecture for intelligent task distribution and content management:

```
TopLevelAgent → MasterAgent → NotebookAgent
```

Each layer has its own responsibilities, working collaboratively to achieve intelligent decomposition and execution of complex tasks.

### 🔄 Modular Design
- **Section Creators**: Automatically select optimal strategies based on different input types (files, papers, from scratch)
- **Content Refiners**: Automatically identify and optimize the completeness of exercises, proofs, and other content
- **Content Modifiers**: Easily modify and adjust note content through natural language interaction

### 💬 Natural Language Interaction
- Describe requirements in natural language, the system automatically understands and executes
- Support conversational modifications without manual editing
- Intelligently recognize user intent and provide optimal solutions

## 🚀 Quick Start

### Requirements
- Python 3.13+
- Node.js 18+
- npm (usually comes with Node.js)
- OpenAI API Key

> **⚠️ If Node.js and npm are not installed:**
> 
> When running `./scripts/start_frontend.sh`, if Node.js or npm is not detected, the script will show an error. Please install Node.js and npm first following the instructions below, then start the frontend service.

### Installing Dependencies

#### Installing Node.js and npm

If Node.js and npm are not installed on your system, please follow these steps:

**macOS:**
```bash
# Install using Homebrew (recommended)
brew install node

# Or download from official website
# Visit https://nodejs.org/ to download and install
```

**Linux (Ubuntu/Debian):**
```bash
# Install using apt
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or use nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Windows:**
- Visit [Node.js official website](https://nodejs.org/) to download Windows installer
- Run the installer and follow the prompts
- npm will be automatically installed with Node.js

**Verify Installation:**
```bash
node --version  # Should show v18.x.x or higher
npm --version   # Should show 9.x.x or higher
```

#### Installing Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### One-Click Setup

```bash
# Clone the repository
git clone https://github.com/bochendong/AgentUniverse.git
cd AgentUniverse

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment variables (add OpenAI API Key)
cp .env.example .env

# Start services
./scripts/start_backend.sh

# In another terminal
./scripts/start_frontend.sh
```

Visit http://localhost:3001 to get started!

## 💡 Usage Examples

### Generate Notes from File
```
User: Please generate a note about "Group Theory" for me
[Upload group.md file]

System: Analyze file → Generate outline → Create structured notebook ✅
```

### Generate Notes from Scratch
```
User: Can you generate a note about PPO (Reinforcement Learning) for me?

System: Generate detailed outline → Wait for confirmation → Generate complete note content ✅
```

### Intelligent Content Modification
```
User: Please modify the definition in Chapter 1 to make it clearer

System: Identify content → Call modification Agent → Update notes ✅
```

## 🏗️ Technical Architecture

### Backend Tech Stack
- **FastAPI** - High-performance API framework
- **OpenAI Agents SDK** - AI Agent core framework
- **SQLite** - Lightweight data persistence
- **Pydantic** - Data validation and serialization

### Frontend Tech Stack
- **React 18** - Modern UI framework
- **Material-UI** - Beautiful UI components
- **React Markdown** - Markdown rendering
- **KaTeX** - Mathematical formula support

## 📦 Project Structure

```
AgentUniverse/
├── backend/              # Backend core code
│   ├── agent/           # Multi-layer Agent implementation
│   ├── tools/           # Tools and Agent-as-Tool
│   ├── api/             # RESTful API
│   └── models/          # Data models
├── frontend/            # React frontend application
├── export/              # Note export tools
└── scripts/             # Startup scripts
```

## 🎨 Features

### 📝 Note Generation
- ✅ Support multiple input formats (Markdown, Word, papers, etc.)
- ✅ Automatically identify content quality and select optimal processing strategy
- ✅ Generate structured learning notes (definitions, examples, exercises, proofs, etc.)
- ✅ Automatically optimize content completeness

### 🔧 Content Management
- ✅ Intelligent task distribution to appropriate Agents
- ✅ Support parallel management of multiple notebooks
- ✅ Automatic saving and version management

### 🎯 Content Optimization
- ✅ Automatically identify question types and supplement missing content
- ✅ Optimize proof steps, supplement intermediate processes
- ✅ Improve overall note quality

### 💬 Interactive Modification
- ✅ Modify note content in natural language
- ✅ Support adding, deleting, and modifying various content types
- ✅ Real-time updates and saving

## 📊 System Advantages

1. **Intelligent**: AI Agents automatically understand user intent and select optimal processing strategies
2. **Modular**: Clear architectural design, easy to extend and maintain
3. **User-Friendly**: Natural language interaction, no need to learn complex operations
4. **High Quality**: Automatic optimization and supplementation ensure note completeness
5. **Extensible**: Plugin-based design, easy to add new features

## 🔮 Future Plans

- [ ] Support more file formats (PDF, PPT, etc.)
- [ ] Multi-language support
- [ ] Collaboration features (multi-user editing)
- [ ] Note template system
- [ ] Knowledge graph visualization

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

## 📄 License

[Add license information]

## 👥 Contributors

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

**Let AI be your learning assistant, making note generation simple and efficient!** 🚀

