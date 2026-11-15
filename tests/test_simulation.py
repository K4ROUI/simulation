"""Tests de comportement du simulateur pédagogique, sans prétention de validation IEEE."""

import unittest
from unittest.mock import patch

import numpy as np

import simulation


class SimulationTests(unittest.TestCase):
    def run_small_simulation(self, seed=2026, stations=3):
        np.random.seed(seed)
        with patch.object(simulation, "TEMPS_MAX", 100):
            return simulation.simulateur_mac(
                N=stations, K=6, lam=0.12, tau=1.0
            )

    def test_returns_four_outputs(self):
        debit_t, occupation_t, perte, debit = self.run_small_simulation()
        self.assertTrue(debit_t)
        self.assertEqual(len(debit_t), len(occupation_t))
        self.assertGreaterEqual(debit, 0)
        self.assertGreaterEqual(perte, 0)
        self.assertLessEqual(perte, 1)

    def test_reproducible_with_fixed_seed(self):
        a = self.run_small_simulation(seed=77)
        b = self.run_small_simulation(seed=77)
        self.assertEqual(a, b)

    def test_history_is_chronological(self):
        debit_t, occupation_t, _, _ = self.run_small_simulation(seed=91)
        times = [t for t, _ in debit_t]
        self.assertTrue(all(t2 >= t1 for t1, t2 in zip(times, times[1:])))
        self.assertTrue(all(t > 0 for t in times))
        self.assertEqual(times, [t for t, _ in occupation_t])

    def test_one_station_no_queue_overflow_in_short_low_load_case(self):
        np.random.seed(123)
        with patch.object(simulation, "TEMPS_MAX", 50):
            _, _, perte, debit = simulation.simulateur_mac(
                N=1, K=1000, lam=0.01, tau=1.0
            )
        self.assertEqual(perte, 0.0)
        self.assertGreaterEqual(debit, 0.0)


if __name__ == "__main__":
    unittest.main()
