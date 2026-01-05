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

## 进阶开发资源

探索 Claude 与 Agent 开发的高级工具与生态：

*   **SkillsMP**
    *   ⭐⭐⭐⭐⭐
    *   [skillsmp.com](https://skillsmp.com/)
    *   **描述**: Agent Skills 聚合市场，提供大量兼容 Claude Code、Codex 和 ChatGPT 的技能包，扩展智能体能力。

*   **Claude 4.5 Opus Soul Document**
    *   ⭐⭐⭐⭐⭐
    *   [阅读文档 (Gist)](https://gist.github.com/Richard-Weiss/efe157692991535403bd7e7fb20b6695)
    *   **描述**: 深度解析 Claude "灵魂"与核心价值观，编写符合 Claude 行为模式 Prompt 的必读材料。

*   **Ralph for Claude Code**
    *   ⭐⭐⭐⭐½
    *   [GitHub 仓库](https://github.com/frankbria/ralph-claude-code)
    *   **描述**: 专为 Claude Code 设计的自主开发循环 (Autonomous Development Loop)，支持智能退出检测。

*   **Vibe to Prod**
    *   ⭐⭐⭐⭐½
    *   [GitHub 仓库](https://github.com/muyen/vibe-to-prod)
    *   **描述**: 生产级全栈开发模版，主打 AI 原生工作流 (Vibecoding)，加速开发周期。

*   **ClaudeKit Skills**
    *   ⭐⭐⭐⭐
    *   [GitHub 仓库](https://github.com/mrgoonie/claudekit-skills)
    *   **描述**: ClaudeKit 核心技能集合，包含 MCP 管理等实用工具，适合深度定制。
