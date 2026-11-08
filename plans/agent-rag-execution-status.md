# 订阅计划执行状态

最后更新：2026-11-01。实施进行中；未迁移或修改线上数据库，未改变线上工作流。

## 基线

- 已用 ViteMind 配置的项目 `axbsjwawwgejesrqywwd` 的现有服务端凭据执行只读备份，`rss_feeds` 18 条、全部启用；`news` 14,456 条。备份在 Git 忽略目录 `output/news-review/baseline-2026-11-01/`，权限为仅当前用户可读写。备份是 Data API 导出，不包含数据库 schema、Auth、RLS 或 Storage；迁移前仍须获得真正的数据库备份和配置。
- 当前静态 JSON 100 条，其中 22 条链接不在上述数据库备份中。切换首页数据源之前必须比对、合并并验证这些差异，不能用数据库直接覆盖快照。列表可能在备份后变化，迁移时重新盘点。
- Supabase 管理插件现已切换到 ViteMind 项目 `axbsjwawwgejesrqywwd`。只读 SQL 再次确认 `rss_feeds` 18 条且全部启用，`news` 14,456 条。生产环境没有执行任何写入。
- 已核查现有 RLS：`news` 和 `rss_feeds` 的写入策略对已认证用户过宽；用户已确认 Auth 当前唯一的已验证账号是管理员。新增管理功能需按该账号的用户 ID 授权，不能将所有认证用户视为管理员。
- 2026-11-01 GitHub API 验证了 LangGraph、LlamaIndex、Haystack 的 release 列表；OpenAI Cookbook 和 Claude Cookbooks 未提供 release，示例文件目录可读取。教程需以实际内容变更为单位，不把普通 commit 直接作为文章。

## 本地进行中

- `scripts/news_sources.py`：新增 GitHub Release、Cookbook 文件变更和 RSS 适配器，统一来源/条目标识及发布时间、更新时间、首次发现时间；RSS 保持原来源关键词过滤。隔离来源级失败；全失败不会伪装成空结果，并保留各来源失败原因。GitHub 跳过草稿和预发布，校验分页链接、限制页数。Cookbook 文件仅建议归为教程，正文确认前不认定为实操教程。
- 新采集适配器已改用 `scripts/news_http.py`，基于固定版本 `microsoft-antissrf==1.0.0` 的 DNS 地址绑定，禁用代理、逐跳验证重定向并限制响应体。依赖单独记录在 `scripts/requirements-news-security.txt`；旧工作流尚未切换。原 `safe_get` 只在连接前检查 DNS，仍被旧工作流使用，不能声称其具有 DNS 重绑定防护。
- `scripts/news_rules.py`：新增纯函数，提供按类型的字面屏蔽词、时间窗口和自动发布数量选择规则。注意：这些只是规则模块，尚未连接持久化、完整校验或线上发布，不能直接用作发布授权。
- `scripts/news_pipeline.py`：把去重、屏蔽、时效、内容类型、受信任校验标记、审核模式与每日限额组合成候选处理结果，保留被拦截的条目及原因；结果只用于后续持久化，发布时仍须在数据库事务中重查设置和限额。未接入现有工作流。
- `scripts/news_runner.py`：使用可替换的存储、原文校验和模型接口，把新候选先保存为待审核，再进行筛选；已有候选不会因为开关变更被重复导入，模型故障或遗漏会保留原始候选。`scripts/news_store.py` 已实现 Supabase 存储适配器，数据库接口通过导入令牌和修订号防止覆盖管理员并发修改；尚未在真实 Supabase 中联调，也未接入现有采集任务。
- `scripts/news_model_output.py`：检查模型输出的候选 ID、字段、来源链接和时间；模型不能自改来源日期或链接，未核实实操证据的教程建议保留为待分类。这些检查不等于事实核验，尚未接入模型调用。
- 已用 Supabase CLI 创建 `supabase/migrations/20261101074245_news_subscription_foundation.sql`，仅新增管理权限、设置、规则、候选、来源和公开新闻等基础表；没有对生产项目执行。管理员账号仍需迁移时以用户 ID 安全初始化。设置和关键词的变更记录由数据库触发器写入，客户端不能直接写入记录。
- 迁移草稿包含批量发布事务：区分服务端自动发布和管理员手动发布，重查审核开关、屏蔽词、来源校验、时间、重复、每日总量及观点数量；设置行锁用于串行化并发发布及规则变更。真实 Supabase 的 API 角色及客户端调用仍需集成验证，未接入现有工作流。
- `NewsSettings.vue` 已实现审核开关和分类型屏蔽词界面，并在读取设置前查询管理员身份；组件尚未挂入菜单，避免线上尚未部署时显示失效功能。
- 现有 RSS 管理页面新增“获取方式”列，明确旧分类与 RSS 获取方式不同；不改变源数据。精确重复候选会标记并保留来源记录；RSS 无数据库 ID 时使用 URL 摘要作为标识，避免在标识中暴露 URL 内的密钥。
- 上述模块尚未替换现有 `scripts/generate_news.py` 和 Actions；现有系统仍按原来的待审核 Artifact 运行。数据库审核开关、来源管理、发布事务、页面和历史迁移仍未实现。

## 验证及阻碍

- 安全依赖临时虚拟环境中的 51 项新增测试通过，包括实际库的内网阻断、DNS 地址绑定和 TLS 主机名检查；`npm run docs:build` 通过。完整 Python 测试此前有 2 项依赖外网 DNS 的既有 SSRF 测试因运行环境无法解析域名而失败；不能据此判定线上网络可用性。
- 本机 GitHub 域名解析为代理的假地址，安全库按策略拒绝连接；没有放宽策略。已验证安全库行为，但尚不能证明无代理的真实网络请求或 GitHub Actions 可以成功。
- 使用 Docker 中独立的 PostgreSQL 17.6 模拟 Supabase 角色与 `auth.uid()`，迁移 SQL、默认设置、历史表保留、匿名/普通用户/管理员权限、设置审计、发布事务、批次回滚和一次并发额度测试通过。它不等同完整 Supabase 集成测试；历史导入、现有策略修订和端到端验证仍未完成。数据库中的关键词使用 PostgreSQL `lower`，与 Python `casefold` 对部分 Unicode 字符的结果可能不同，需统一匹配语义后才能上线。
- 仅有 Data API 导出不能代替完整备份，生产迁移前仍须核实备份与恢复方法。

## 外链抓取方案调研

- 2026-11-01 查询 [Microsoft AntiSSRF](https://github.com/microsoft/AntiSSRF)：MIT，仓库未归档，最近推送 2026-10-21；Python 发布包 1.0.0 的连接适配器将校验后的 IP 用于连接，并保留原域名用于 TLS。需要 requests 2.34.2 和 urllib3 2.7.0。使用其库而非复制实现，未做完整安全审计。
- 对比 [ssrf-safe-fetch](https://github.com/tommypj/ssrf-safe-fetch)：MIT，2026-06-23 最近推送，仓库当时只有一次提交；[Champion](https://github.com/Gee19/champion) 显示许可证无法通过 SPDX 自动识别，最近推送 2026-05-31。两者暂不采用。
