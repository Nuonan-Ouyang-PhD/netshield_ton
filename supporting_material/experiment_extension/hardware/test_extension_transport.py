import unittest
from collections import defaultdict

from reconstruct_attempt import add_range, timing, verify_receipts


class ReconstructionTests(unittest.TestCase):
    def test_receipt_identity_and_offsets(self):
        seg = dict(event_key="a", event_id="sample", offset=0, length=4, total_bytes=8)
        ack = dict(
            event_key="a",
            event_id="sample",
            offset=0,
            segment_bytes_received=4,
            event_total_bytes=8,
            event_bytes_received=4,
            unique_bytes_added=4,
            complete=False,
        )

        def frame(receipts):
            return dict(sent_segments=[seg], receipt_ack=dict(segments=receipts))

        for change in (
            dict(event_key="b"),
            dict(offset=4),
            dict(event_bytes_received=8),
            dict(complete=True),
            dict(unique_bytes_added=0),
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_receipts(frame([dict(ack, **change)]), defaultdict(list))
        covered = defaultdict(list)
        self.assertEqual(verify_receipts(frame([]), covered), 1)
        self.assertFalse(covered)
        self.assertEqual(verify_receipts(frame([ack]), covered), 0)
        self.assertEqual(
            verify_receipts(frame([dict(ack, unique_bytes_added=0)]), covered), 0
        )
        self.assertEqual(covered["a"], [(0, 4)])

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
