"""Tests for the cli and ai modules."""

import datetime
import unittest

from click.testing import CliRunner

from geemap import ai
from geemap.cli import main


class TestMatchesDatetime(unittest.TestCase):

    def setUp(self):
        self.start_date = datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC)
        self.end_date = datetime.datetime(2021, 1, 1, tzinfo=datetime.UTC)
        self.now = datetime.datetime.now(tz=datetime.UTC)
        self.before_start = datetime.datetime(2019, 12, 31, tzinfo=datetime.UTC)
        self.after_end = datetime.datetime(2021, 1, 2, tzinfo=datetime.UTC)
        self.within_interval = datetime.datetime(2020, 6, 1, tzinfo=datetime.UTC)
        self.after_now = self.now + datetime.timedelta(days=1)

    def test_end_date_set_query_within_interval(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertTrue(ai.matches_datetime(collection_interval, self.within_interval))

    def test_end_date_set_query_exactly_at_start(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertTrue(ai.matches_datetime(collection_interval, self.start_date))

    def test_end_date_set_query_exactly_at_end(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertTrue(ai.matches_datetime(collection_interval, self.end_date))

    def test_end_date_set_query_before_start(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertFalse(ai.matches_datetime(collection_interval, self.before_start))

    def test_end_date_set_query_after_end(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertFalse(ai.matches_datetime(collection_interval, self.after_end))

    def test_end_date_none_query_before_start(self):
        collection_interval = (self.start_date, None)
        self.assertFalse(ai.matches_datetime(collection_interval, self.before_start))

    def test_end_date_none_query_within_interval(self):
        collection_interval = (self.start_date, None)
        # Assuming the interval from start_date to now contains this date
        self.assertTrue(ai.matches_datetime(collection_interval, self.within_interval))

    def test_end_date_none_query_after_now(self):
        collection_interval = (self.start_date, None)
        self.assertFalse(ai.matches_datetime(collection_interval, self.after_now))


class TestMain(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_main_no_args_returns_zero(self):
        result = self.runner.invoke(main)
        self.assertEqual(result.exit_code, 0)

    def test_main_no_args_outputs_message(self):
        result = self.runner.invoke(main)
        self.assertIn("geemap.cli.main", result.output)

    def test_main_no_args_outputs_click_docs_reference(self):
        result = self.runner.invoke(main)
        self.assertIn("click.palletsprojects.com", result.output)

    def test_main_help_flag_shows_help(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Console script for geemap", result.output)

    def test_main_help_flag_shows_usage(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertIn("Usage:", result.output)


if __name__ == "__main__":
    unittest.main()
