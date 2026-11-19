"""Seeded space-filling futures and stock-based adaptive pathway experiments."""
from dataclasses import asdict
from copy import deepcopy
import math
import random
from .model import Parameters, World, Action


def finite(value, lo, hi, name):
    value = float(value)
    if not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError(f'{name}: expected {lo} to {hi}')
    return value


def continuation(world, action):
    branch = deepcopy(world)
    rows = [branch.observe()]
    revenue = spending = 0.0
    while branch.s.time < branch.p.horizon-1e-10:
        previous_time = branch.s.time
        row = branch.step(action)
        h = row['time']-previous_time
        revenue += row.get('revenue',0)*h
        spending += row.get('spending',0)*h
        rows.append(row)
    return dict(rows=rows, revenue=revenue, spending=spending, action=asdict(action))


def experiment(request):
    inputs = request.get('parameters', {})
    p = Parameters(**inputs)
    if not 1 <= p.horizon <= 50 or not 1/104 <= p.dt <= .25:
        raise ValueError('Horizon must be 1–50 years and dt 1/104–0.25 years')
    n = int(finite(request.get('samples', 8), 1, 40, 'samples'))
    rng = random.Random(int(request.get('seed', 42)))
    jitter = finite(request.get('shock_jitter',0),0,10,'shock jitter')
    ranges = request.get('ranges', {})
    columns = {}
    for key, bounds in ranges.items():
        if key not in ('availability', 'market_growth', 'hiring_delay', 'certification_years'):
            raise ValueError('Unsupported DOE parameter: ' + key)
        low, high = map(float, bounds)
        if not math.isfinite(low+high) or low > high:
            raise ValueError('Invalid range for ' + key)
        values = [low+(high-low)*(i+rng.random())/n for i in range(n)]
        rng.shuffle(values)
        columns[key] = values
    shocks = request.get('shocks', [])
    if len(shocks) > 12:
        raise ValueError('At most twelve shocks')
    shock_columns = []
    for s in shocks:
        if s['kind'] not in ('diversion', 'demand', 'productivity', 'supply'):
            raise ValueError('Unknown shock kind')
        sampled = {}
        for key, lo, hi in [('start',0,p.horizon), ('duration',.01,50), ('magnitude',0,1)]:
            bounds = s.get(key+'_range', [s.get(key), s.get(key)])
            if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                raise ValueError('Expected min/max for shock '+key)
            low, high = [finite(v,lo,hi,'shock '+key) for v in bounds]
            if low > high:
                raise ValueError('Shock minimum exceeds maximum: '+key)
            values = [low+(high-low)*(j+rng.random())/n for j in range(n)]
            rng.shuffle(values)
            sampled[key] = values
        shock_columns.append(sampled)
    cfg = request.get('adaptive', {})
    hire_at = finite(cfg.get('hire_at', .85), .1, 1.5, 'hire threshold')
    protect_at = finite(cfg.get('protect_at', .7), .1, hire_at, 'protection threshold')
    cash_limit = finite(cfg.get('cash_limit', 4000), 1, 1e6, 'cash limit')
    review = finite(cfg.get('review', .25), p.dt, 5, 'review interval')
    latency = finite(cfg.get('latency', .1), 0, 5, 'latency')
    result = []
    for i in range(n):
        params = asdict(p)
        params.update({k:v[i] for k,v in columns.items()})
        future = Parameters(**params)
        # Jitter each event separately. The identical realization is reused across policies.
        events = [dict(kind=s['kind'], start=max(0,min(p.horizon,col['start'][i]+rng.uniform(-1,1)*jitter)),
                       duration=col['duration'][i], magnitude=col['magnitude'][i])
                  for s,col in zip(shocks,shock_columns)]
        for policy in ('baseline','hire','protect_hire','adaptive'):
            world = World(future, events)
            rows = [world.observe()]
            logs, pending, counterfactuals = [], None, []
            action = Action()
            next_review = 0
            while world.s.time < p.horizon-1e-10:
                o = world.observe()
                if policy == 'adaptive':
                    if pending and o['time'] >= pending[0]-1e-9:
                        if request.get('include_counterfactuals', True):
                            counterfactuals.append(dict(decision_id=pending[2], time=o['time'],
                                reasons=pending[3], previous_action=asdict(action), new_action=asdict(pending[1]),
                                keep=continuation(world, action), change=continuation(world, pending[1])))
                        action = pending[1]
                        logs.append(dict(time=o['time'], event='implemented', action=asdict(action),
                                         decision_id=pending[2], reasons=pending[3]))
                        pending = None
                    if o['time'] >= next_review-1e-9 and not o['exited']:
                        next_review = o['time']+review
                        ratio = o['engineers']/future.required_engineers
                        # Escalation is irreversible in this initial pathway design.
                        desired = Action(action.hire or ratio < hire_at,
                                         action.protect or ratio < protect_at,
                                         o['peak_exposure'] >= cash_limit)
                        if desired != action and pending is None:
                            reasons = []
                            if desired.hire and not action.hire:
                                reasons.append(f'Staffing ratio {ratio:.3f} < hire threshold {hire_at:.3f}')
                            if desired.protect and not action.protect:
                                reasons.append(f'Staffing ratio {ratio:.3f} < protection threshold {protect_at:.3f}')
                            if desired.exit:
                                reasons.append(f'Peak exposure {o["peak_exposure"]:.1f} >= limit {cash_limit:.1f} USD million')
                            decision_id = 1 + sum(d['event']=='triggered' for d in logs)
                            pending = (o['time']+latency, desired, decision_id, reasons)
                            logs.append(dict(time=o['time'], event='triggered', staffing_ratio=ratio,
                                             exposure=o['peak_exposure'], action=asdict(desired),
                                             decision_id=decision_id, reasons=reasons,
                                             scheduled_implementation=o['time']+latency))
                else:
                    action = Action(hire=policy!='baseline',protect=policy=='protect_hire')
                rows.append(world.step(action))
            last=rows[-1]
            result.append(dict(run=f'future_{i+1}_{policy}',future=i+1,policy=policy,
                               parameters=params,shocks=events,decisions=logs,rows=rows,
                               counterfactuals=counterfactuals,
                               summary={k:last[k] for k in ('eis','npv','peak_exposure','delivered','exited')}))
    return dict(runs=result,seed=request.get('seed',42),request=request,
                note='Latin hypercube ranges are exploratory, not probability estimates. Adaptive rules are candidate pathways, not optimized DAPP.')


def robustness(request):
    """Re-evaluate exposure triggers over identical seeded futures; return adaptive summaries."""
    original = request['experiment']
    thresholds = request.get('thresholds', [])
    if not 1 <= len(thresholds) <= 9:
        raise ValueError('Choose one to nine exposure thresholds')
    rows = []
    for value in thresholds:
        limit = finite(value, 1, 1e6, 'exposure threshold')
        config = deepcopy(original)
        config['include_counterfactuals'] = False
        config.setdefault('adaptive', {})['cash_limit'] = limit
        result = experiment(config)
        rows.append(dict(threshold=limit, futures=[dict(future=r['future'], **r['summary'])
                                                  for r in result['runs'] if r['policy']=='adaptive']))
    return dict(rows=rows, note='Identical seeded futures at each threshold. Counts are design-space coverage, not probabilities.')
