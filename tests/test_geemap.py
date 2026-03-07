#!/usr/bin/env python
"""Tests for `geemap` package."""

import unittest
from unittest.mock import patch, MagicMock

import ee
import ipyleaflet
import geemap

class TestGeemap(unittest.TestCase):
    """Tests for `geemap` package."""

    @patch('geemap.coreutils.ee_initialize')
    @patch('ee.Reducer.mean')
    def test_map_init(self, mock_mean, mock_init):
        m = geemap.Map(ee_initialize=True)
        self.assertIsInstance(m, ipyleaflet.Map)
        mock_init.assert_called_once()
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
        m.ee_layers = {"test_layer": {"ee_object": MagicMock(spec=ee.Image), "ee_layer": MagicMock()}}
        self.assertIn("test_layer", m.ee_raster_layers)
        self.assertNotIn("test_layer", m.ee_vector_layers)

        m.ee_layers = {"test_vector": {"ee_object": MagicMock(spec=ee.Feature), "ee_layer": MagicMock()}}
        self.assertIn("test_vector", m.ee_vector_layers)
        self.assertNotIn("test_vector", m.ee_raster_layers)

    def test_add_basemap(self):
        m = geemap.Map(ee_initialize=False)
        m.add_basemap("ROADMAP")
        layer_names = m.get_layer_names()
        self.assertTrue(len(layer_names) > 0)

    def test_add(self):
        m = geemap.Map(ee_initialize=False)
        # Assuming search_control was added via config to map controls when we add it explicitly or we test adding a built-in control string.
        m.add("layer_ctrl")
        self.assertTrue(any(isinstance(c, ipyleaflet.LayersControl) for c in m.controls))

    def test_zoom_to_bounds(self):
        m = geemap.Map(ee_initialize=False)
        m.fit_bounds = MagicMock()
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

if __name__ == "__main__":
    unittest.main()
