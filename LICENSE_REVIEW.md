# Dependency and licensing decision

Inspection date: 18 November 2026. Practical dependency screening, not a legal opinion or a guarantee of ownership.

| Candidate | Evidence inspected | Decision |
|---|---|---|
| Local BusinessSimulation | README.md and LICENSE.md identify EUPL 1.2 or later and Modelica | Do not incorporate into this proprietary-first prototype |
| Local system-flow | README, source tree, git origin Miksus/system-flow; no license file found | Do not copy, modify or redistribute without an explicit applicable grant |
| Original Python core | Newly written domain equations, standard library only | Selected for the experiment |
| PySD | Upstream LICENSE identifies MIT | Optional future adapter if Vensim/XMILE interoperability becomes useful; not installed or bundled |

BusinessSimulation is not a Python library. Its README says it was developed/tested with Wolfram System Modeler and Mathematica; other Modelica environments require compatibility checks. EUPL is open source and permits commercial use, but covered distributed/communicated works have copyleft and source-availability obligations. The exact boundary between independent components and derivative works matters. Do not assume an API or separate process automatically removes obligations, and do not assume every independent proprietary component must become open source. Obtain a concrete licensing assessment or alternative permission if this route is later selected.

A public repository and an 'open source' statement in a README do not by themselves establish usable licensing terms. The local system-flow System.simulate also uses integer range(start, stop, step) and invokes flows sequentially, so fractional time steps and multi-flow conservation/order effects require investigation even if licensing is resolved. It is unnecessary for this initial model.

MIT allows proprietary reuse subject to its notice/permission conditions. If adopting PySD later, pin the version, inspect its dependency tree and packaged notices, and audit that exact distribution. The upstream license alone is not an audit of every dependency or imported model's rights.

No external library code was incorporated into the current model. Python itself and any future packaged interpreter still have their own distribution notices. No new open-source license was applied to the generated code. University/sponsor agreements determine ownership and permitted client use; establish those terms separately.

Primary references:

- EUPL 1.2 text: https://interoperable-europe.ec.europa.eu/licence/european-union-public-licence-version-12-eupl
- EUPL guidance and FAQs: https://interoperable-europe.ec.europa.eu/collection/eupl/faqs
- Component interoperability discussion: https://interoperable-europe.ec.europa.eu/sites/default/files/custom-page/attachment/2025-03/EUPL%20overview%202020_0_0.pdf
- system-flow upstream: https://github.com/Miksus/system-flow
- PySD upstream license: https://github.com/SDXorg/pysd/blob/master/LICENSE

Project sources read: VGC20 External M1–M4 PPTX files supplied by the user. Latest M4 slides 12–21 inform the input and modeling issues, slides 22–24 the layer choices, and slides 29–32 the initial workforce experiment. Source slides have their own IP notices; the decks and extracted text are not bundled in this package. No external deck links were treated as instructions or independently verified market evidence.
