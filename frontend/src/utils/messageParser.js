/**
 * Message parsing utilities
 */

/**
 * Parse notebook creation info from a message
 * @param {string} message - Message content
 * @returns {{notebookId: string, notebookTitle: string} | null}
 */
export function parseNotebookCreationInfo(message) {
  // 首先尝试解析 JSON 格式的结构化数据（后端返回的格式）
  try {
    // 尝试解析整个消息为 JSON
    const jsonData = JSON.parse(message.trim())
    if (jsonData.status === 'success' && jsonData.notebook_id && jsonData.notebook_title) {
      return {
        notebookId: jsonData.notebook_id,
        notebookTitle: jsonData.notebook_title,
      }
    }
  } catch (e) {
    // 不是 JSON，继续尝试其他方式
  }
  
  // 尝试从消息中提取 JSON 对象（可能消息包含其他文本 + JSON）
  try {
    // 匹配包含 notebook_id 和 notebook_title 的 JSON 对象
    const jsonMatch = message.match(/\{[\s\S]*"notebook_id"[\s\S]*"notebook_title"[\s\S]*\}/)
    if (jsonMatch) {
      const jsonData = JSON.parse(jsonMatch[0])
      // 必须同时满足：status 为 success，且有 notebook_id 和 notebook_title
      if (jsonData.status === 'success' && jsonData.notebook_id && jsonData.notebook_title) {
        return {
          notebookId: jsonData.notebook_id,
          notebookTitle: jsonData.notebook_title,
        }
      }
    }
  } catch (e) {
    // JSON 解析失败
  }
  
  // 后备方案：尝试从文本格式中提取（Agent 可能把 JSON 转换成了文本）
  // 匹配格式：ID: xxx 和 标题: xxx
  try {
    // 匹配 "ID: " 或 "ID：" 后面的 UUID 或短 ID
    const idMatch = message.match(/ID[：:]\s*([a-f0-9\-]+)/i)
    // 匹配 "标题: " 或 "标题：" 后面的内容（到换行或下一个字段为止）
    const titleMatch = message.match(/标题[：:]\s*([^\n\r]+)/i)
    
    if (idMatch && titleMatch) {
      const notebookId = idMatch[1].trim()
      const notebookTitle = titleMatch[1].trim()
      
      // 验证 ID 格式（UUID 或短 ID）
      if (notebookId && notebookTitle && (notebookId.length >= 8 || notebookId.includes('-'))) {
        return {
          notebookId: notebookId,
          notebookTitle: notebookTitle,
        }
      }
    }
  } catch (e) {
    // 文本解析失败
  }
  
  // 如果都失败了，返回 null
  return null
}

/**
 * Parse outline from a message
 * @param {string} message - Message content
 * @returns {{notebook_title: string, notebook_description: string, outlines: object} | null}
 */
export function parseOutlineFromMessage(message) {
  // 检测是否包含大纲确认标记
  if (!message.includes('📋') && !message.includes('大纲已生成')) {
    return null
  }

  try {
    // 尝试从markdown格式的消息中提取大纲
    // 匹配 "**标题**：{title}" 或 "**标题**：{title}"
    const titleMatch = message.match(/\*\*标题\*\*[：:]\s*(.+?)(?:\n|$)/m)
    if (!titleMatch) {
      return null
    }

    const notebook_title = titleMatch[1].trim()
    
    // 匹配描述（可能在标题之后，章节之前）
    const descMatch = message.match(/\*\*描述\*\*[：:]\s*([\s\S]+?)(?:\*\*章节\*\*|\n\*\*\d+\.|请确认|$)/m)
    const notebook_description = descMatch ? descMatch[1].trim() : ''
    
    // 解析章节 - 匹配 "**1. 章节名**\n描述内容" 格式
    const outlines = {}
    // 先找到章节部分
    const sectionsStart = message.indexOf('**章节**')
    if (sectionsStart >= 0) {
      const sectionsText = message.substring(sectionsStart)
      // 匹配 "**数字. 章节名**\n描述"（描述可能有多行，直到下一个**数字.或结尾）
      const sectionRegex = /\*\*(\d+)\.\s*(.+?)\*\*\s*\n([\s\S]*?)(?=\n\*\*\d+\.|请确认|$)/g
      let match
      while ((match = sectionRegex.exec(sectionsText)) !== null) {
        const title = match[2].trim()
        let description = match[3].trim()
        // 移除末尾的省略号（如果有）
        description = description.replace(/\.\.\.\s*$/, '').trim()
        if (title && description) {
          outlines[title] = description
        }
      }
    }

    if (Object.keys(outlines).length === 0) {
      return null
    }

    return {
      notebook_title,
      notebook_description,
      outlines,
    }
  } catch (err) {
    console.error('Failed to parse outline:', err)
    return null
  }
}

