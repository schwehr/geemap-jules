import re

with open("tests/test_foliumap.py", "r") as f:
    content = f.read()

replacements = [
    (
        '''    @mock.patch.object(foliumap.Map, "add_tile_layer")
    @mock.patch("geemap.foliumap.cog_bounds")
    @mock.patch("geemap.foliumap.cog_tile")
    def test_add_cog_layer(self, mock_cog_tile, mock_cog_bounds, mock_add_tile_layer):
        m = foliumap.Map(ee_initialize=False)
        mock_cog_tile.return_value = "cog_url"
        mock_cog_bounds.return_value = [0, 0, 10, 10]
        m.add_cog_layer("http://cog_url", name="cog", attribution="attr", opacity=0.5)
        mock_cog_tile.assert_called_once()
        mock_add_tile_layer.assert_called_once()''',
        '''    @mock.patch("geemap.foliumap.cog_bounds")
    @mock.patch("geemap.foliumap.cog_tile")
    def test_add_cog_layer(self, mock_cog_tile, mock_cog_bounds):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
            mock_cog_tile.return_value = "cog_url"
            mock_cog_bounds.return_value = [0, 0, 10, 10]
            m.add_cog_layer("http://cog_url", name="cog", attribution="attr", opacity=0.5)
            mock_cog_tile.assert_called_once()
            mock_add_tile_layer.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_tile_layer")
    @mock.patch("geemap.foliumap.stac_bounds")
    @mock.patch("geemap.foliumap.stac_tile")
    def test_add_stac_layer(self, mock_stac_tile, mock_stac_bounds, mock_add_tile_layer):
        m = foliumap.Map(ee_initialize=False)
        mock_stac_tile.return_value = "stac_url"
        mock_stac_bounds.return_value = [0, 0, 10, 10]
        m.add_stac_layer("http://stac_url", collection="col", items="item", assets="asset", name="stac")
        mock_stac_tile.assert_called_once()
        mock_add_tile_layer.assert_called_once()''',
        '''    @mock.patch("geemap.foliumap.stac_bounds")
    @mock.patch("geemap.foliumap.stac_tile")
    def test_add_stac_layer(self, mock_stac_tile, mock_stac_bounds):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
            mock_stac_tile.return_value = "stac_url"
            mock_stac_bounds.return_value = [0, 0, 10, 10]
            m.add_stac_layer("http://stac_url", collection="col", items="item", assets="asset", name="stac")
            mock_stac_tile.assert_called_once()
            mock_add_tile_layer.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.common.read_postgis")
    def test_add_gdf_from_postgis(self, mock_read_postgis, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_read_postgis.return_value = mock.Mock()
        m.add_gdf_from_postgis("sql", "con", layer_name="Test")
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.common.read_postgis")
    def test_add_gdf_from_postgis(self, mock_read_postgis):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_read_postgis.return_value = mock.Mock()
            m.add_gdf_from_postgis("sql", "con", layer_name="Test")
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_geojson")
    @mock.patch.object(foliumap.Map, "add_shapefile")
    @mock.patch.object(foliumap.Map, "add_kml")
    @mock.patch("geemap.foliumap.check_file_path")
    def test_add_data(self, mock_check_file_path, mock_add_kml, mock_add_shapefile, mock_add_geojson):
        m = foliumap.Map(ee_initialize=False)

        mock_check_file_path.return_value = "test.geojson"
        m.add_data("test.geojson", layer_name="Test")
        mock_add_geojson.assert_called_once()

        mock_check_file_path.return_value = "test.shp"
        m.add_data("test.shp", layer_name="Test")
        mock_add_shapefile.assert_called_once()

        mock_check_file_path.return_value = "test.kml"
        m.add_data("test.kml", layer_name="Test")
        mock_add_kml.assert_called_once()''',
        '''    def test_add_data(self):
        m = foliumap.Map(ee_initialize=False)

        with mock.patch("geemap.foliumap.check_file_path") as mock_check_file_path, mock.patch.object(m, "add_geojson") as mock_add_geojson:
            mock_check_file_path.return_value = "test.geojson"
            m.add_data("test.geojson", layer_name="Test")
            mock_add_geojson.assert_called_once()

        with mock.patch("geemap.foliumap.check_file_path") as mock_check_file_path, mock.patch.object(m, "add_shapefile") as mock_add_shapefile:
            mock_check_file_path.return_value = "test.shp"
            m.add_data("test.shp", layer_name="Test")
            mock_add_shapefile.assert_called_once()

        with mock.patch("geemap.foliumap.check_file_path") as mock_check_file_path, mock.patch.object(m, "add_kml") as mock_add_kml:
            mock_check_file_path.return_value = "test.kml"
            m.add_data("test.kml", layer_name="Test")
            mock_add_kml.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.common.xy_to_gdf")
    def test_add_points_from_xy(self, mock_xy_to_gdf, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_xy_to_gdf.return_value = mock.Mock()
        m.add_points_from_xy(mock.Mock(), x="x", y="y")
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.common.xy_to_gdf")
    def test_add_points_from_xy(self, mock_xy_to_gdf):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_xy_to_gdf.return_value = mock.Mock()
            m.add_points_from_xy(mock.Mock(), x="x", y="y")
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_place")
    def test_add_osm(self, mock_osm_gdf_from_place, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_place.return_value = mock.Mock()
        m.add_osm("place", which_result=1, by_osmid=False, buffer_dist=100)
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_place")
    def test_add_osm(self, mock_osm_gdf_from_place):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_place.return_value = mock.Mock()
            m.add_osm("place", which_result=1, by_osmid=False, buffer_dist=100)
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_geocode")
    def test_add_osm_from_geocode(self, mock_osm_gdf_from_geocode, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_geocode.return_value = mock.Mock()
        m.add_osm_from_geocode("query")
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_geocode")
    def test_add_osm_from_geocode(self, mock_osm_gdf_from_geocode):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_geocode.return_value = mock.Mock()
            m.add_osm_from_geocode("query")
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_address")
    def test_add_osm_from_address(self, mock_osm_gdf_from_address, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_address.return_value = mock.Mock()
        m.add_osm_from_address("address")
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_address")
    def test_add_osm_from_address(self, mock_osm_gdf_from_address):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_address.return_value = mock.Mock()
            m.add_osm_from_address("address")
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_place")
    def test_add_osm_from_place(self, mock_osm_gdf_from_place, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_place.return_value = mock.Mock()
        m.add_osm_from_place("query")
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_place")
    def test_add_osm_from_place(self, mock_osm_gdf_from_place):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_place.return_value = mock.Mock()
            m.add_osm_from_place("query")
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_point")
    def test_add_osm_from_point(self, mock_osm_gdf_from_point, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_point.return_value = mock.Mock()
        m.add_osm_from_point([0, 0])
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_point")
    def test_add_osm_from_point(self, mock_osm_gdf_from_point):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_point.return_value = mock.Mock()
            m.add_osm_from_point([0, 0])
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_polygon")
    def test_add_osm_from_polygon(self, mock_osm_gdf_from_polygon, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_polygon.return_value = mock.Mock()
        m.add_osm_from_polygon("polygon")
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_polygon")
    def test_add_osm_from_polygon(self, mock_osm_gdf_from_polygon):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_polygon.return_value = mock.Mock()
            m.add_osm_from_polygon("polygon")
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_gdf")
    @mock.patch("geemap.osm.osm_gdf_from_bbox")
    def test_add_osm_from_bbox(self, mock_osm_gdf_from_bbox, mock_add_gdf):
        m = foliumap.Map(ee_initialize=False)
        mock_osm_gdf_from_bbox.return_value = mock.Mock()
        m.add_osm_from_bbox(0, 1, 0, 1)
        mock_add_gdf.assert_called_once()''',
        '''    @mock.patch("geemap.osm.osm_gdf_from_bbox")
    def test_add_osm_from_bbox(self, mock_osm_gdf_from_bbox):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_gdf") as mock_add_gdf:
            mock_osm_gdf_from_bbox.return_value = mock.Mock()
            m.add_osm_from_bbox(0, 1, 0, 1)
            mock_add_gdf.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_tile_layer")
    @mock.patch("geemap.common.planet_tiles_by_month")
    def test_add_planet_by_month(self, mock_planet_tiles_by_month, mock_add_tile_layer):
        m = foliumap.Map(ee_initialize=False)
        mock_planet_tiles_by_month.return_value = "url"
        m.add_planet_by_month(year=2020, month=1)
        mock_planet_tiles_by_month.assert_called_once()
        mock_add_tile_layer.assert_called_once()''',
        '''    @mock.patch("geemap.common.planet_tiles_by_month")
    def test_add_planet_by_month(self, mock_planet_tiles_by_month):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
            mock_planet_tiles_by_month.return_value = "url"
            m.add_planet_by_month(year=2020, month=1)
            mock_planet_tiles_by_month.assert_called_once()
            mock_add_tile_layer.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "add_tile_layer")
    @mock.patch("geemap.common.planet_tiles_by_quarter")
    def test_add_planet_by_quarter(self, mock_planet_tiles_by_quarter, mock_add_tile_layer):
        m = foliumap.Map(ee_initialize=False)
        mock_planet_tiles_by_quarter.return_value = "url"
        m.add_planet_by_quarter(year=2020, quarter=1)
        mock_planet_tiles_by_quarter.assert_called_once()
        mock_add_tile_layer.assert_called_once()''',
        '''    @mock.patch("geemap.common.planet_tiles_by_quarter")
    def test_add_planet_by_quarter(self, mock_planet_tiles_by_quarter):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
            mock_planet_tiles_by_quarter.return_value = "url"
            m.add_planet_by_quarter(year=2020, quarter=1)
            mock_planet_tiles_by_quarter.assert_called_once()
            mock_add_tile_layer.assert_called_once()'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "save")
    @mock.patch("os.path.abspath")
    def test_to_html(self, mock_abspath, mock_save):
        m = foliumap.Map(ee_initialize=False)
        mock_abspath.return_value = "test.html"
        m.to_html("test.html")
        mock_save.assert_called_once_with("test.html", close_file=False)''',
        '''    @mock.patch("os.path.abspath")
    def test_to_html(self, mock_abspath):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "save") as mock_save:
            mock_abspath.return_value = "test.html"
            m.to_html("test.html")
            mock_save.assert_called_once_with("test.html", close_file=False)'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "static_map")
    def test_static_map(self, mock_static_map):
        m = foliumap.Map(ee_initialize=False)
        m.static_map()
        mock_static_map.assert_called_once()''',
        '''    def test_static_map(self):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "static_map") as mock_static_map:
            m.static_map()
            mock_static_map.assert_called_once()'''
    ),
    (
        '''    @mock.patch("folium.raster_layers.ImageOverlay")
    @mock.patch("geemap.foliumap.image_overlay")
    def test_image_overlay(self, mock_io, mock_image_overlay):
        m = foliumap.Map(ee_initialize=False)
        m.image_overlay("url", [[0, 0], [1, 1]])
        mock_io.assert_called_once()''',
        '''    @mock.patch("folium.raster_layers.ImageOverlay")
    def test_image_overlay(self, mock_image_overlay):
        m = foliumap.Map(ee_initialize=False)
        m.image_overlay("url", [[0, 0], [1, 1]])
        mock_image_overlay.assert_called_once()
        mock_image_overlay.return_value.add_to.assert_called_once_with(m)'''
    ),
    (
        '''    @mock.patch("folium.raster_layers.VideoOverlay")
    @mock.patch("geemap.foliumap.video_overlay")
    def test_video_overlay(self, mock_vo, mock_video_overlay):
        m = foliumap.Map(ee_initialize=False)
        m.video_overlay("url", [[0, 0], [1, 1]])
        mock_vo.assert_called_once()''',
        '''    @mock.patch("folium.raster_layers.VideoOverlay")
    def test_video_overlay(self, mock_video_overlay):
        m = foliumap.Map(ee_initialize=False)
        m.video_overlay("url", [[0, 0], [1, 1]])
        mock_video_overlay.assert_called_once()
        mock_video_overlay.return_value.add_to.assert_called_once_with(m)'''
    ),
    (
        '''    @mock.patch("folium.LatLngPopup")
    @mock.patch("folium.plugins.Fullscreen")
    @mock.patch("folium.LayerControl")
    def test_set_control_visibility(self, mock_layer_control, mock_fullscreen, mock_latlng):
        m = foliumap.Map(ee_initialize=False)
        m.set_control_visibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
        mock_layer_control.return_value.add_to.assert_called_once_with(m)
        mock_fullscreen.return_value.add_to.assert_called_once_with(m)
        mock_latlng.return_value.add_to.assert_called_once_with(m)''',
        '''    @mock.patch("folium.LatLngPopup")
    @mock.patch("folium.plugins.Fullscreen")
    @mock.patch("folium.LayerControl")
    def test_set_control_visibility(self, mock_layer_control, mock_fullscreen, mock_latlng):
        m = foliumap.Map(ee_initialize=False, plugin_Fullscreen=False, plugin_LatLngPopup=False)
        m.set_control_visibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
        mock_layer_control.return_value.add_to.assert_called_once_with(m)
        mock_fullscreen.return_value.add_to.assert_called_once_with(m)
        mock_latlng.return_value.add_to.assert_called_once_with(m)'''
    )
]

for old, new in replacements:
    content = content.replace(old, new)

with open("tests/test_foliumap.py", "w") as f:
    f.write(content)
