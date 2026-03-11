import re

with open("tests/test_foliumap.py", "r") as f:
    content = f.read()

replacements = [
    (
        '''    @mock.patch.object(foliumap.Map, "fit_bounds")
    def test_set_center(self, mock_fit_bounds):
        m = foliumap.Map(ee_initialize=False)
        m.set_center(10, 20, 5)
        mock_fit_bounds.assert_called_once_with([[20, 10], [20, 10]], max_zoom=5)''',
        '''    def test_set_center(self):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "fit_bounds") as mock_fit_bounds:
            m.set_center(10, 20, 5)
            mock_fit_bounds.assert_called_once_with([[20, 10], [20, 10]], max_zoom=5)'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "fit_bounds")
    def test_zoom_to_bounds(self, mock_fit_bounds):
        m = foliumap.Map(ee_initialize=False)
        m.zoom_to_bounds([1, 2, 3, 4])
        mock_fit_bounds.assert_called_once_with([[2, 1], [4, 3]])''',
        '''    def test_zoom_to_bounds(self):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "fit_bounds") as mock_fit_bounds:
            m.zoom_to_bounds([1, 2, 3, 4])
            mock_fit_bounds.assert_called_once_with([[2, 1], [4, 3]])'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "zoom_to_bounds")
    def test_zoom_to_gdf(self, mock_zoom_to_bounds):
        m = foliumap.Map(ee_initialize=False)
        mock_gdf = mock.Mock()
        mock_gdf.total_bounds = [1, 2, 3, 4]
        m.zoom_to_gdf(mock_gdf)
        mock_zoom_to_bounds.assert_called_once_with([1, 2, 3, 4])''',
        '''    def test_zoom_to_gdf(self):
        m = foliumap.Map(ee_initialize=False)
        mock_gdf = mock.Mock()
        mock_gdf.total_bounds = [1, 2, 3, 4]
        with mock.patch.object(m, "zoom_to_bounds") as mock_zoom_to_bounds:
            m.zoom_to_gdf(mock_gdf)
            mock_zoom_to_bounds.assert_called_once_with([1, 2, 3, 4])'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "set_center")
    def test_center_object_zoom(self, mock_set_center):
        m = foliumap.Map(ee_initialize=False)
        mock_ee_object = mock.Mock()
        mock_geom = mock.Mock()
        mock_ee_object.geometry.return_value = mock_geom
        mock_geom.transform.return_value = mock_geom
        mock_geom.centroid.return_value.getInfo.return_value = {"coordinates": [10, 20]}
        m.center_object(mock_ee_object, zoom=5)
        mock_set_center.assert_called_once_with(10, 20, 5)''',
        '''    def test_center_object_zoom(self):
        m = foliumap.Map(ee_initialize=False)
        mock_ee_object = mock.Mock()
        mock_geom = mock.Mock()
        mock_ee_object.geometry.return_value = mock_geom
        mock_geom.transform.return_value = mock_geom
        mock_geom.centroid.return_value.getInfo.return_value = {"coordinates": [10, 20]}
        with mock.patch.object(m, "set_center") as mock_set_center:
            m.center_object(mock_ee_object, zoom=5)
            mock_set_center.assert_called_once_with(10, 20, 5)'''
    ),
    (
        '''    @mock.patch.object(foliumap.Map, "fit_bounds")
    def test_center_object_no_zoom(self, mock_fit_bounds):
        m = foliumap.Map(ee_initialize=False)
        mock_ee_object = mock.Mock()
        mock_geom = mock.Mock()
        mock_ee_object.geometry.return_value = mock_geom
        mock_geom.transform.return_value = mock_geom
        mock_geom.bounds.return_value.getInfo.return_value = {"coordinates": [[[10, 20], [10, 30], [20, 30], [20, 20]]]}
        m.center_object(mock_ee_object)
        mock_fit_bounds.assert_called_once_with([[20, 10], [30, 20]])''',
        '''    def test_center_object_no_zoom(self):
        m = foliumap.Map(ee_initialize=False)
        mock_ee_object = mock.Mock()
        mock_geom = mock.Mock()
        mock_ee_object.geometry.return_value = mock_geom
        mock_geom.transform.return_value = mock_geom
        mock_geom.bounds.return_value.getInfo.return_value = {"coordinates": [[[10, 20], [10, 30], [20, 30], [20, 20]]]}
        with mock.patch.object(m, "fit_bounds") as mock_fit_bounds:
            m.center_object(mock_ee_object)
            mock_fit_bounds.assert_called_once_with([[20, 10], [30, 20]])'''
    ),
    (
        '''    @mock.patch("geemap.foliumap.cog_bounds")
    @mock.patch("geemap.foliumap.cog_tile")
    def test_add_cog_layer(self, mock_cog_tile, mock_cog_bounds):
        m = foliumap.Map(ee_initialize=False)
        with mock.patch.object(m, "add_tile_layer") as mock_add_tile_layer:
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
    )
]

for old, new in replacements:
    content = content.replace(old, new)

with open("tests/test_foliumap.py", "w") as f:
    f.write(content)
