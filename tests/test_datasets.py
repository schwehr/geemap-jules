"""Tests for `datasets` module."""

import os
import unittest
from unittest import mock

import ee

from geemap import datasets


class DatasetsTest(unittest.TestCase):
    """Tests for `datasets` module."""

    def test_get_data_csv(self):
        data_csv = datasets.get_data_csv()
        self.assertTrue(os.path.exists(data_csv))
        self.assertEqual(os.path.basename(data_csv), "ee_data_catalog.csv")

    @mock.patch.object(ee, "ImageCollection")
    def test_get_ee_image_collection(self, mock_image_collection):
        """Test getting an Earth Engine ImageCollection."""
        mock_instance = mock.MagicMock()
        mock_image_collection.return_value = mock_instance

        asset_id = "COPERNICUS/S2_SR"
        result = datasets.get_ee_image_collection(asset_id)

        mock_image_collection.assert_called_once_with(asset_id)
        self.assertEqual(result, mock_instance)


if __name__ == "__main__":
    unittest.main()
