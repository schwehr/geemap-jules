import unittest
from unittest import mock
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

    def test_map_init_more_options(self):
        m = foliumap.Map(ee_initialize=False, add_google_map=True, plugin_LatLngPopup=True, plugin_Fullscreen=True, plugin_Draw=True, Draw_export=True, plugin_MiniMap=True, plugin_LayerControl=True, locate_control=True, search_control=True, height=500, width="50%", tiles="OpenStreetMap", basemap="HYBRID")
        self.assertIsInstance(m, folium.Map)
        self.assertEqual(m.options["zoom"], 2)

    def test_map_init_width_px(self):
        m = foliumap.Map(ee_initialize=False, width="500px")
        self.assertIsInstance(m, folium.Map)

    def test_set_options(self):
        m = foliumap.Map(ee_initialize=False)
        m.setOptions("SATELLITE")
        m.setOptions(mapTypeId="TERRAIN")
        m.setOptions(styles={}, types=[])

    def test_add_basemap_dict(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_basemap({"HYBRID": "url"})

    def test_add_layer(self):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch("geemap.ee_tile_layers.EEFoliumTileLayer") as MockLayer:
            mock_layer = mock.Mock()
            mock_layer.url_format = "mock_url"
            MockLayer.return_value = mock_layer
            m.add_layer(mock.Mock(), {}, "Test Layer")
            mock_layer.add_to.assert_called_once_with(m)

    def test_repr_mimebundle(self):
        m = foliumap.Map(ee_initialize=False)
        m.options["layersControl"] = True
        with mock.patch.object(m, "add_layer_control") as mock_add_layer_control:
            m._repr_mimebundle_()
            mock_add_layer_control.assert_called_once()

    def test_set_center(self):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "fit_bounds") as mock_fit_bounds:
            m.set_center(10, 20, 5)
            mock_fit_bounds.assert_called_once_with([[20, 10], [20, 10]], max_zoom=5)

    def test_zoom_to_bounds(self):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "fit_bounds") as mock_fit_bounds:
            m.zoom_to_bounds([1, 2, 3, 4])
            mock_fit_bounds.assert_called_once_with([[2, 1], [4, 3]])

    def test_zoom_to_gdf(self):
        m = foliumap.Map(ee_initialize=False)
        mock_gdf = mock.Mock()
        mock_gdf.total_bounds = [1, 2, 3, 4]
        with mock.patch.object(m, "zoom_to_bounds") as mock_zoom_to_bounds:
            m.zoom_to_gdf(mock_gdf)
            mock_zoom_to_bounds.assert_called_once_with([1, 2, 3, 4])

    def test_center_object_zoom(self):
        m = foliumap.Map(ee_initialize=False)
        mock_ee_object = mock.Mock()
        mock_geom = mock.Mock()
        mock_ee_object.geometry.return_value = mock_geom
        mock_geom.transform.return_value = mock_geom
        mock_geom.centroid.return_value.getInfo.return_value = {"coordinates": [10, 20]}
        with mock.patch.object(m, "set_center") as mock_set_center:
            m.center_object(mock_ee_object, zoom=5)
            mock_set_center.assert_called_once_with(10, 20, 5)

    def test_center_object_no_zoom(self):
        m = foliumap.Map(ee_initialize=False)
        mock_ee_object = mock.Mock()
        mock_geom = mock.Mock()
        mock_ee_object.geometry.return_value = mock_geom
        mock_geom.transform.return_value = mock_geom
        mock_geom.bounds.return_value.getInfo.return_value = {"coordinates": [[[10, 20], [10, 30], [20, 30], [20, 20]]]}
        with mock.patch.object(m, "fit_bounds") as mock_fit_bounds:
            m.center_object(mock_ee_object)
            mock_fit_bounds.assert_called_once_with([[20, 10], [30, 20]])

    def test_add_wms_layer(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_wms_layer("url", "layer", "name", attribution="attr", shown=False)

    def test_add_tile_layer(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_tile_layer("url", "name", attribution="attr", shown=False, opacity=0.5)

    @mock.patch("geemap.foliumap.cog_bounds")
    @mock.patch("geemap.foliumap.cog_tile")
    def test_add_cog_layer(self, mock_cog_tile, mock_cog_bounds):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
            mock_cog_tile.return_value = "cog_url"
            mock_cog_bounds.return_value = [0, 0, 10, 10]
            m.add_cog_layer("http://cog_url", name="cog", attribution="attr", opacity=0.5)
            mock_cog_tile.assert_called_once()
            mock_add_tile_layer.assert_called_once()

    @mock.patch("geemap.foliumap.stac_bounds")
    @mock.patch("geemap.foliumap.stac_tile")
    def test_add_stac_layer(self, mock_stac_tile, mock_stac_bounds):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
            mock_stac_tile.return_value = "stac_url"
            mock_stac_bounds.return_value = [0, 0, 10, 10]
            m.add_stac_layer("http://stac_url", collection="col", items="item", assets="asset", name="stac")
            mock_stac_tile.assert_called_once()
            mock_add_tile_layer.assert_called_once()

    @mock.patch("geemap.foliumap.create_legend")
    def test_add_legend(self, mock_create_legend):
        mock_create_legend.return_value = "Legend HTML"
        m = foliumap.Map(ee_initialize=False)
        m.add_legend(title="Legend", builtin_legend="NLCD")

    def test_add_colorbar(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_colorbar(vis_params={"palette": ["#ff0000", "#00ff00", "#0000ff"], "min": 0, "max": 100})

    def test_add_geojson(self):
        m = foliumap.Map(ee_initialize=False)
        m.add_geojson({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": "Test"}, "geometry": {"type": "Point", "coordinates": [0, 0]}}]}, layer_name="Test")

    @mock.patch("os.path.exists")
    @mock.patch("geemap.foliumap.shp_to_geojson")
    @mock.patch("folium.GeoJson")
    def test_add_shapefile(self, mock_geojson, mock_shp_to_geojson, mock_exists):
        m = foliumap.Map(ee_initialize=False)
        mock_exists.return_value = True
        mock_shp_to_geojson.return_value = {"type": "FeatureCollection", "features": []}
        m.add_shapefile("test.shp", layer_name="Test")
        mock_geojson.assert_called_once()
        mock_geojson.return_value.add_to.assert_called_once_with(m)

if __name__ == "__main__":
    unittest.main()
