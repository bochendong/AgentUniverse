# Export Notebook Scripts

这个文件夹包含所有用于导出笔记本的脚本和导出的文件。

## 脚本文件

- `export_notebook.py` - 主要的导出脚本（支持 API 和直接数据库访问）
- `export_notebook_simple.py` - 简化版导出脚本（仅直接数据库访问）
- `export_notebook_via_api.py` - 通过 API 导出的脚本
- `export_notebook_group_theory.py` - 群论笔记本导出脚本（示例）
- `export_notebook_group_theory_api.py` - 群论笔记本导出脚本（API 版本）

## 导出的文件

所有导出的 Markdown 文件也会保存在这个文件夹中。

## 使用方法

```bash
# 使用简化版脚本（推荐）
python export/export_notebook_simple.py <notebook_id>

# 使用完整版脚本
python export/export_notebook.py <notebook_id>
```


