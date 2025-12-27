# Google Gemini 资源指南

Gemini 是 Google DeepMind 开发的最强多模态 AI 模型系列，原生支持文本、图像、音频和视频理解。

## 官方资源

- **Google AI Studio**: [aistudio.google.com](https://aistudio.google.com) - 快速构建和测试 Gemini 应用。
- **Gemini 官网**: [deepmind.google/technologies/gemini](https://deepmind.google/technologies/gemini)
- **API 文档**: [ai.google.dev/docs](https://ai.google.dev/docs)
- **Google DeepMind Blog**: [deepmind.google/discover/blog](https://deepmind.google/discover/blog)

## 模型概览

| 模型 | 特点 | 适用场景 |
| :--- | :--- | :--- |
| **Gemini 1.5 Pro** | 强大的推理能力，支持超长上下文 (1M/2M tokens) | 复杂多模态任务、长文档分析、视频理解 |
| **Gemini 1.5 Flash** | 极速、低延迟、高性价比 | 高频任务、实时应用、大规模数据提取 |
| **Gemini Ultra** | 最强性能，处理高度复杂的任务 | 科学研究、深度推理 |

## 开发工具

- **Vertex AI**: 企业级 AI 开发平台，集成 Gemini 模型。
- **Firebase Genkit**: 适用于 JavaScript/TypeScript 开发者的 AI 框架。
- **Project IDX**: Google 的云端 AI 辅助开发环境。

## 最佳实践

1. **多模态输入**: 充分利用 Gemini 的原生多模态能力，混合输入文本、图片和视频进行提问。
2. **长上下文利用**: 1.5 Pro 支持百万级 Token，可以直接上传整个代码库或长视频进行检索和问答。
3. **System Instructions**: 在 AI Studio 中设置系统指令，定义模型的角色和行为规范。
