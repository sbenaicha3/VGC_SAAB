import unittest
from vgc_sd.experiment import experiment, robustness
from vgc_sd.model import World, Parameters, Action


class ExperimentTests(unittest.TestCase):
    def test_robustness_matches_identical_futures(self):
        config=dict(parameters=dict(horizon=3,availability=.5),samples=2,seed=9,
                    adaptive=dict(cash_limit=800),include_counterfactuals=False)
        baseline=experiment(config)
        sweep=robustness(dict(experiment=config,thresholds=[800,2800]))
        expected=[r['summary'] for r in baseline['runs'] if r['policy']=='adaptive']
        for expected_summary,actual in zip(expected,sweep['rows'][0]['futures']):
            self.assertEqual(expected_summary,{k:v for k,v in actual.items() if k!='future'})
        self.assertEqual(config['adaptive']['cash_limit'],800)
        self.assertTrue(all(not r['counterfactuals'] for r in baseline['runs']))

    def test_decision_branches_share_state_and_cash_decomposition(self):
        request=dict(parameters=dict(horizon=3,availability=.5),samples=1,
                     shocks=[dict(kind='diversion',start=1,duration=.5,magnitude=.2)])
        run=experiment(request)['runs'][-1]
        self.assertTrue(run['counterfactuals'])
        for fork in run['counterfactuals']:
            keep,change=fork['keep'],fork['change']
            self.assertEqual(keep['rows'][0],change['rows'][0])
            self.assertAlmostEqual(keep['rows'][0]['time'],fork['time'])
            for branch in (keep,change):
                self.assertAlmostEqual(branch['rows'][-1]['time'],3)
                self.assertAlmostEqual(branch['rows'][-1]['cash']-branch['rows'][0]['cash'],
                                       branch['revenue']-branch['spending'],places=7)

    def test_shock_ranges_stratified_and_shared(self):
        request=dict(parameters=dict(horizon=4),samples=4,seed=19,
                     shocks=[dict(kind='demand',start_range=[0,4],duration_range=[1,2],magnitude_range=[0,.8])])
        a=experiment(request)
        events=[r['shocks'][0] for r in a['runs'][::4]]
        for key,low,width in [('start',0,1),('duration',1,.25),('magnitude',0,.2)]:
            self.assertEqual(sorted(int((e[key]-low)/width) for e in events),[0,1,2,3])
        self.assertEqual(a,experiment(request))
        for offset in range(0,16,4):
            self.assertTrue(all(r['shocks']==a['runs'][offset]['shocks'] for r in a['runs'][offset:offset+4]))

    def test_decision_explanations_and_links(self):
        run=experiment(dict(parameters=dict(horizon=1,availability=.5),samples=1))['runs'][-1]
        trigger=next(d for d in run['decisions'] if d['event']=='triggered')
        applied=next(d for d in run['decisions'] if d['event']=='implemented')
        self.assertEqual(trigger['decision_id'],applied['decision_id'])
        self.assertTrue(trigger['reasons'])
        self.assertGreaterEqual(applied['time'],trigger['scheduled_implementation'])

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            experiment(dict(shocks=[dict(kind='demand',start_range=[3,1],duration=1,magnitude=.5)]))

    def test_reproducible_matched_worlds_and_lhs(self):
        request=dict(parameters=dict(horizon=2,shock_diversion=0),samples=4,seed=12,
                     ranges=dict(availability=[.6,1.0]),
                     shocks=[dict(kind='diversion',start=.5,duration=1,magnitude=.2)],shock_jitter=.1)
        a=experiment(request)
        self.assertEqual(a,experiment(request))
        values=[r['parameters']['availability'] for r in a['runs'][::4]]
        self.assertEqual(sorted(int((v-.6)/.1) for v in values),[0,1,2,3])
        self.assertTrue(all(r['shocks']==a['runs'][0]['shocks'] for r in a['runs'][:4]))

    def test_shock_effect_and_expiry(self):
        p=Parameters(shock_diversion=0)
        w=World(p,[dict(kind='productivity',start=0,duration=p.dt,magnitude=1)])
        self.assertEqual(w.step(Action())['completed_work'],0)
        self.assertGreater(w.step(Action())['completed_work'],0)

    def test_adaptive_latency_and_exit(self):
        a=experiment(dict(parameters=dict(horizon=1,availability=.5),samples=1,
                          adaptive=dict(latency=.2,cash_limit=1)))
        r=a['runs'][-1]
        self.assertEqual(r['decisions'][0]['event'],'triggered')
        self.assertGreaterEqual(r['decisions'][1]['time'],.2)
        self.assertTrue(r['summary']['exited'])

    def test_invalid_shock(self):
        with self.assertRaises(ValueError):
            experiment(dict(shocks=[dict(kind='demand',start=1,duration=1,magnitude=2)]))
