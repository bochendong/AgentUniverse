# Prompt 片段重构指南

本文档说明如何重构 Agent 的 prompt，使用公共片段避免重复代码。

## 📋 问题背景

在 `agent_as_tools` 中，很多 Agent 的 prompt 有大量重复内容：
- 题目类型要求（5种类型）
- 证明质量要求
- LaTeX 格式要求
- 代码和数学公式格式要求
- Section 输出结构说明

这些重复内容导致：
- 维护成本高：修改时需要改多个文件
- 容易不一致：不同文件中的描述可能略有差异
- 代码冗余：大量重复的 prompt 文本

## ✅ 解决方案

创建公共 prompt 片段文件：`backend/prompts/common_prompt_snippets.py`

### 可用的片段

| 片段名称 | 变量名 | 用途 |
|---------|--------|------|
| 题目类型要求 | `QUESTION_TYPE_REQUIREMENTS` | 说明5种题目类型的要求 |
| 证明质量要求 | `PROOF_QUALITY_REQUIREMENTS` | 说明证明的质量标准 |
| LaTeX 格式要求 | `LATEX_FORMAT_REQUIREMENTS` | 说明 LaTeX 公式的格式要求 |
| 代码和数学公式格式要求 | `CODE_AND_MATH_FORMAT_REQUIREMENTS` | 说明代码和数学公式的格式要求 |
| Section 输出结构说明 | `SECTION_OUTPUT_STRUCTURE` | 说明 Section 对象的结构 |
| 选择题优化要求 | `MULTIPLE_CHOICE_REQUIREMENTS` | 说明选择题的优化要求 |
| 填空题优化要求 | `FILL_BLANK_REQUIREMENTS` | 说明填空题的优化要求 |
| 证明题优化要求 | `PROOF_EXERCISE_REQUIREMENTS` | 说明证明题的优化要求 |
| 简答题优化要求 | `SHORT_ANSWER_REQUIREMENTS` | 说明简答题的优化要求 |
| 题目类型识别说明 | `QUESTION_TYPE_IDENTIFICATION` | 说明如何识别题目类型 |

## 🔧 使用方法

### 步骤 1：导入公共片段

```python
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_REQUIREMENTS,
    PROOF_QUALITY_REQUIREMENTS,
    CODE_AND_MATH_FORMAT_REQUIREMENTS,
    SECTION_OUTPUT_STRUCTURE
)
```

### 步骤 2：在 instructions 中使用

```python
instructions = f"""
你是一个专业的教育内容创作者。

{SECTION_OUTPUT_STRUCTURE}

{QUESTION_TYPE_REQUIREMENTS}

{PROOF_QUALITY_REQUIREMENTS}

{CODE_AND_MATH_FORMAT_REQUIREMENTS}
"""
```

## 📝 重构示例

### 示例 1：重构 FromScratchSectionCreator

**重构前**：
```python
instructions = f"""
...
**代码和数学公式格式要求（重要）**：
- **代码块**：所有代码必须使用 Markdown 代码块格式
  - 行内代码：使用反引号包裹，如 `code`
  - 代码块：使用三个反引号包裹，并指定语言
- **数学公式**：所有数学公式必须使用 LaTeX 格式
  - **行内公式**：使用单个美元符号包裹，格式为 `$公式内容$`
  - **块级公式**：使用两个美元符号包裹，格式为 `$$公式内容$$`
  - **重要规则**：所有数学符号、变量、集合等都必须在公式标记内

**题目类型要求（examples 和 exercises 都必须使用以下5种类型之一）**

1. **选择题 (multiple_choice)**：...
2. **填空题 (fill_blank)**：...
...

**证明质量要求（重要，必须严格遵守）**：
- 所有proof必须包含详细的中间步骤...
...
"""
```

**重构后**：
```python
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_REQUIREMENTS,
    PROOF_QUALITY_REQUIREMENTS,
    CODE_AND_MATH_FORMAT_REQUIREMENTS
)

instructions = f"""
...
{CODE_AND_MATH_FORMAT_REQUIREMENTS}

{QUESTION_TYPE_REQUIREMENTS}

{PROOF_QUALITY_REQUIREMENTS}
"""
```

### 示例 2：重构 ExerciseRefinementAgent

**重构前**：
```python
instructions = f"""
...
1. **题目类型识别**：
   - 如果question_type为null，根据question内容智能识别类型
   - 选择题关键词："下列哪个"、"哪个是"、"选择"、"Which of the following"等
   ...

2. **选择题优化**（question_type = "multiple_choice"）：
   - **必须**包含4个选项（options字段）
   ...
"""
```

**重构后**：
```python
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_IDENTIFICATION,
    MULTIPLE_CHOICE_REQUIREMENTS,
    FILL_BLANK_REQUIREMENTS,
    PROOF_EXERCISE_REQUIREMENTS,
    SHORT_ANSWER_REQUIREMENTS
)

instructions = f"""
...
{QUESTION_TYPE_IDENTIFICATION}

{MULTIPLE_CHOICE_REQUIREMENTS}

{FILL_BLANK_REQUIREMENTS}

{PROOF_EXERCISE_REQUIREMENTS}

{SHORT_ANSWER_REQUIREMENTS}
"""
```

## 📋 需要重构的文件列表

### Section Creators
- [ ] `backend/tools/agent_as_tools/section_creators/from_scratch.py`
- [ ] `backend/tools/agent_as_tools/section_creators/well_formed_note.py`
- [ ] `backend/tools/agent_as_tools/section_creators/paper.py`

### Refinement Agents
- [ ] `backend/tools/agent_as_tools/refinement_agents/exercise.py`
- [ ] `backend/tools/agent_as_tools/refinement_agents/proof.py`

### Modify Agents
- [ ] `backend/tools/agent_as_tools/modify_agents/exercise.py`
- [ ] `backend/tools/agent_as_tools/modify_agents/definition.py`
- [ ] `backend/tools/agent_as_tools/modify_agents/introduction.py`
- [ ] `backend/tools/agent_as_tools/modify_agents/summary.py`

## 🔄 重构步骤

1. **识别重复片段**：在文件中找到重复的 prompt 内容
2. **查找对应片段**：在 `common_prompt_snippets.py` 中找到对应的片段
3. **导入片段**：在文件顶部添加 import 语句
4. **替换内容**：用片段变量替换重复的 prompt 文本
5. **测试验证**：确保功能正常

## ⚠️ 注意事项

1. **保持格式一致**：片段中的格式（如缩进、换行）应该与使用场景匹配
2. **上下文相关**：某些片段可能需要根据上下文调整，可以在片段前后添加说明
3. **版本控制**：修改片段时，要考虑对所有使用该片段的地方的影响
4. **测试覆盖**：重构后需要测试所有使用该 Agent 的场景

## 💡 最佳实践

1. **逐步重构**：一次重构一个文件，确保功能正常后再继续
2. **保留注释**：在替换的地方添加注释，说明使用了哪个片段
3. **文档更新**：如果添加新的片段，更新 `common_prompt_snippets.md`
4. **代码审查**：重构后进行代码审查，确保没有遗漏

## 🎯 重构的好处

1. **减少重复**：prompt 内容只在一个地方维护
2. **统一标准**：所有 Agent 使用相同的标准描述
3. **易于修改**：修改时只需要改一处
4. **提高可读性**：instructions 更简洁，重点更突出

