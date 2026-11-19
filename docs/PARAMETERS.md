# Parameter reference

[Back to the code guide](CODE_GUIDE.md) · [Open the offline guide](index.html)

## World parameters

These are the defaults declared by `Parameters`, not necessarily the current UI fields or a loaded experiment. Complete saved requests are the authoritative inputs for a run. All values must be finite and nonnegative. The exact validator is in [Parameters](../vgc_sd/model.py#L6).

| Code field | Python default | Unit | Meaning | Assumption / constraint |
| --- | --- | --- | --- | --- |
| `horizon` | 25 | years | Simulation end measured from launch | 25 in Python; UI/config use 20 |
| `dt` | 0.019230769 | years | Integration step | 1/52 = weekly; shortened at horizon |
| `required_engineers` | 1000 | FTE | Reference staffing requirement | Positive; not corporate workforce |
| `availability` | 0.8 | ratio | Initial staffing divided by required staffing | Can exceed 1; not a continuing external staffing multiplier |
| `hiring_delay` | 1.5 | years | First-order staffing-gap adjustment time | Positive; not a fixed recruitment pipeline |
| `attrition` | 0.04 | 1/year | Baseline workforce departure rate | Nonnegative; protection does not reduce this |
| `diversion` | 0.08 | 1/year | Baseline diversion to other programs | Protection multiplies total diversion by 0.2 |
| `shock_year` | 3 | years | Start of legacy permanent diversion shock | Interactive UI disables its magnitude |
| `shock_diversion` | 0.12 | 1/year | Legacy permanent addition to diversion | UI sends zero; CSV example uses 0.12 |
| `design_work` | 6000 | FTE-years | Initial remaining design workload | Positive |
| `rework_fraction` | 0.12 | fraction | Maximum pressure-scaled share of completion returned as rework | 0 to 1 |
| `certification_years` | 2 | years | Nominal progress time at full staffing/productivity | Positive |
| `capacity_target` | 60 | aircraft/year | Post-certification production capacity target | Nonnegative; no cash gate |
| `ramp_years` | 3 | years | Capacity adjustment time | Positive; dt must not exceed this |
| `market_units` | 850 | aircraft/year | Initial total annual demand rate | Not fleet size |
| `market_growth` | 0.03 | fraction/year | Annual compounding demand trend | Nonnegative in current validator |
| `capture_share` | 0.06 | fraction | Fixed share of market orders | 0 to 1; not a dynamic share stock |
| `price` | 40 | USD million/aircraft | Revenue per delivered aircraft | Constant real price |
| `unit_cost` | 32 | USD million/aircraft | Initial unit production cost | Learning reference/floor hard-coded in step |
| `learning_exponent` | 0.08 | dimensionless | Power-law cost reduction with cumulative deliveries | Nonnegative; zero disables learning |
| `engineer_cost` | 0.18 | USD million/FTE/year | Annual program engineering cost | Charged throughout operations |
| `overhead` | 40 | USD million/year | Fixed annual program operating overhead | Charged throughout operations |
| `certification_cost` | 300 | USD million | Total cost at certification completion | Spent in proportion to actual progress |
| `capex` | 500 | USD million | Time-zero project capital expenditure | No staged industrial investment |
| `protection_cost` | 25 | USD million/year | Cost while protection is active | Does not depend on workforce size |
| `discount_rate` | 0.08 | annual fraction | Effective real discount rate | Used at interval-end times |

Additional validation: horizon, dt, required engineers, hiring delay, design work, certification years and ramp years must be positive. dt must not exceed the smaller of hiring_delay and ramp_years. The experiment API additionally bounds horizon to 1–50 years and dt to 1/104–0.25 years. Supported sampled parameters are revalidated when constructing each future. No dimensional-analysis library checks units.

## Adaptive policy settings

These fields live in `request.adaptive`, not in `Parameters`.

| Field | Default | Meaning | Constraint |
| --- | --- | --- | --- |
| `hire_at` | 0.85 | Trigger hiring if engineers/required is strictly below this | 0.1 to 1.5 |
| `protect_at` | 0.7 | Trigger protection if staffing ratio is strictly below this | 0.1 to hire_at |
| `cash_limit` | 4000 | Trigger exit if historical peak exposure is at least this | 1 to 1,000,000 USD million; team example uses 2800 |
| `review` | 0.25 | Time between stock-based reviews | dt to 5 years |
| `latency` | 0.1 | Requested trigger-to-implementation delay | 0 to 5 years; grid ordering adds at least one loop |

## Experiment settings

| Field | Default / accepted values | Meaning |
| --- | --- | --- |
| `samples` | 8; API accepts 1–40 then converts to int | Number of futures; four policy runs each |
| `seed` | 42 | Initializes local Python random generator |
| `ranges` | Empty in API; UI prepopulates four ranges | Min/max Latin hypercube inputs; override fixed world parameters |
| `shocks` | Empty in API; UI supplies example events | Up to 12 event descriptions; every event occurs once per future |
| `shock_jitter` | 0 | Legacy uniform extra start shift, clamped to horizon; UI sends zero |
| `include_counterfactuals` | True | Compute same-state decision audit branches; disabled during robustness sweeps |

`samples` and `seed` are converted with int() in the backend. Supply integer values; fractional API inputs are not separate sampling modes. UI defaults are defined independently in app.html.

## Shock event settings

| Field | Input shape / bound | Meaning |
| --- | --- | --- |
| `kind` | diversion, demand, productivity, supply | Equation channel |
| `start_range` | [min,max], both 0–horizon | Sampled beginning year |
| `duration_range` | [min,max], both 0.01–50 years | Sampled duration, may extend beyond horizon |
| `magnitude_range` | [min,max], both 0–1 | Annual rate addition for diversion; fractional reduction for other types |

Min must not exceed max. Equal min/max fixes a value. For API compatibility, `start`, `duration`, `magnitude` scalars can replace their ranges. Realized events returned in run.shocks always use scalar values. Example: diversion magnitude 0.2 adds 20 percentage points/year to the departure rate; it does not instantly remove 20% of engineers.

## Dashboard settings

The browser starts with minimum NPV 0 USD million and latest acceptable EIS year 12. Success additionally requires no exit. These criteria are not policy thresholds and do not alter simulation trajectories. Exposure sweep values are alternative policy triggers; they do rerun Python. Neither the currently selected dashboard criteria nor computed sweep results are in the main experiment export.

## Built-in constants to recognize

| Constant | Where | Current effect |
| --- | --- | --- |
| 0.2 | protection equation | Retains 20% of diversion rate |
| 10 aircraft | learning equation | Reference cumulative delivery quantity |
| 0.6 | learned unit cost floor | Minimum 60% of original unit cost |
| 1e-9 | design work | Near-zero completion tolerance |
| 1e-10 / 1e-9 | loops / event comparisons | Floating-point timing tolerance |

These are not editable in the current UI. Changing them requires code changes and validation.
