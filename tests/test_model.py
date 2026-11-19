import unittest
from dataclasses import replace
from vgc_sd.model import Parameters, Action, World, simulate


class ModelTests(unittest.TestCase):
    def test_balances_and_gates(self):
        p = Parameters()
        w = World(p)
        previous = w.observe()
        while w.s.time < p.horizon - 1e-10:
            r = w.step(Action(hire=True))
            h = r['time'] - previous['time']
            self.assertAlmostEqual(r['engineers'], previous['engineers'] + h*(r['hires']-r['losses']))
            self.assertAlmostEqual(r['work'], previous['work'] + h*(r['rework']-r['completed_work']))
            self.assertAlmostEqual(r['backlog'], previous['backlog'] + h*(r['orders']-r['deliveries']))
            self.assertAlmostEqual(r['cash'], previous['cash'] + h*r['cashflow'])
            if previous['certification'] < 1:
                self.assertEqual(r['deliveries'], 0)
            for k in ('engineers', 'work', 'backlog', 'capacity'):
                self.assertGreaterEqual(r[k], -1e-9)
            previous = r

    def test_zero_engineers_cannot_certify(self):
        rows = simulate(Parameters(availability=0), lambda o: Action())
        self.assertIsNone(rows[-1]['eis'])
        self.assertEqual(rows[-1]['delivered'], 0)

    def test_exit_is_absorbing(self):
        w = World(Parameters())
        before = w.observe()
        w.step(Action(exit=True))
        after = w.step(Action(hire=True))
        self.assertEqual(after['cash'], before['cash'])
        self.assertEqual(after['work'], before['work'])

    def test_timestep_convergence(self):
        p = Parameters()
        a = simulate(p, lambda o: Action(hire=True))[-1]
        b = simulate(replace(p, dt=p.dt/2), lambda o: Action(hire=True))[-1]
        self.assertLess(abs(a['eis']-b['eis']), 0.06)
        # Scale by project exposure: net NPV may legitimately approach zero.
        self.assertLess(abs(a['npv']-b['npv']) / b['peak_exposure'], 0.01)

    def test_deterministic_and_validation(self):
        p = Parameters(horizon=0.2)
        self.assertEqual(simulate(p, lambda o: Action()), simulate(p, lambda o: Action()))
        with self.assertRaises(ValueError):
            Parameters(hiring_delay=0)


if __name__ == '__main__':
    unittest.main()
