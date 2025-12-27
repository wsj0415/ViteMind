# Claude AI 资源指南

Claude 是由 Anthropic 开发的先进 AI 模型，以其安全性、长上下文窗口和卓越的编码能力而闻名。

## 官方资源

- **官方网站**: [anthropic.com](https://www.anthropic.com)
- **Claude.ai (Web Chat)**: [claude.ai](https://claude.ai)
- **开发者控制台**: [console.anthropic.com](https://console.anthropic.com)
- **API 文档**: [docs.anthropic.com](https://docs.anthropic.com)
- **Prompt Engineering Guide**: [docs.anthropic.com/claude/docs/prompt-engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- **Anthropic Cookbook**: [github.com/anthropic/anthropic-cookbook](https://github.com/anthropic/anthropic-cookbook)

## 模型概览

| 模型 | 特点 | 适用场景 |
| :--- | :--- | :--- |
| **Claude 3.5 Sonnet** | 速度与智能的最佳平衡，编码能力极强 | 复杂任务、代码生成、数据分析 |
| **Claude 3 Opus** | 最强推理能力，擅长处理极其复杂的任务 | 深度研究、创意写作、复杂策略规划 |
| **Claude 3 Haiku** | 极速、低成本 | 实时交互、简单任务、大量数据处理 |

## 常用工具

- **Claude Workbench**: 在控制台中测试和优化 Prompt。
- **Artifacts**: 在 Claude.ai 中生成和预览代码、文档、图表的功能。

## 最佳实践

1. **利用 XML 标签**: Claude 非常擅长解析 XML 结构的 Prompt，使用 `<instruction>`, `<example>` 等标签可以显著提高效果。
2. **长上下文**: 利用其 200k+ 的上下文窗口，可以一次性输入整本书或整个代码库进行分析。
3. **Chain of Thought**: 引导 Claude "一步步思考" (Let's think step by step) 以处理复杂逻辑。
