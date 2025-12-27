# OpenAI 资源指南

OpenAI 是生成式 AI 领域的先驱，开发了 GPT 系列模型和 DALL·E 图像生成模型。

## 官方资源

- **OpenAI Platform**: [platform.openai.com](https://platform.openai.com)
- **ChatGPT**: [chatgpt.com](https://chatgpt.com)
- **API 文档**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **OpenAI Cookbook**: [github.com/openai/openai-cookbook](https://github.com/openai/openai-cookbook) - 包含大量示例代码。
- **Research Blog**: [openai.com/research](https://openai.com/research)

## 模型概览

| 模型 | 特点 | 适用场景 |
| :--- | :--- | :--- |
| **GPT-4o** | 全能旗舰，多模态，速度快 | 复杂对话、视觉任务、通用助手 |
| **OpenAI o1 (Preview)** | 强化推理能力，擅长 STEM 领域 | 数学、编程、科学推理 |
| **GPT-4o mini** | 经济高效，替代 GPT-3.5 | 简单任务、聊天机器人、低成本应用 |
| **DALL·E 3** | 顶尖的图像生成模型 | 创意绘图、设计素材生成 |

## 开发工具

- **Playground**: 在网页端测试不同的模型参数和 Prompt。
- **Assistants API**: 构建拥有记忆、工具使用（Code Interpreter, File Search）能力的智能体。
- **Fine-tuning**: 对模型进行微调以适应特定任务或风格。

## 最佳实践

1. **明确指令**: 给出的指令越具体，模型表现越好。
2. **提供示例 (Few-Shot)**: 在 Prompt 中提供几个输入输出示例，能显著提升准确性。
3. **拆分任务**: 将复杂任务拆解为多个简单的子任务。
4. **使用工具**: 利用 Function Calling 让模型连接外部数据和 API。
