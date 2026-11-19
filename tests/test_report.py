import json
import re
import tempfile
import unittest
from pathlib import Path
from dataclasses import asdict
from vgc_sd.model import Parameters, Action, World, simulate
from vgc_sd.report import write_report


class ReportTests(unittest.TestCase):
    def test_embedded_data_preserves_initial_and_final_state(self):
        p = Parameters(horizon=20)
        rows = [World(p).observe()] + simulate(p, lambda o: Action(hire=True))
        runs = [dict(policy='hire', parameters=asdict(p), rows=rows)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.html'
            write_report(path, runs)
            html = path.read_text(encoding='utf-8')
        payload = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1)
        data = json.loads(payload)
        self.assertEqual(data[0]['rows'][0]['time'], 0)
        self.assertAlmostEqual(data[0]['rows'][-1]['time'], 20)
        self.assertEqual(data[0]['rows'][-1]['npv'], rows[-1]['npv'])
        self.assertNotIn('__RUN_DATA__', html)
        self.assertNotIn('<script src=', html)
