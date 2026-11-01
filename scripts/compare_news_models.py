"""Compare models on the same saved candidate input; never publish results."""
import argparse
import json
import time
from pathlib import Path
import generate_news as news

parser = argparse.ArgumentParser()
parser.add_argument('input', help='JSON array of enriched source candidates')
parser.add_argument('--output', default='output/news-review/model-comparison.json')
args = parser.parse_args()
candidates = json.loads(Path(args.input).read_text(encoding='utf-8'))
if not isinstance(candidates, list) or not 1 <= len(candidates) <= 20:
    parser.error('input must be an array of 1–20 enriched source candidates')
results = []
for model in ('Qwen/Qwen3.5-397B-A17B', 'Qwen/Qwen3.8-Flash-Next', 'deepseek-ai/DeepSeek-V4.1-Flash'):
    news.MODEL_NAME = model
    started = time.monotonic()
    try:
        items = news.validate_insights(news.distill_wisdom(candidates), candidates)
        results.append({'model': model, 'seconds': round(time.monotonic()-started, 2), 'items': items})
    except Exception as error:
        results.append({'model': model, 'seconds': round(time.monotonic()-started, 2), 'error': str(error)})
path = Path(args.output)
path.parent.mkdir(parents=True, exist_ok=True)
if path.exists():
    raise FileExistsError(path)
path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Comparison saved to {path}. Review factual accuracy against sources; timing is not a quality score.')
