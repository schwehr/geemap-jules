"""Tests for the plotlymap module."""

import unittest
from unittest import mock

import pandas as pd

try:
    from plotly import graph_objects as go
    from geemap import plotlymap

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@unittest.skipUnless(PLOTLY_AVAILABLE, "plotly not available")
class PlotlymapTest(unittest.TestCase):

    @mock.patch("geemap.coreutils.ee_initialize")
    def test_map_init_ee_initialize(self, mock_ee_initialize):
        m = plotlymap.Map(ee_initialize=True)
        mock_ee_initialize.assert_called_once()
        self.assertEqual(m.layout.mapbox.center.lat, 20)
        self.assertEqual(m.layout.mapbox.center.lon, 0)

    def test_map_init_default_params(self):
        m = plotlymap.Map(ee_initialize=False)
        self.assertEqual(m.layout.mapbox.center.lat, 20)
        self.assertEqual(m.layout.mapbox.center.lon, 0)
        self.assertEqual(m.layout.mapbox.zoom, 1)
        self.assertEqual(m.layout.mapbox.style, "open-street-map")
        self.assertEqual(m.layout.height, 600)
        self.assertEqual(len(m.data), 1)
        self.assertEqual(m.get_layers(), {})
        self.assertEqual(m.get_tile_layers(), {})
        self.assertEqual(m.get_data_layers(), {})
        self.assertIsNone(m.find_layer_index("nonexistent"))

    def test_map_init_custom_center(self):
        m = plotlymap.Map(center=(40, -100), ee_initialize=False)
        self.assertEqual(m.layout.mapbox.center.lat, 40)
        self.assertEqual(m.layout.mapbox.center.lon, -100)

    def test_map_init_custom_zoom(self):
        m = plotlymap.Map(zoom=10, ee_initialize=False)
        self.assertEqual(m.layout.mapbox.zoom, 10)

    def test_map_init_custom_height(self):
        m = plotlymap.Map(height=800, ee_initialize=False)
        self.assertEqual(m.layout.height, 800)

    def test_map_init_custom_basemap(self):
        m = plotlymap.Map(basemap="carto-positron", ee_initialize=False)
        self.assertEqual(m.layout.mapbox.style, "carto-positron")

    def test_set_center_with_zoom(self):
        m = plotlymap.Map(ee_initialize=False)
        m.set_center(lat=37.8, lon=-122.4, zoom=12)
        self.assertEqual(m.layout.mapbox.center.lat, 37.8)
        self.assertEqual(m.layout.mapbox.center.lon, -122.4)
        self.assertEqual(m.layout.mapbox.zoom, 12)

    def test_set_center_without_zoom(self):
        m = plotlymap.Map(ee_initialize=False)
        m.set_center(lat=37.8, lon=-122.4)
        self.assertEqual(m.layout.mapbox.center.lat, 37.8)
        self.assertEqual(m.layout.mapbox.center.lon, -122.4)
        self.assertEqual(m.layout.mapbox.zoom, 1)

    def test_add_controls_string_and_list(self):
        m = plotlymap.Map(ee_initialize=False)
        m.add_controls("drawline")
        self.assertIn("drawline", m.layout.modebar.add)
        m.add_controls(["drawline", "drawopenpath"])
        self.assertIn("drawopenpath", m.layout.modebar.add)

    def test_add_controls_invalid_type_raises(self):
        m = plotlymap.Map(ee_initialize=False)
        with self.assertRaises(ValueError):
            m.add_controls(12345)

    def test_remove_controls_string_and_list(self):
        m = plotlymap.Map(ee_initialize=False)
        m.remove_controls("zoomin")
        self.assertIn("zoomin", m.layout.modebar.remove)
        m.remove_controls(["zoomin", "zoomout"])
        self.assertIn("zoomout", m.layout.modebar.remove)

    def test_remove_controls_invalid_type_raises(self):
        m = plotlymap.Map(ee_initialize=False)
        with self.assertRaises(ValueError):
            m.remove_controls(12345)

    def test_add_tile_layer(self):
        m = plotlymap.Map(ee_initialize=False)
        m.add_tile_layer(
            url="https://tile.example.com/{z}/{x}/{y}.png",
            name="Test Layer",
        )
        self.assertIn("Test Layer", m.get_tile_layers())

    def test_add_layer(self):
        m = plotlymap.Map(ee_initialize=False)
        layer = go.Scattermapbox(lat=[37.8], lon=[-122.4])
        m.add_layer(layer, name="My Layer")
        self.assertIn("My Layer", m.get_data_layers())

    def test_find_layer_index_data_layer(self):
        m = plotlymap.Map(ee_initialize=False)
        layer = go.Scattermapbox(lat=[37.8], lon=[-122.4], name="pts")
        m.add_layer(layer)
        self.assertEqual(m.find_layer_index("pts"), 1)

    def test_clear_layers_keeps_basemap(self):
        m = plotlymap.Map(ee_initialize=False)
        layer = go.Scattermapbox(lat=[37.8], lon=[-122.4], name="extra")
        m.add_layer(layer)
        m.clear_layers()
        self.assertEqual(len(m.data), 1)

    def test_clear_layers_with_basemap(self):
        m = plotlymap.Map(ee_initialize=False)
        m.clear_layers(clear_basemap=True)
        self.assertEqual(len(m.data), 0)

    def test_add_heatmap_dataframe(self):
        m = plotlymap.Map(ee_initialize=False)
        df = pd.DataFrame(
            {
                "latitude": [37.8, 37.7],
                "longitude": [-122.4, -122.3],
                "value": [1.0, 0.5],
            }
        )
        m.add_heatmap(df)
        self.assertEqual(len(m.data), 2)

    def test_add_heatmap_invalid_data_raises(self):
        m = plotlymap.Map(ee_initialize=False)
        with self.assertRaises(ValueError):
            m.add_heatmap({"invalid": "data"})

    def test_map_show(self):
        m = plotlymap.Map(ee_initialize=False)
        canvas_widget = m.show(toolbar=True)
        self.assertIsNotNone(canvas_widget)
        # Without toolbar, it should call super().show() which returns None implicitly or a plotly figure object depending on the env
        # In testing context it usually returns None
        ret = m.show(toolbar=False)
        self.assertIsNone(ret)

    def test_clear_controls(self):
        m = plotlymap.Map(ee_initialize=False)
        # Mock the super().show or Map.show to just test it is called correctly
        with mock.patch.object(plotlymap.Map, "show") as mock_show:
            m.clear_controls()
            mock_show.assert_called_once()
            args, kwargs = mock_show.call_args
            self.assertFalse(kwargs.get("toolbar"))
            self.assertEqual(kwargs.get("config").get("displayModeBar"), False)

    def test_add_basemap_invalid_raises(self):
        m = plotlymap.Map(ee_initialize=False)
        with self.assertRaises(ValueError):
            m.add_basemap("INVALID_BASEMAP_XYZ")

    def test_add_basemap_already_present(self):
        m = plotlymap.Map(ee_initialize=False)
        # Ensure it is empty first
        m.layout.mapbox.layers = []
        m.add_basemap("ROADMAP")
        self.assertEqual(len(m.layout.mapbox.layers), 1)
        # Add again, should remove and add
        m.add_basemap("ROADMAP")
        self.assertEqual(len(m.layout.mapbox.layers), 1)
        self.assertEqual(m.layout.mapbox.layers[0]["name"], "ROADMAP")

    def test_remove_basemap(self):
        m = plotlymap.Map(ee_initialize=False)
        m.layout.mapbox.layers = []
        m.add_basemap("ROADMAP")
        self.assertEqual(len(m.layout.mapbox.layers), 1)
        m.remove_basemap("ROADMAP")
        self.assertEqual(len(m.layout.mapbox.layers), 0)

    def test_add_mapbox_layer(self):
        m = plotlymap.Map(ee_initialize=False)
        m.add_mapbox_layer(style="streets", access_token="test_token")
        self.assertEqual(m.layout.mapbox.style, "streets")
        self.assertEqual(m.layout.mapbox.accesstoken, "test_token")

    def test_add_ee_layer_invalid_type_raises(self):
        m = plotlymap.Map(ee_initialize=False)
        with self.assertRaises(AttributeError):
            m.add_ee_layer("not_an_ee_object")

    def test_add_ee_layer_image(self):
        from . import fake_ee
        m = plotlymap.Map(ee_initialize=False)
        img = fake_ee.Image()
        with mock.patch("geemap.plotlymap.ee.Image", fake_ee.Image), \
             mock.patch("geemap.plotlymap.ee.ImageCollection", fake_ee.ImageCollection), \
             mock.patch("geemap.plotlymap.ee.FeatureCollection", fake_ee.FeatureCollection), \
             mock.patch("geemap.plotlymap.ee.Feature", fake_ee.Feature), \
             mock.patch("geemap.plotlymap.ee.Geometry", fake_ee.Geometry):

            m.add_ee_layer(img, name="fake_ee_img")
            self.assertIn("fake_ee_img", m.get_tile_layers())

    def test_addlayer_alias(self):
        m = plotlymap.Map(ee_initialize=False)
        self.assertEqual(m.addLayer, m.add_ee_layer)

    @mock.patch("geemap.plotlymap.cog_tile")
    @mock.patch("geemap.plotlymap.cog_center")
    def test_add_cog_layer(self, mock_cog_center, mock_cog_tile):
        mock_cog_tile.return_value = "https://example.com/cog_tile.png"
        mock_cog_center.return_value = (-100, 40)

        m = plotlymap.Map(ee_initialize=False)
        m.add_cog_layer(url="fake_url", name="cog_test")

        mock_cog_tile.assert_called_once()
        mock_cog_center.assert_called_once()
        self.assertIn("cog_test", m.get_tile_layers())
        self.assertEqual(m.layout.mapbox.center.lon, -100)
        self.assertEqual(m.layout.mapbox.center.lat, 40)

    @mock.patch("geemap.plotlymap.stac_tile")
    @mock.patch("geemap.plotlymap.stac_center")
    def test_add_stac_layer(self, mock_stac_center, mock_stac_tile):
        mock_stac_tile.return_value = "https://example.com/stac_tile.png"
        mock_stac_center.return_value = (-100, 40)

        m = plotlymap.Map(ee_initialize=False)
        m.add_stac_layer(url="fake_url", name="stac_test")

        mock_stac_tile.assert_called_once()
        mock_stac_center.assert_called_once()
        self.assertIn("stac_test", m.get_tile_layers())
        self.assertEqual(m.layout.mapbox.center.lon, -100)
        self.assertEqual(m.layout.mapbox.center.lat, 40)


    @mock.patch("geemap.plotlymap.planet_by_month")
    def test_add_planet_by_month(self, mock_planet_by_month):
        mock_planet_by_month.return_value = "https://example.com/planet_month.png"

        m = plotlymap.Map(ee_initialize=False)
        with mock.patch("os.environ.get", return_value="fake_planet_key"):
            m.add_planet_by_month(year=2020, month=5)

            # geemap passes the API key if provided, or defaults to the token_name (which gets fetched by planet_by_month)
            # wait, inspecting geemap.plotlymap:
            # tile_url = planet_by_month(year, month, api_key, token_name)
            mock_planet_by_month.assert_called_once_with(2020, 5, None, "PLANET_API_KEY")
            self.assertIn("2020-05", m.get_tile_layers())

    @mock.patch("geemap.plotlymap.planet_by_quarter")
    def test_add_planet_by_quarter(self, mock_planet_by_quarter):
        mock_planet_by_quarter.return_value = "https://example.com/planet_quarter.png"

        m = plotlymap.Map(ee_initialize=False)
        with mock.patch("os.environ.get", return_value="fake_planet_key"):
            m.add_planet_by_quarter(year=2020, quarter=2)

            mock_planet_by_quarter.assert_called_once_with(2020, 2, None, "PLANET_API_KEY")
            self.assertIn("2020-q2", m.get_tile_layers())

    @mock.patch("geemap.plotlymap.json.loads")
    def test_add_choropleth_map(self, mock_json_loads):
        try:
            import geopandas as gpd
            from shapely.geometry import Point

            # Create a mock GeoDataFrame
            df = pd.DataFrame({"value": [1, 2]})
            geometry = [Point(0, 0), Point(1, 1)]
            gdf = gpd.GeoDataFrame(df, geometry=geometry)
            gdf.crs = "EPSG:4326"

            with mock.patch("geopandas.read_file") as mock_read_file:
                mock_read_file.return_value = gdf
                mock_json_loads.return_value = {"type": "FeatureCollection", "features": []}

                m = plotlymap.Map(ee_initialize=False)
                # Plotly's graph_objects uses add_choroplethmapbox automatically via validation, or it might just use it directly, but in Map class:
                # `self.add_choroplethmapbox` is inherited from `go.FigureWidget`
                with mock.patch.object(m, "add_choroplethmapbox") as mock_add_choropleth:
                    m.add_choropleth_map("fake_data.geojson", name="choro_test", z="value")
                    mock_read_file.assert_called_once_with("fake_data.geojson")
                    mock_add_choropleth.assert_called_once()
                    _, kwargs = mock_add_choropleth.call_args
                    self.assertEqual(kwargs.get("name"), "choro_test")
        except ImportError:
            pass  # Skip if geopandas is missing

    def test_add_scatter_plot_demo(self):
        m = plotlymap.Map(ee_initialize=False)
        m.add_scatter_plot_demo()
        self.assertEqual(len(m.data), 2)  # Base trace + scatter trace
        self.assertEqual(m.data[-1].name, "Random points")

    @mock.patch("pandas.read_csv")
    def test_add_heatmap_demo(self, mock_read_csv):
        # Create a dummy dataframe for earthquakes
        df = pd.DataFrame({
            "Latitude": [34.0, 35.0],
            "Longitude": [-118.0, -119.0],
            "Magnitude": [5.0, 6.0]
        })
        mock_read_csv.return_value = df

        m = plotlymap.Map(ee_initialize=False)
        # Mocking add_basemap so we don't have to worry about missing 'Esri.WorldTopoMap'
        with mock.patch.object(m, "add_basemap") as mock_add_basemap:
            m.add_heatmap_demo()
            mock_read_csv.assert_called_once()
            self.assertIn("Earthquake", m.get_data_layers())
            mock_add_basemap.assert_called_once_with("Esri.WorldTopoMap")

    @mock.patch("geemap.plotlymap.px.choropleth_mapbox")
    def test_add_gdf(self, mock_px_choropleth):
        try:
            import geopandas as gpd
            from shapely.geometry import Point

            df = pd.DataFrame({"color_val": [10, 20], "label_col": ["A", "B"]})
            geometry = [Point(0, 0), Point(1, 1)]
            gdf = gpd.GeoDataFrame(df, geometry=geometry)
            gdf.crs = "EPSG:4326"

            # Mock the figure returned by px.choropleth_mapbox
            class DummyFig:
                data = [{"type": "choroplethmapbox", "name": "gdf_trace"}]
            mock_px_choropleth.return_value = DummyFig()

            m = plotlymap.Map(ee_initialize=False)
            m.add_gdf(gdf, label_col="label_col", color_col="color_val")

            mock_px_choropleth.assert_called_once()
            self.assertEqual(m.data[-1].name, "gdf_trace")
        except ImportError:
            pass  # Skip if geopandas is missing

    def test_save(self):
        m = plotlymap.Map(ee_initialize=False)
        with mock.patch.object(m, "write_image") as mock_write_image:
            m.save("test.png", format="png", width=800, height=600)
            mock_write_image.assert_called_once_with("test.png", format="png", width=800, height=600, scale=None)


    @mock.patch("shutil.copyfile")
    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="if not BaseFigure._is_key_path_compatible(key_path_str, self.layout):")
    @mock.patch("os.path.join")
    def test_fix_widget_error(self, mock_path_join, mock_file, mock_copyfile):
        def join_side_effect(*args):
            return "/".join(args)
        mock_path_join.side_effect = join_side_effect

        # Need to patch os.path.dirname and os.__file__ to control the root path
        with mock.patch("os.path.dirname", return_value="fake_dir"), mock.patch("geemap.plotlymap.os.__file__", "fake_file.py"):
            plotlymap.fix_widget_error()

            expected_path = "fake_dir/site-packages/plotly/basedatatypes.py"
            expected_bk_path = "fake_dir/site-packages/plotly/basedatatypes_bk.py"

            mock_copyfile.assert_called_once_with(expected_path, expected_bk_path)

            # Check that open was called to read and write
            mock_file.assert_any_call(expected_path)
            mock_file.assert_any_call(expected_path, "w")

            # Verify write was called with the replacement text
        handle = mock_file()
        expected_replace = """if not BaseFigure._is_key_path_compatible(key_path_str, self.layout):
                if key_path_str == "mapbox._derived":
                    return"""
        handle.write.assert_called_once_with(expected_replace)


    def test_remove_layer(self):
        m = plotlymap.Map(ee_initialize=False)
        m.add_tile_layer(
            url="https://tile.example.com/{z}/{x}/{y}.png",
            name="removable",
        )
        self.assertIn("removable", m.get_tile_layers())
        m.remove_layer("removable")
        self.assertNotIn("removable", m.get_tile_layers())

    def test_set_layer_visibility(self):
        m = plotlymap.Map(ee_initialize=False)
        layer = go.Scattermapbox(lat=[0], lon=[0], name="vis_test")
        m.add_layer(layer)
        m.set_layer_visibility("vis_test", show=False)
        index = m.find_layer_index("vis_test")
        self.assertFalse(m.data[index].visible)

    def test_set_layer_opacity(self):
        m = plotlymap.Map(ee_initialize=False)
        m.add_tile_layer(
            url="https://tile.example.com/{z}/{x}/{y}.png",
            name="opacity_test",
        )
        m.set_layer_opacity("opacity_test", opacity=0.5)
        index = m.find_layer_index("opacity_test")
        self.assertEqual(m.layout.mapbox.layers[index].opacity, 0.5)

    def test_canvas_init(self):
        m = plotlymap.Map(ee_initialize=False)
        canvas = plotlymap.Canvas(m)
        self.assertEqual(canvas.map, m)
        self.assertEqual(canvas.map_min_width, "90%")
        self.assertEqual(canvas.map_max_width, "98%")
        self.assertFalse(canvas.map_refresh)

    def test_canvas_toolbar_reset(self):
        import ipywidgets

        m = plotlymap.Map(ee_initialize=False)
        canvas = plotlymap.Canvas(m)

        # Mocking the toolbar and its children.
        tool1 = ipywidgets.ToggleButton(value=True)
        tool2 = ipywidgets.ToggleButton(value=True)
        toolbar_grid = ipywidgets.VBox([tool1, tool2])
        canvas._toolbar = toolbar_grid

        canvas.toolbar_reset()

        self.assertFalse(tool1.value)
        self.assertFalse(tool2.value)


if __name__ == "__main__":
    unittest.main()
