import unittest

from reconstruct_attempt import add_range, timing


class ReconstructionTests(unittest.TestCase):
    def test_overlap(self):
        union = []
        got = [
            add_range(union, *interval)
            for interval in ((0, 10), (4, 7), (12, 16), (8, 14))
        ]
        self.assertEqual(got, [10, 0, 4, 2])
        self.assertEqual(union, [(0, 16)])

    def test_origin_deadline(self):
        for received, horizon, expected in [
            (200, 201, "timely"),
            (201, 201, "late"),
            (None, 199, "censored"),
            (None, 200, "miss"),
        ]:
            self.assertEqual(timing(100, received, horizon, 100), expected)
        with self.assertRaises(ValueError):
            timing(100, 199, 140, 100)
