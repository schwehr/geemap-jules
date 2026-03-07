import unittest
import os

os.environ["USE_FOLIUM"] = "1"

import folium
import geemap
from geemap import foliumap

class TestFoliumap(unittest.TestCase):

    def test_map_init_default(self):
        m = foliumap.Map(ee_initialize=False)
        self.assertIsInstance(m, folium.Map)
        self.assertEqual(m.options["zoom"], 2)
        self.assertEqual(m.location, [20, 0])

    def test_map_init_custom_center(self):
        m = foliumap.Map(center=[40, -100], ee_initialize=False)
        self.assertEqual(m.location, [40, -100])

    def test_map_init_custom_zoom(self):
        m = foliumap.Map(zoom=10, ee_initialize=False)
        self.assertEqual(m.options["zoom"], 10)

    def test_add_basemap(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_basemap("ROADMAP")

    def test_add_marker(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_marker(location=[40, -100], popup="Test")

if __name__ == "__main__":
    unittest.main()
