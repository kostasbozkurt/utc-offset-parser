import datetime
import unittest

from utc_offset_parser import OffsetParseError, parse_utc_offset


class TestParseUtcOffset(unittest.TestCase):
    def test_simple_with_colon(self):
        tz = parse_utc_offset("+05:30")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5, minutes=30))

    def test_gmt_prefix(self):
        tz = parse_utc_offset("GMT-5")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5))

    def test_utc_prefix(self):
        tz = parse_utc_offset("UTC+02:00")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=2))

    def test_compact_minutes(self):
        tz = parse_utc_offset("+0530")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5, minutes=30))

    def test_hours_only(self):
        tz = parse_utc_offset("-09")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-9))

    def test_one_digit_hours_with_colon(self):
        tz = parse_utc_offset("+1:30")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=1, minutes=30))

    def test_zero_offset(self):
        tz = parse_utc_offset("+00:00")
        self.assertIs(tz, datetime.timezone.utc)
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(0))

    def test_negative_minutes(self):
        tz = parse_utc_offset("-05:30")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5, minutes=-30))

    def test_leading_trailing_whitespace(self):
        tz = parse_utc_offset("  +05:30  ")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5, minutes=30))

    def test_case_insensitive_prefix(self):
        tz = parse_utc_offset("gmt+07")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=7))

    def test_reject_internal_whitespace(self):
        with self.assertRaises(OffsetParseError):
            parse_utc_offset("+ 05:30")

    def test_reject_trailing_garbage(self):
        with self.assertRaises(OffsetParseError):
            parse_utc_offset("+05:30 extra")

    def test_reject_empty(self):
        with self.assertRaises(OffsetParseError):
            parse_utc_offset("")

    def test_reject_non_string(self):
        with self.assertRaises(OffsetParseError):
            parse_utc_offset(530)  # type: ignore[arg-type]

    def test_reject_hours_out_of_range(self):
        with self.assertRaises(OffsetParseError):
            parse_utc_offset("+24:00")

    def test_reject_minutes_out_of_range(self):
        with self.assertRaises(OffsetParseError):
            parse_utc_offset("+05:60")

    def test_ambiguous_compact_one_digit_rejected(self):
        # "+130" is ambiguous (could be +1:30 or +13:00); we refuse to guess.
        with self.assertRaises(OffsetParseError):
            parse_utc_offset("+130")


if __name__ == "__main__":
    unittest.main()
