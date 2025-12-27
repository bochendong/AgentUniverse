# 公共 Prompt 片段使用指南

本文档说明如何使用公共 prompt 片段来避免重复代码。

## 📋 可用的片段

### 1. 题目类型要求
- **变量名**：`QUESTION_TYPE_REQUIREMENTS`
- **用途**：说明5种题目类型的要求
- **使用场景**：SectionCreator、ModifyAgent、RefinementAgent

### 2. 证明质量要求
- **变量名**：`PROOF_QUALITY_REQUIREMENTS`
- **用途**：说明证明的质量标准
- **使用场景**：SectionCreator、ProofRefinementAgent

### 3. LaTeX 格式要求
- **变量名**：`LATEX_FORMAT_REQUIREMENTS`
- **用途**：说明 LaTeX 公式的格式要求
- **使用场景**：所有涉及数学公式的 Agent

### 4. 代码和数学公式格式要求
- **变量名**：`CODE_AND_MATH_FORMAT_REQUIREMENTS`
- **用途**：说明代码和数学公式的格式要求
- **使用场景**：SectionCreator

### 5. Section 输出结构说明
- **变量名**：`SECTION_OUTPUT_STRUCTURE`
- **用途**：说明 Section 对象的结构
- **使用场景**：SectionCreator

### 6. 选择题优化要求
- **变量名**：`MULTIPLE_CHOICE_REQUIREMENTS`
- **用途**：说明选择题的优化要求
- **使用场景**：ExerciseRefinementAgent

### 7. 填空题优化要求
- **变量名**：`FILL_BLANK_REQUIREMENTS`
- **用途**：说明填空题的优化要求
- **使用场景**：ExerciseRefinementAgent

### 8. 证明题优化要求
- **变量名**：`PROOF_EXERCISE_REQUIREMENTS`
- **用途**：说明证明题的优化要求
- **使用场景**：ExerciseRefinementAgent

### 9. 简答题优化要求
- **变量名**：`SHORT_ANSWER_REQUIREMENTS`
- **用途**：说明简答题的优化要求
- **使用场景**：ExerciseRefinementAgent

### 10. 题目类型识别说明
- **变量名**：`QUESTION_TYPE_IDENTIFICATION`
- **用途**：说明如何识别题目类型
- **使用场景**：ExerciseRefinementAgent

### 11. Concept Blocks 基本要求（通用）
- **变量名**：`CONCEPT_BLOCKS_BASIC_REQUIREMENTS`
- **用途**：说明 concept_blocks 的基本要求（所有场景都需要）
- **使用场景**：所有 Section Creator（WellFormedNoteSectionCreator 等）

### 12. Concept Blocks 详细要求（从零创建场景专用）
- **变量名**：`CONCEPT_BLOCKS_DETAILED_REQUIREMENTS_FROM_SCRATCH`
- **用途**：说明 concept_blocks 的详细要求（从零创建场景）
- **使用场景**：FromScratchSectionCreator
- **注意**：这个要求比基本要求更严格，强调"必须为每个核心概念创建"、"必须关联 examples"等

### 13. Exercises 详细要求（从零创建场景专用）
- **变量名**：`EXERCISES_DETAILED_REQUIREMENTS_FROM_SCRATCH`
- **用途**：说明 exercises 的多样化要求（从零创建场景）
- **使用场景**：FromScratchSectionCreator
- **注意**：这个要求强调"必须多样化"、"必须包含各种类型"，主要适用于从零创建场景


## 🔧 使用方法

### 示例 1：在 SectionCreator 中使用

```python
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_REQUIREMENTS,
    PROOF_QUALITY_REQUIREMENTS,
    CODE_AND_MATH_FORMAT_REQUIREMENTS,
    SECTION_OUTPUT_STRUCTURE
)

instructions = f"""
你是一个专业的教育内容创作者。

{SECTION_OUTPUT_STRUCTURE}

{QUESTION_TYPE_REQUIREMENTS}

{PROOF_QUALITY_REQUIREMENTS}

{CODE_AND_MATH_FORMAT_REQUIREMENTS}
"""
```

### 示例 2：在 RefinementAgent 中使用

```python
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_IDENTIFICATION,
    MULTIPLE_CHOICE_REQUIREMENTS,
    FILL_BLANK_REQUIREMENTS,
    PROOF_EXERCISE_REQUIREMENTS,
    SHORT_ANSWER_REQUIREMENTS
)

instructions = f"""
你是一个专业的题目整理和优化专家。

{QUESTION_TYPE_IDENTIFICATION}

{MULTIPLE_CHOICE_REQUIREMENTS}

{FILL_BLANK_REQUIREMENTS}

{PROOF_EXERCISE_REQUIREMENTS}

{SHORT_ANSWER_REQUIREMENTS}
"""
```

### 示例 3：在 ModifyAgent 中使用

```python
from backend.prompts.common_prompt_snippets import (
    QUESTION_TYPE_REQUIREMENTS
)

instructions = f"""
你是专门负责修改练习题的Agent。

{QUESTION_TYPE_REQUIREMENTS}

支持的操作：
- 修改现有exercise的question、answer、explanation等字段
- 生成新的exercise（支持5种题目类型）
"""
```

## 📝 重构步骤

1. **识别重复片段**：在多个文件中找到相同的 prompt 内容
2. **提取到公共文件**：添加到 `common_prompt_snippets.py`
3. **替换原文件**：在原文件中 import 并使用
4. **测试验证**：确保功能正常

## ⚠️ 注意事项

1. **保持一致性**：所有使用相同片段的地方应该保持一致
2. **版本控制**：修改片段时，要考虑对所有使用该片段的地方的影响
3. **文档更新**：修改片段时，更新本文档说明

