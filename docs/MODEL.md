# Model notes

## State and integration

The world stores program engineers (FTE), remaining design work (FTE-years), certification progress (0–1), production capacity (aircraft/year), order backlog and cumulative deliveries (aircraft), cumulative net cash, NPV and peak cash exposure (constant USD million). Aircraft quantities are continuous SD approximations.

Explicit Euler updates use beginning-of-step state and weekly default time steps. The final step shortens to the horizon. Threshold and event timing is quantized to the integration grid. Smaller steps and convergence checks remain important near gates.

## Main relationships

Hiring, when enabled, closes the required/available staffing gap over `hiring_delay` and replaces current losses. Attrition and diversion remove engineers. Protection reduces diversion to 20% of its unprotected rate, with an annual cost. Recruitment is an aggregate first-order adjustment, not a fixed hiring pipeline.

Design completion is bounded by engineers, productivity and remaining work. Staffing pressure increases rework per unit completed. Certification starts after design work reaches zero and depends on staffing and productivity. This is a program readiness proxy, not regulatory approval simulation or an average TRL.

Orders begin only after certification. Production capacity ramps toward a target; deliveries are limited by capacity, supply shocks and beginning-of-step backlog. Cumulative deliveries lower unit cost through a bounded learning curve. Market share is fixed and there is no competitor response.

## Cash and exposure

Cashflow is revenue minus production costs, engineering costs, overhead, certification expenditure and protection costs. Capex is charged at time zero. NPV discounts end-of-step cashflows using an annual effective real discount rate. Peak exposure is the maximum negative cumulative undiscounted net project cash, including initial capex. This is a project metric, not corporate cash availability. There is no automatic bankruptcy constraint.

## Scenarios and adaptive policies

Four policies share each realized future: baseline, hire, protect-and-hire, and adaptive. Independent Latin hypercube sampling varies supported uncertainty parameters and shock start/duration/magnitude. Correlation, uncertain event occurrence and event counts are not modeled.

Diversion shocks add annual workforce loss rates. Demand, productivity and supply shocks multiply remaining factors while active. Productivity affects design and certification; supply reduces delivery throughput. Overlapping shocks combine. The interactive UI disables the legacy single permanent workforce shock in favor of explicit events. The CSV mode retains its own configuration.

Adaptive review checks observed staffing/required ratios and peak exposure. Hiring and protection escalate irreversibly, with review intervals and implementation delay. Pending actions cannot be cancelled, and can delay a subsequent exit decision. Exit is absorbing and stops operational changes. It includes no closure costs, salvage, recovery or contract penalties.

## Robustness and audits

Success requires no exit plus the dashboard NPV and EIS criteria. Design-space coverage counts are not real-world probabilities. Exposure sweeps rerun identical seeded futures with different exit triggers. Exit is a policy decision, distinct from success or failure against stakeholder criteria.

Decision audits fork from the exact state immediately before implementation. One branch holds the prior action and the other holds the newly selected action. Neither makes subsequent adaptive decisions. Both retain identical future shocks. A combined hire/protect decision is evaluated as a package. Cash decomposition reconciles extra revenue minus extra spending to the final undiscounted cash difference.

## Calibration needs

Validate staffing requirements, work breakdown, rework relationships, hiring/diversion histories, certification work and costs, market segment, production ramp, unit economics and price base against an agreed proxy case. Corporate R&D/CapEx must not be substituted for program costs. Available/required program staffing differs from the program's share of total corporate headcount. Ordinal TRL scores should not be treated as physical accumulating stocks.

The equations, sample values and apparent decision thresholds are hypotheses for research. Threshold crossings in NPV or schedule do not establish mathematical bifurcations. Tests check numerical and implementation properties, not empirical accuracy.
