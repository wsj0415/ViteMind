# 新闻质量审核

Daily AI News 每天 08:00（北京时间）生成待审核草稿，不再自动发布。GitHub Actions 运行页面的 Artifacts 中下载 `news-review-<run id>`，解压得到 `draft.json`。Artifacts 保留 14 天；为空表示本次没有选出内容。

## 审核

逐条核对 `source_excerpt` 和原文链接：事实、数字、时间、结论是否有依据；关注选题价值、重复、夸大和传闻。`source_quality` 为 `rss_summary` 时，摘录可能不完整，应特别谨慎。将 `review_status` 从 `pending` 改为 `approved` 或 `rejected`；可以修改标题、摘要、正文和标签。不要将模型提供的推断当成事实。链接和日期来自抓取结果，但仍需对照原文检查，校验并不证明真实性。

发布已审核条目（本地执行）：

```bash
python scripts/generate_news.py --publish /path/to/draft.json
```

此命令只合并 `approved` 条目到 `docs/public/data/news.json`，并在配置可用时尝试同步 Supabase；不会自动提交或推送。检查 `git diff` 后再提交推送以触发 Pages 部署。保留草稿备查；避免重复发布。

## 本地生成与模型比较

```bash
python scripts/generate_news.py --draft output/news-review/draft.json --candidates-output output/news-review/candidates.json
python scripts/compare_news_models.py output/news-review/candidates.json
```

需要 `.env.local` 中配置的 ModelScope 凭据；比较会对三个模型分别发起请求，消耗账号额度。使用同一批候选材料，人工对照原文盲评真实性、完整性、选题、JSON 格式、耗时和消耗，再决定是否更换。结果保存在 `output/news-review/`，不会发布；文件已被 Git 忽略，避免意外公开未审核内容。脚本不会覆盖已有输出。

来源配置读取 Supabase `rss_feeds`；不可用时回退内置 RSS，并在运行日志记录错误。回退时自定义来源及关键词不会生效，应检查连接。`OPENROUTER_API_KEY` 是历史名称，当前用于 ModelScope API，不要将密钥写入草稿或提交到仓库。
