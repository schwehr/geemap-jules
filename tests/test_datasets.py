"""Tests for `datasets` module."""

import os
import unittest

from geemap import datasets


class DatasetsTest(unittest.TestCase):
    """Tests for `datasets` module."""

    def test_get_data_csv(self):
        data_csv = datasets.get_data_csv()
        self.assertTrue(os.path.exists(data_csv))
        self.assertEqual(os.path.basename(data_csv), "ee_data_catalog.csv")

    def test_merge_dict(self):
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": 3, "d": 4}
        expected = {"a": 1, "b": 3, "d": 4}
        self.assertEqual(datasets.merge_dict(dict1, dict2), expected)

        dict3 = {}
        self.assertEqual(datasets.merge_dict(dict1, dict3), dict1)
        self.assertEqual(datasets.merge_dict(dict3, dict2), dict2)

        dict4 = {"a": {"b": 1}}
        dict5 = {"a": {"c": 2}}
        expected_nested = {"a": {"b": 1, "c": 2}}
        self.assertEqual(datasets.merge_dict(dict4, dict5), expected_nested)


if __name__ == "__main__":
    unittest.main()
