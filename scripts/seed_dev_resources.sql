-- Initial data for dev_resources table

INSERT INTO public.dev_resources (title, description, url, github_url, category, tags, language, license, logo_url, is_featured) VALUES
-- Agent Frameworks
('AutoGen', 'A framework that enables the development of LLM applications using multiple agents that can converse with each other to solve tasks.', 'https://microsoft.github.io/autogen/', 'https://github.com/microsoft/autogen', 'Agent Frameworks', ARRAY['Multi-Agent', 'Microsoft', 'Python'], 'Python', 'MIT', 'https://microsoft.github.io/autogen/img/autogen_logo.png', true),
('LangGraph', 'Build language agents as graphs.', 'https://python.langchain.com/docs/langgraph', 'https://github.com/langchain-ai/langgraph', 'Agent Frameworks', ARRAY['LangChain', 'Graph', 'Stateful'], 'Python', 'MIT', 'https://avatars.githubusercontent.com/u/126733545?s=200&v=4', true),
('CrewAI', 'Framework for orchestrating role-playing, autonomous AI agents.', 'https://www.crewai.com/', 'https://github.com/joaomdmoura/crewAI', 'Agent Frameworks', ARRAY['Role-Playing', 'Orchestration'], 'Python', 'MIT', 'https://www.crewai.com/favicon.ico', true),
('BabyAGI', 'An AI-powered task management system.', 'https://github.com/yoheinakajima/babyagi', 'https://github.com/yoheinakajima/babyagi', 'Agent Frameworks', ARRAY['Autonomous', 'Task Management'], 'Python', 'MIT', 'https://github.com/yoheinakajima/babyagi/raw/main/docs/babyagi-logo.png', false),

-- Skills & MCP
('Model Context Protocol', 'An open standard for connecting AI assistants to systems and data.', 'https://modelcontextprotocol.io/', 'https://github.com/modelcontextprotocol', 'Skills & MCP', ARRAY['Standard', 'Protocol', 'Anthropic'], 'Spec', 'MIT', 'https://modelcontextprotocol.io/images/favicon.ico', true),
('LangChain Community', 'Community contributed integrations for LangChain.', 'https://python.langchain.com/', 'https://github.com/langchain-ai/langchain', 'Skills & MCP', ARRAY['Integrations', 'Tools'], 'Python', 'MIT', 'https://python.langchain.com/img/favicon.ico', false),

-- Dev Tools
('LangSmith', 'Platform for debugging, testing, evaluating, and monitoring LLM applications.', 'https://www.langchain.com/langsmith', '', 'Dev Tools', ARRAY['Observability', 'Evaluation'], 'SaaS', 'Proprietary', 'https://www.langchain.com/favicon.ico', true),
('Vercel AI SDK', 'The TypeScript Toolkit for building AI applications.', 'https://sdk.vercel.ai/docs', 'https://github.com/vercel/ai', 'Dev Tools', ARRAY['TypeScript', 'React', 'Next.js'], 'TypeScript', 'Apache-2.0', 'https://assets.vercel.com/image/upload/front/favicon/vercel/favicon.ico', true),
('Pezzo', 'Open-source LLMOps platform to manage prompts and monitor AI usage.', 'https://pezzo.ai/', 'https://github.com/pezzolabs/pezzo', 'Dev Tools', ARRAY['LLMOps', 'Prompt Management'], 'TypeScript', 'Apache-2.0', 'https://pezzo.ai/favicon.ico', false),

-- Prompt Engineering
('DSPy', 'Programming—not prompting—foundation models.', 'https://dspy-docs.vercel.app/', 'https://github.com/stanfordnlp/dspy', 'Prompt Engineering', ARRAY['Optimization', 'Stanford'], 'Python', 'MIT', 'https://dspy-docs.vercel.app/img/dspy_logo.png', true),
('Instructor', 'Structured outputs for LLMs.', 'https://python.useinstructor.com/', 'https://github.com/jxnl/instructor', 'Prompt Engineering', ARRAY['Structured Output', 'Pydantic'], 'Python', 'MIT', 'https://python.useinstructor.com/favicon.ico', true),

-- Workflow
('n8n', 'Fair-code workflow automation tool with native AI capabilities.', 'https://n8n.io/', 'https://github.com/n8n-io/n8n', 'Workflow', ARRAY['Low-Code', 'Automation'], 'TypeScript', 'Fair-code', 'https://n8n.io/favicon.ico', true),
('Flowise', 'Drag & drop UI to build your customized LLM flow.', 'https://flowiseai.com/', 'https://github.com/FlowiseAI/Flowise', 'Workflow', ARRAY['No-Code', 'LangChain'], 'TypeScript', 'Apache-2.0', 'https://flowiseai.com/favicon.ico', true),

-- Docs & Specs
('OpenAI API', 'Documentation for OpenAI API.', 'https://platform.openai.com/docs', '', 'Docs & Specs', ARRAY['API', 'Reference'], 'Docs', '', 'https://openai.com/favicon.ico', false),
('Anthropic API', 'Documentation for Claude and Anthropic API.', 'https://docs.anthropic.com/', '', 'Docs & Specs', ARRAY['API', 'Reference'], 'Docs', '', 'https://www.anthropic.com/favicon.ico', false);
