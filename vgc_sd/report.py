"""Self-contained offline HTML report. No external scripts or services."""
import json
from pathlib import Path


def write_report(path, runs):
    template = Path(__file__).with_name('report.html').read_text(encoding='utf-8')
    payload = json.dumps(runs, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    Path(path).write_text(template.replace('__RUN_DATA__', payload), encoding='utf-8')
