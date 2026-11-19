import argparse
import csv
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from .model import Parameters, Action, World, simulate
from .report import write_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config/baseline.json')
    parser.add_argument('--out', default='results')
    parser.add_argument('--years', type=float, help='Override simulation horizon in years')
    args = parser.parse_args()
    p = Parameters(**json.loads(Path(args.config).read_text()))
    if args.years is not None:
        p = replace(p, horizon=args.years)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    policies = {'baseline': Action(), 'hire': Action(hire=True),
                'protect_hire': Action(hire=True, protect=True)}
    summary, manifest, report_runs = [], [], []
    for availability in (0.6, 0.8, 1.1):
        for name, action in policies.items():
            config = replace(p, availability=availability)
            rows = simulate(config, lambda observation: action)
            run_id = f'{name}_{availability:.1f}'
            with (out / f'{run_id}.csv').open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows)
            last = rows[-1]
            summary.append(dict(run=run_id, eis=last['eis'], npv=last['npv'],
                                peak_exposure=last['peak_exposure'], delivered=last['delivered']))
            manifest.append(dict(run=run_id, parameters=asdict(config), action=asdict(action)))
            initial = World(config).observe()
            initial.update(orders=0.0, deliveries=0.0, cashflow=0.0,
                           hires=0.0, losses=0.0, completed_work=0.0, rework=0.0)
            report_runs.append(dict(run=run_id, policy=name, parameters=asdict(config),
                                    rows=[initial] + rows))
    with (out / 'summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary[0])
        writer.writeheader()
        writer.writerows(summary)
    code_hash = hashlib.sha256(Path(__file__).with_name('model.py').read_bytes()).hexdigest()
    (out / 'manifest.json').write_text(json.dumps(dict(model_sha256=code_hash,
        units='years, FTE, engineer-years, aircraft, constant USD million',
        status='synthetic demonstration, uncalibrated', runs=manifest), indent=2))
    write_report(out / 'report.html', report_runs)
    print(f'Wrote {len(summary)} experiments to {out.resolve()}')
    print(f'Open {(out / "report.html").resolve()} in your browser')


if __name__ == '__main__':
    main()
