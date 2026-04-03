"""Tests for `datasets` module."""

import os
import unittest

from unittest import mock
from geemap import datasets


class DatasetsTest(unittest.TestCase):
    """Tests for `datasets` module."""

    def test_get_data_csv(self):
        data_csv = datasets.get_data_csv()
        self.assertTrue(os.path.exists(data_csv))
        self.assertEqual(os.path.basename(data_csv), "ee_data_catalog.csv")

    @mock.patch.object(datasets, "get_ee_stac_list")
    @mock.patch.object(datasets, "get_geemap_data_list")
    @mock.patch.object(datasets, "get_community_data_list")
    def test_get_data_list(
        self, mock_get_community, mock_get_geemap, mock_get_ee_stac
    ):
        mock_get_ee_stac.return_value = ["stac1", "stac2"]
        mock_get_geemap.return_value = ["geemap1", "geemap2"]
        mock_get_community.return_value = ["community1", "community2"]

        result = datasets.get_data_list()

        self.assertEqual(
            result,
            [
                "stac1",
                "stac2",
                "geemap1",
                "geemap2",
                "community1",
                "community2",
            ],
        )
        mock_get_ee_stac.assert_called_once()
        mock_get_geemap.assert_called_once()
        mock_get_community.assert_called_once()


if __name__ == "__main__":
    unittest.main()
