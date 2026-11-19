from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class Parameters:
    horizon: float = 25.0
    dt: float = 1 / 52
    required_engineers: float = 1000
    availability: float = 0.8
    hiring_delay: float = 1.5
    attrition: float = 0.04
    diversion: float = 0.08
    shock_year: float = 3.0
    shock_diversion: float = 0.12
    design_work: float = 6000  # engineer-years
    rework_fraction: float = 0.12
    certification_years: float = 2.0
    capacity_target: float = 60.0  # aircraft/year
    ramp_years: float = 3.0
    market_units: float = 850.0  # aircraft/year, illustrative total market
    market_growth: float = 0.03
    capture_share: float = 0.06
    price: float = 40.0  # constant USD million/aircraft
    unit_cost: float = 32.0
    learning_exponent: float = 0.08
    engineer_cost: float = 0.18  # USD million/FTE/year
    overhead: float = 40.0  # USD million/year
    certification_cost: float = 300.0  # total USD million
    capex: float = 500.0  # time-zero USD million
    protection_cost: float = 25.0  # USD million/year
    discount_rate: float = 0.08

    def __post_init__(self):
        for k, v in asdict(self).items():
            if not math.isfinite(v) or v < 0:
                raise ValueError(f'{k} must be finite and nonnegative')
        for k in ('horizon', 'dt', 'required_engineers', 'hiring_delay',
                  'design_work', 'certification_years', 'ramp_years'):
            if getattr(self, k) <= 0:
                raise ValueError(f'{k} must be positive')
        for k in ('rework_fraction', 'capture_share'):
            if getattr(self, k) > 1:
                raise ValueError(f'{k} must be <= 1')
        if self.dt > min(self.hiring_delay, self.ramp_years):
            raise ValueError('dt exceeds a smoothing time constant')


@dataclass(frozen=True)
class Action:
    hire: bool = False
    protect: bool = False
    exit: bool = False


@dataclass
class State:
    time: float
    engineers: float
    work: float
    certification: float = 0.0
    capacity: float = 0.0
    backlog: float = 0.0
    delivered: float = 0.0
    cash: float = 0.0
    npv: float = 0.0
    peak_exposure: float = 0.0
    eis: float | None = None
    exited: bool = False


class World:
    """Beginning-of-step rates, simultaneous Euler stock updates; years and USD million."""
    def __init__(self, p: Parameters, shocks=()):
        self.p = p
        self.shocks = tuple(shocks)
        self.s = State(0, p.required_engineers * p.availability, p.design_work,
                       cash=-p.capex, npv=-p.capex, peak_exposure=p.capex)

    def observe(self):
        # Only contemporaneous indicators: future shocks remain in the world configuration.
        return asdict(self.s).copy()

    def step(self, a: Action):
        p, s = self.p, self.s
        h = min(p.dt, p.horizon - s.time)
        if h <= 1e-12:
            raise ValueError('simulation horizon reached')
        if a.exit:
            s.exited = True
        if s.exited:
            s.time += h
            return dict(**asdict(s), orders=0.0, deliveries=0.0, cashflow=0.0,
                        hires=0.0, losses=0.0, completed_work=0.0, rework=0.0)
        diversion = p.diversion + (p.shock_diversion if s.time >= p.shock_year else 0)
        market_factor = productivity = supply = 1.0
        for shock in self.shocks:
            if shock['start'] <= s.time < shock['start'] + shock['duration']:
                kind, magnitude = shock['kind'], shock['magnitude']
                if kind == 'diversion':
                    diversion += magnitude
                elif kind == 'demand':
                    market_factor *= 1 - magnitude
                elif kind == 'productivity':
                    productivity *= 1 - magnitude
                elif kind == 'supply':
                    supply *= 1 - magnitude
        if a.protect:
            diversion *= 0.2
        losses = min(s.engineers / h, s.engineers * (p.attrition + diversion))
        hires = (max(0, p.required_engineers - s.engineers) / p.hiring_delay
                 + losses) if a.hire else 0.0
        pressure = max(0, 1 - s.engineers / p.required_engineers)
        # Rework is added to remaining work, giving a balancing progress loop.
        completed = min(s.work / h, s.engineers * productivity) if s.work > 1e-9 else 0.0
        rework = completed * p.rework_fraction * min(1, pressure)
        work = max(0.0, s.work + (rework - completed) * h)
        if work < 1e-9:
            work = 0.0
        cert_rate = (productivity * min(1, s.engineers / p.required_engineers) / p.certification_years
                     if s.work == 0 and s.certification < 1 else 0)
        cert_delta = min(1 - s.certification, cert_rate * h)
        active = s.certification >= 1
        capacity = s.capacity + ((p.capacity_target - s.capacity) / p.ramp_years * h
                                 if active else 0)
        orders = market_factor * p.market_units * (1 + p.market_growth) ** s.time * p.capture_share if active else 0
        deliveries = min(s.capacity * supply, s.backlog / h) if active else 0
        cost_per_unit = p.unit_cost * max(1, s.delivered / 10) ** (-p.learning_exponent)
        cost_per_unit = max(0.6 * p.unit_cost, cost_per_unit)
        revenue = p.price * deliveries
        spending = (cost_per_unit * deliveries + p.engineer_cost * s.engineers
                    + p.overhead + p.certification_cost * cert_delta / h
                    + (p.protection_cost if a.protect else 0))
        flow = ((p.price - cost_per_unit) * deliveries - p.engineer_cost * s.engineers
                - p.overhead - p.certification_cost * cert_delta / h
                - (p.protection_cost if a.protect else 0))
        s.engineers += (hires - losses) * h
        s.work = work
        s.certification += cert_delta
        capacity_change = (capacity - s.capacity) / h
        s.capacity = capacity
        s.backlog += (orders - deliveries) * h
        s.delivered += deliveries * h
        s.cash += flow * h
        s.npv += flow * h / (1 + p.discount_rate) ** (s.time + h)
        s.peak_exposure = max(s.peak_exposure, -s.cash)
        s.time += h
        if s.certification >= 1 and s.eis is None:
            s.eis = s.time
        return dict(**asdict(s), orders=orders, deliveries=deliveries, cashflow=flow,
                    hires=hires, losses=losses, completed_work=completed, rework=rework,
                    revenue=revenue, spending=spending, certification_rate=cert_delta/h,
                    capacity_change=capacity_change)


def simulate(p: Parameters, policy):
    world = World(p)
    rows = []
    while world.s.time < p.horizon - 1e-10:
        rows.append(world.step(policy(world.observe())))
    return rows
