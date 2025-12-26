---
description: 将当前会话转换为可重用的 workflow
---

请分析当前会话的历史记录，提取关键步骤，并将其转换为一个新的 Antigravity workflow 文件。

1.  **分析历史记录**：回顾当前会话的所有交互，识别用户意图和关键操作步骤。忽略闲聊、错误尝试和无关信息。
2.  **提取步骤**：将关键操作总结为清晰、可执行的步骤。
3.  **生成 Workflow 内容**：
    *   创建一个包含 YAML frontmatter 的 Markdown 内容。
    *   `description` 应该是对该 workflow 功能的简短描述。
    *   正文部分应包含具体的步骤说明。
4.  **询问文件名**：询问用户希望将此 workflow 命名为什么（例如 `deploy_app.md`）。
5.  **保存文件**：使用 `write_to_file` 工具将生成的内容保存到 `.agent/workflows/<用户提供的文件名>`。

**示例输出格式**：

```markdown
---
description: [Workflow 描述]
---
[步骤 1]
[步骤 2]
...
```

请现在开始分析并询问我文件名。
