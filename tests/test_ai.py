"""Tests for the AI module."""

import unittest

from click.testing import CliRunner

from geemap.cli import main

try:
    from geemap.ai import BBox

    HAS_BBOX = True
except ImportError:
    HAS_BBOX = False


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


@unittest.skipIf(not HAS_BBOX, "geemap[ai] dependencies not installed")
class TestBBox(unittest.TestCase):
    def test_bbox_to_list(self):
        bbox = BBox(west=-122.5, south=37.7, east=-122.3, north=37.8)
        self.assertEqual(bbox.to_list(), [-122.5, 37.7, -122.3, 37.8])

    def test_bbox_from_list(self):
        bbox_list = [-122.5, 37.7, -122.3, 37.8]
        bbox = BBox.from_list(bbox_list)
        self.assertEqual(bbox.west, -122.5)
        self.assertEqual(bbox.south, 37.7)
        self.assertEqual(bbox.east, -122.3)
        self.assertEqual(bbox.north, 37.8)

    def test_bbox_from_list_invalid_west_east(self):
        bbox_list = [-122.3, 37.7, -122.5, 37.8]
        with self.assertRaisesRegex(
            ValueError, r"The smaller \(west\) coordinate must be listed first"
        ):
            BBox.from_list(bbox_list)

    def test_bbox_from_list_invalid_south_north(self):
        bbox_list = [-122.5, 37.8, -122.3, 37.7]
        with self.assertRaisesRegex(
            ValueError, r"The smaller \(south\) coordinate must be listed first"
        ):
            BBox.from_list(bbox_list)

    def test_bbox_is_global_true(self):
        bbox = BBox(west=-180, south=-90, east=180, north=90)
        self.assertTrue(bbox.is_global())

    def test_bbox_is_global_false(self):
        bbox = BBox(west=-122.5, south=37.7, east=-122.3, north=37.8)
        self.assertFalse(bbox.is_global())

    def test_bbox_intersects_true(self):
        bbox1 = BBox(west=0, south=0, east=10, north=10)
        bbox2 = BBox(west=5, south=5, east=15, north=15)
        self.assertTrue(bbox1.intersects(bbox2))
        self.assertTrue(bbox2.intersects(bbox1))

    def test_bbox_intersects_false(self):
        bbox1 = BBox(west=0, south=0, east=10, north=10)
        bbox2 = BBox(west=11, south=11, east=20, north=20)
        self.assertFalse(bbox1.intersects(bbox2))
        self.assertFalse(bbox2.intersects(bbox1))

    def test_bbox_intersects_touching_false(self):
        bbox1 = BBox(west=0, south=0, east=10, north=10)
        bbox2 = BBox(west=10, south=10, east=20, north=20)
        self.assertFalse(bbox1.intersects(bbox2))
        self.assertFalse(bbox2.intersects(bbox1))


if __name__ == "__main__":
    unittest.main()
