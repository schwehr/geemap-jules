#!/usr/bin/env python
"""Tests for `geemap` package."""

import unittest
from unittest import mock

import ee
import ipyleaflet
import geemap


class TestGeemap(unittest.TestCase):
    """Tests for `geemap` package."""

    @mock.patch.object(geemap.coreutils, "ee_initialize")
    @mock.patch.object(ee.Reducer, "mean")
    def test_map_init(self, mock_mean, mock_init):
        m = geemap.Map(ee_initialize=True)
        self.assertIsInstance(m, ipyleaflet.Map)
        mock_init.assert_called_once()
        # ee.Reducer.mean is called during initialization to set the default roi_reducer
        mock_mean.assert_called_once()

    def test_map_properties(self):
        m = geemap.Map(ee_initialize=False)
        self.assertIsInstance(m.draw_control, geemap.core.MapDrawControl)
        self.assertIsInstance(m.draw_control_lite, geemap.core.MapDrawControl)

    def test_control_config(self):
        m = geemap.Map(ee_initialize=False, lite_mode=True)
        config = m._control_config()
        self.assertIn("zoom_control", config["topleft"])

        m2 = geemap.Map(ee_initialize=False, lite_mode=False)
        config2 = m2._control_config()
        self.assertIn("search_ctrl", config2["topleft"])

    def test_layer_dict_properties(self):
        m = geemap.Map(ee_initialize=False)
        m.ee_layers = {
            "test_layer": {
                "ee_object": mock.MagicMock(spec=ee.Image),
                "ee_layer": mock.MagicMock(),
            }
        }
        self.assertIn("test_layer", m.ee_raster_layers)
        self.assertNotIn("test_layer", m.ee_vector_layers)

        m.ee_layers = {
            "test_vector": {
                "ee_object": mock.MagicMock(spec=ee.Feature),
                "ee_layer": mock.MagicMock(),
            }
        }
        self.assertIn("test_vector", m.ee_vector_layers)
        self.assertNotIn("test_vector", m.ee_raster_layers)

    def test_add_basemap(self):
        m = geemap.Map(ee_initialize=False)
        m.add_basemap("ROADMAP")
        layer_names = m.get_layer_names()
        self.assertTrue(len(layer_names) > 0)

    def test_add(self):
        m = geemap.Map(ee_initialize=False)
        # Assuming search_control was added via config to map controls when
        # we add it explicitly or we test adding a built-in control string.
        m.add("layer_ctrl")
        self.assertTrue(
            any(isinstance(c, ipyleaflet.LayersControl) for c in m.controls)
        )

    def test_zoom_to_bounds(self):
        m = geemap.Map(ee_initialize=False)
        m.fit_bounds = mock.MagicMock()
        m.zoom_to_bounds([1, 2, 3, 4])
        m.fit_bounds.assert_called_once_with([[2, 1], [4, 3]])

    def test_get_scale(self):
        m = geemap.Map(ee_initialize=False)
        scale = m.get_scale()
        self.assertIsInstance(scale, float)

    def test_set_center(self):
        m = geemap.Map(ee_initialize=False)
        m.set_center(0, 0, 2)
        self.assertEqual(m.center, [0, 0])
        self.assertEqual(m.zoom, 2)

    def test_add_ee_layer(self):
        from tests import fake_ee

        m = geemap.Map(ee_initialize=False)
        img = fake_ee.Image()

        class MockEELeafletTileLayer:
            EE_TYPES = (fake_ee.Image, fake_ee.ImageCollection, type(mock.MagicMock()))

            def __init__(self, *args, **kwargs):
                self.url_format = "mock_url"

        with (
            mock.patch.object(
                geemap.core.ee_tile_layers, "EELeafletTileLayer", MockEELeafletTileLayer
            ),
            mock.patch.object(geemap.geemap, "arc_add_layer") as mock_arc_add_layer,
            mock.patch.object(geemap.geemap.ee, "Image", fake_ee.Image),
            mock.patch.object(
                geemap.geemap.ee, "ImageCollection", fake_ee.ImageCollection
            ),
        ):
            m.add_ee_layer(img, name="test_layer")
            self.assertIn("test_layer", m.ee_layers)
            self.assertEqual(m.ee_layers["test_layer"]["ee_object"], img)
            mock_arc_add_layer.assert_called_once_with(
                "mock_url", "test_layer", True, 1.0
            )

            # Test plot dropdown
            m._plot_dropdown_widget = mock.MagicMock()
            m.add_ee_layer(img, name="test_layer_2")
            self.assertIn("test_layer_2", m._plot_dropdown_widget.options)

            # Update an existing layer to test `layer is not None` condition
            m.add_ee_layer(img, name="test_layer_2")

    def test_remove_ee_layer(self):
        from tests import fake_ee

        m = geemap.Map(ee_initialize=False)
        m.ee_layers = {
            "test_layer": {
                "ee_object": fake_ee.Image(),
                "ee_layer": "mock_ee_layer",
            }
        }

        with mock.patch.object(
            geemap.Map, "layers", new_callable=mock.PropertyMock
        ) as mock_layers:
            mock_layers.return_value = ["mock_ee_layer"]
            with mock.patch.object(m, "remove_layer") as mock_remove_layer:
                m.remove_ee_layer("test_layer")
                self.assertNotIn("test_layer", m.ee_layers)
                mock_remove_layer.assert_called_once_with("mock_ee_layer")

                # test remove non-existent
                m.remove_ee_layer("not_exist")


if __name__ == "__main__":
    unittest.main()
