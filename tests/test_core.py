#!/usr/bin/env python
"""Tests for `map_widgets` module."""
import unittest
from unittest import mock

import ee
import ipyleaflet
import ipywidgets

from geemap import core
from geemap import map_widgets
from geemap import toolbar
from tests import fake_ee
from tests import fake_map


@mock.patch.object(ee, "FeatureCollection", fake_ee.FeatureCollection)
@mock.patch.object(ee, "Geometry", fake_ee.Geometry)
class TestMap(unittest.TestCase):
    """Tests for Map."""

    def _clear_default_widgets(self):
        widgets = [
            "search_control",
            "zoom_control",
            "fullscreen_control",
            "scale_control",
            "attribution_control",
            "toolbar",
            "inspector",
            "layer_manager",
            "draw_control",
        ]
        for widget in widgets:
            self.core_map.remove(widget)

    def setUp(self):
        super().setUp()
        self.core_map = core.Map(ee_initialize=False, width="100%")

    def test_defaults(self):
        """Tests that map defaults are set properly."""
        self.assertEqual(self.core_map.width, "100%")
        self.assertEqual(self.core_map.height, "600px")
        self.assertEqual(self.core_map.get_center(), [0, 0])
        self.assertEqual(self.core_map.get_zoom(), 2)

        controls = self.core_map.controls
        self.assertEqual(len(controls), 7)
        self.assertIsInstance(controls[0], ipyleaflet.WidgetControl)
        self.assertIsInstance(controls[0].widget.children[0], map_widgets.LayerManager)
        self.assertIsInstance(controls[0].widget.children[1], toolbar.Toolbar)
        self.assertIsInstance(controls[1].widget, map_widgets.SearchBar)
        self.assertIsInstance(controls[2], ipyleaflet.ZoomControl)
        self.assertIsInstance(controls[3], ipyleaflet.FullScreenControl)
        self.assertIsInstance(controls[4], core.MapDrawControl)
        self.assertIsInstance(controls[5], ipyleaflet.ScaleControl)
        self.assertIsInstance(controls[6], ipyleaflet.AttributionControl)

    def test_set_center(self):
        """Tests that `set_center` sets the center and zoom."""
        self.core_map.set_center(1, 2, 3)
        self.assertEqual(self.core_map.get_center(), [2, 1])
        self.assertEqual(self.core_map.get_zoom(), 3)
        self.core_map.set_center(5, 6)
        self.assertEqual(self.core_map.get_center(), [6, 5])
        self.assertEqual(self.core_map.get_zoom(), 3)

    def test_scale(self):
        """Tests that `scale` is calculated correctly."""
        self.core_map.set_center(0, 0, 2)
        self.assertAlmostEqual(self.core_map.get_scale(), 39135.76, places=2)
        self.core_map.set_center(-10, 4, 8)
        self.assertAlmostEqual(self.core_map.get_scale(), 610.01, places=2)

    def test_center_object(self):
        """Tests that `center_object` fits the object to the bounds."""
        fit_bounds_mock = mock.Mock()
        self.core_map.fit_bounds = fit_bounds_mock
        self.core_map.center_object(ee.Geometry.Point())
        fit_bounds_mock.assert_called_with([[-76, -178], [80, 179]])

        fit_bounds_mock = mock.Mock()
        self.core_map.fit_bounds = fit_bounds_mock
        self.core_map.center_object(ee.FeatureCollection([]))
        fit_bounds_mock.assert_called_with([[-76, -178], [80, 179]])

        set_center_mock = mock.Mock()
        self.core_map.set_center = set_center_mock
        self.core_map.center_object(ee.Geometry.Point(), 2)
        set_center_mock.assert_called_with(120, -70, 2)

        with self.assertRaisesRegex(Exception, "must be one of"):
            self.core_map.center_object("invalid object")

        with self.assertRaisesRegex(ValueError, "Zoom must be an integer"):
            self.core_map.center_object(ee.Geometry.Point(), "2")

    @mock.patch.object(core.Map, "bounds")
    def test_get_bounds(self, mock_bounds):
        """Tests that `get_bounds` returns the bounds of the map."""
        mock_bounds.__get__ = mock.Mock(return_value=[[1, 2], [3, 4]])
        self.assertEqual(self.core_map.get_bounds(), [2, 1, 4, 3])
        self.assertEqual(self.core_map.getBounds(), [2, 1, 4, 3])
        expected_geo_json = {
            "geodesic": False,
            "type": "Polygon",
            "coordinates": [[0, 1], [1, 2], [0, 1]],
        }
        self.assertEqual(self.core_map.get_bounds(as_geojson=True), expected_geo_json)

        mock_bounds.__get__ = mock.Mock(return_value=())
        with self.assertRaisesRegex(RuntimeError, "Map bounds are undefined"):
            self.core_map.get_bounds(as_geojson=True)

    def test_add_basic_widget_by_name(self):
        """Tests that `add` adds widgets by name."""
        self._clear_default_widgets()

        self.core_map.add("scale_control", position="topleft", metric=False)

        # Scale control and top right layout box.
        self.assertEqual(len(self.core_map.controls), 2)
        control = self.core_map.controls[1]
        self.assertIsInstance(control, ipyleaflet.ScaleControl)
        self.assertEqual(control.position, "topleft")
        self.assertEqual(control.metric, False)

    def test_add_basic_widget(self):
        """Tests that `add` adds widget instances to the map."""
        self._clear_default_widgets()

        self.core_map.add(ipyleaflet.ScaleControl(position="topleft", metric=False))

        # Scale control and top right layout box.
        self.assertEqual(len(self.core_map.controls), 2)
        control = self.core_map.controls[1]
        self.assertIsInstance(control, ipyleaflet.ScaleControl)
        self.assertEqual(control.position, "topleft")
        self.assertEqual(control.metric, False)

    def test_add_duplicate_basic_widget(self):
        """Tests adding a duplicate widget to the map."""
        self.assertEqual(len(self.core_map.controls), 7)
        self.assertIsInstance(self.core_map.controls[1], ipyleaflet.WidgetControl)
        self.assertEqual(self.core_map.controls[1].position, "topleft")

        self.core_map.add("zoom_control", position="bottomright")

        self.assertEqual(len(self.core_map.controls), 7)
        self.assertIsInstance(self.core_map.controls[1], ipyleaflet.WidgetControl)
        self.assertEqual(self.core_map.controls[1].position, "topleft")

    def test_add_toolbar(self):
        """Tests adding the toolbar widget."""
        self._clear_default_widgets()

        self.core_map.add("toolbar", position="bottomright")

        # Toolbar and top right layout box.
        self.assertEqual(len(self.core_map.controls), 2)
        toolbar_control = self.core_map.controls[1].widget

        self.assertEqual(len(toolbar_control.main_tools), 3)
        self.assertEqual(toolbar_control.main_tools[0].tooltip_text, "Basemap selector")
        self.assertEqual(toolbar_control.main_tools[1].tooltip_text, "Inspector")
        self.assertEqual(toolbar_control.main_tools[2].tooltip_text, "Get help")

    def test_add_draw_control(self):
        """Tests adding and getting the draw widget."""

        self._clear_default_widgets()
        self.core_map.add("draw_control", position="topleft")

        # Draw control and top right layout box.
        self.assertEqual(len(self.core_map.controls), 2)
        self.assertIsInstance(self.core_map.get_draw_control(), core.MapDrawControl)

    def test_add_basemap_selector(self):
        """Tests adding the basemap selector widget."""
        self._clear_default_widgets()

        self.core_map.add("basemap_selector")

        # Basemap selector and top right layout box.
        self.assertEqual(len(self.core_map.controls), 2)

    def test_width_height_setters(self):
        """Tests setting width and height of the map."""
        self.core_map.width = "50%"
        self.assertEqual(self.core_map.width, "50%")
        self.core_map.height = "500px"
        self.assertEqual(self.core_map.height, "500px")

    def test_map_properties(self):
        """Tests map properties for widgets."""
        self.assertIsNone(self.core_map._layer_editor)
        self.assertIsInstance(self.core_map._search_bar, map_widgets.SearchBar)
        self.assertIsInstance(self.core_map._layer_manager, map_widgets.LayerManager)
        self.assertIsNone(self.core_map._basemap_selector)
        # the inspector is not added by default
        self.assertIsNone(self.core_map._inspector)

    @mock.patch.object(map_widgets, "LayerEditor", create=True)
    def test_add_remove_widgets(self, MockLayerEditor):
        """Tests adding and removing widgets by name."""
        self._clear_default_widgets()

        # Add layer editor
        # Mocking the __new__ or return_value won't satisfy isinstance if LayerEditor is completely mocked out,
        # so we patch Map._layer_editor and skip the actual addition to ee layers, but we want to test the add method.
        # The add method uses map_widgets.LayerEditor.

        # Let's mock out the _find_widget_of_type specifically for LayerEditor so it doesn't crash on isinstance(mock)
        original_find = self.core_map._find_widget_of_type
        def side_effect(widget_type, return_control=False):
            if widget_type == MockLayerEditor:
                return None
            return original_find(widget_type, return_control)

        self.core_map._find_widget_of_type = side_effect

        MockLayerEditor.return_value = ipywidgets.DOMWidget()

        self.core_map.add("layer_editor")

        # We can't easily assert it's added due to the mocked type, but we can verify it doesn't error out.
        self.core_map.add("layer_editor")

        # Add search control
        self.core_map.add("search_control")
        self.assertIsNotNone(self.core_map._search_bar)
        self.core_map.add("search_control")

        # Add layer manager
        self.core_map.add("layer_manager")
        self.assertIsNotNone(self.core_map._layer_manager)
        self.core_map.add("layer_manager")

        # Add basemap selector
        self.core_map.add("basemap_selector")
        self.assertIsNotNone(self.core_map._basemap_selector)
        self.core_map.add("basemap_selector")

        # Add inspector
        self.core_map.add("inspector")
        self.assertIsNotNone(self.core_map._inspector)
        self.core_map.add("inspector")

        # Remove them
        self.core_map.remove("layer_editor")

        self.core_map.remove("search_control")
        self.assertIsNone(self.core_map._search_bar)

        self.core_map.remove("layer_manager")
        self.assertIsNone(self.core_map._layer_manager)

        self.core_map.remove("basemap_selector")
        self.assertIsNone(self.core_map._basemap_selector)

        self.core_map.remove("inspector")
        self.assertIsNone(self.core_map._inspector)

        self.core_map.remove("draw_control")
        self.assertIsNone(self.core_map.get_draw_control())

    def test_add_layer_ee_object(self):
        """Tests adding an ee.Image and ee.ImageCollection layer."""
        img = fake_ee.Image()

        class MockEELeafletTileLayer:
            EE_TYPES = (fake_ee.Image, fake_ee.ImageCollection, type(mock.MagicMock()))
            def __init__(self, *args, **kwargs):
                pass

        with mock.patch("geemap.core.ee_tile_layers.EELeafletTileLayer", MockEELeafletTileLayer):
            self.core_map.add_layer(img, name="test_image")
            self.assertIn("test_image", self.core_map.ee_layers)
            self.assertEqual(self.core_map.ee_layers["test_image"]["ee_object"], img)

            # fake image collection
            mock_col = fake_ee.ImageCollection([])
            mock_col.mosaic = mock.Mock(return_value=fake_ee.Image())
            self.core_map.add_layer(mock_col, name="test_collection")
            self.assertIn("test_collection", self.core_map.ee_layers)

        # test non EE object fallback
        with mock.patch("ipyleaflet.Map.add_layer") as mock_super_add:
            self.core_map.add_layer("not an ee object")
            mock_super_add.assert_called_with("not an ee object")

        # remove layer
        self.core_map.remove("test_image")
        self.assertNotIn("test_image", self.core_map.ee_layers)

    def test_add_legend(self):
        """Tests adding a legend."""
        class MockEELeafletTileLayer:
            EE_TYPES = (fake_ee.Image, fake_ee.ImageCollection, type(mock.MagicMock()))
            def __init__(self, *args, **kwargs):
                pass

        with mock.patch("geemap.core.ee_tile_layers.EELeafletTileLayer", MockEELeafletTileLayer):
            self.core_map.add_layer(fake_ee.Image(), name="test_layer")

        control = self.core_map._add_legend(title="test_legend", layer_name="test_layer")
        self.assertIn("legend", self.core_map.ee_layers["test_layer"])

        # Test replacement
        control2 = self.core_map._add_legend(title="test_legend2", layer_name="test_layer")
        self.assertEqual(self.core_map.ee_layers["test_layer"]["legend"], control2)

    def test_add_colorbar(self):
        """Tests adding a colorbar."""
        class MockEELeafletTileLayer:
            EE_TYPES = (fake_ee.Image, fake_ee.ImageCollection, type(mock.MagicMock()))
            def __init__(self, *args, **kwargs):
                pass

        with mock.patch("geemap.core.ee_tile_layers.EELeafletTileLayer", MockEELeafletTileLayer):
            self.core_map.add_layer(fake_ee.Image(), name="test_layer")

        control = self.core_map._add_colorbar(vis_params={"min": 0, "max": 1, "palette": ["red", "blue"]}, layer_name="test_layer")
        self.assertIn("colorbar", self.core_map.ee_layers["test_layer"])

        # Test replacement
        control2 = self.core_map._add_colorbar(vis_params={"min": 0, "max": 1, "palette": ["red", "blue"]}, layer_name="test_layer")
        self.assertEqual(self.core_map.ee_layers["test_layer"]["colorbar"], control2)

        # Remove it
        self.core_map.remove("test_layer")
        self.assertNotIn("test_layer", self.core_map.ee_layers)

    def test_replace_basemap(self):
        """Tests replacing basemap."""
        # Try invalid
        self.core_map._replace_basemap("INVALID_BASEMAP")

        # Try valid
        valid_basemap = next(iter(self.core_map._available_basemaps.keys()))
        self.core_map._replace_basemap(valid_basemap)


@mock.patch.object(ee, "FeatureCollection", fake_ee.FeatureCollection)
@mock.patch.object(ee, "Feature", fake_ee.Feature)
@mock.patch.object(ee, "Geometry", fake_ee.Geometry)
@mock.patch.object(ee, "Image", fake_ee.Image)
class TestAbstractDrawControl(unittest.TestCase):
    """Tests for the draw control interface in the `draw_control` module."""

    geo_json = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [0, 1],
                    [0, -1],
                    [1, -1],
                    [1, 1],
                    [0, 1],
                ]
            ],
        },
        "properties": {"name": "Null Island"},
    }
    geo_json2 = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [0, 2],
                    [0, -2],
                    [2, -2],
                    [2, 2],
                    [0, 2],
                ]
            ],
        },
        "properties": {"name": "Null Island 2x"},
    }

    def setUp(self):
        super().setUp()
        self.map = fake_map.FakeMap()
        self._draw_control = TestAbstractDrawControl.TestDrawControl(self.map)

    def test_initialization(self):
        # Initialized is set by the `_bind_draw_controls` method.
        self.assertTrue(self._draw_control.initialized)
        self.assertIsNone(self._draw_control.layer)
        self.assertEqual(self._draw_control.geometries, [])
        self.assertEqual(self._draw_control.properties, [])
        self.assertIsNone(self._draw_control.last_geometry)
        self.assertIsNone(self._draw_control.last_draw_action)
        self.assertEqual(self._draw_control.features, [])
        self.assertEqual(self._draw_control.collection, fake_ee.FeatureCollection([]))
        self.assertIsNone(self._draw_control.last_feature)
        self.assertEqual(self._draw_control.count, 0)
        self.assertFalse("Drawn Features" in self.map.ee_layers)

    def test_handles_creation(self):
        self._draw_control.create(self.geo_json)
        self.assertEqual(
            self._draw_control.geometries,
            [fake_ee.Geometry(self.geo_json["geometry"])],
        )
        self.assertTrue("Drawn Features" in self.map.ee_layers)

    def test_handles_deletion(self):
        self._draw_control.create(self.geo_json)
        self.assertTrue("Drawn Features" in self.map.ee_layers)
        self.assertEqual(len(self._draw_control.geometries), 1)
        self._draw_control.delete(0)
        self.assertEqual(len(self._draw_control.geometries), 0)
        self.assertFalse("Drawn Features" in self.map.ee_layers)

    def test_handles_edit(self):
        self._draw_control.create(self.geo_json)
        self.assertEqual(len(self._draw_control.geometries), 1)

        self._draw_control.edit(0, self.geo_json2)
        self.assertEqual(len(self._draw_control.geometries), 1)
        self.assertEqual(
            self._draw_control.geometries[0],
            fake_ee.Geometry(self.geo_json2["geometry"]),
        )

    def test_property_accessors(self):
        self._draw_control.create(self.geo_json)

        # Test layer accessor.
        self.assertIsNotNone(self._draw_control.layer)
        # Test geometries accessor.
        geometry = fake_ee.Geometry(self.geo_json["geometry"])
        self.assertEqual(len(self._draw_control.geometries), 1)
        self.assertEqual(self._draw_control.geometries, [geometry])
        # Test properties accessor.
        self.assertEqual(self._draw_control.properties, [None])
        # Test last_geometry accessor.
        self.assertEqual(self._draw_control.last_geometry, geometry)
        # Test last_draw_action accessor.
        self.assertEqual(self._draw_control.last_draw_action, core.DrawActions.CREATED)
        # Test features accessor.
        feature = fake_ee.Feature(geometry, None)
        self.assertEqual(self._draw_control.features, [feature])
        # Test collection accessor.
        self.assertEqual(
            self._draw_control.collection, fake_ee.FeatureCollection([feature])
        )
        # Test last_feature accessor.
        self.assertEqual(self._draw_control.last_feature, feature)
        # Test count accessor.
        self.assertEqual(self._draw_control.count, 1)

    def test_feature_property_access(self):
        self._draw_control.create(self.geo_json)
        geometry = self._draw_control.geometries[0]
        self.assertIsNone(self._draw_control.get_geometry_properties(geometry))
        self.assertEqual(self._draw_control.features, [fake_ee.Feature(geometry, None)])
        self._draw_control.set_geometry_properties(geometry, {"test": 1})
        self.assertEqual(
            self._draw_control.features, [fake_ee.Feature(geometry, {"test": 1})]
        )

    def test_reset(self):
        self._draw_control.create(self.geo_json)
        self.assertEqual(len(self._draw_control.geometries), 1)

        # When clear_draw_control is True, deletes the underlying geometries.
        self._draw_control.reset(clear_draw_control=True)
        self.assertEqual(len(self._draw_control.geometries), 0)
        self.assertEqual(len(self._draw_control.geo_jsons), 0)
        self.assertFalse("Drawn Features" in self.map.ee_layers)

        self._draw_control.create(self.geo_json)
        self.assertEqual(len(self._draw_control.geometries), 1)
        # When clear_draw_control is False, does not delete the underlying geometries.
        self._draw_control.reset(clear_draw_control=False)
        self.assertEqual(len(self._draw_control.geometries), 0)
        self.assertEqual(len(self._draw_control.geo_jsons), 1)
        self.assertFalse("Drawn Features" in self.map.ee_layers)

    def test_features_no_count(self):
        self.assertEqual(self._draw_control.features, [])

    def test_remove_geometry_none_or_not_found(self):
        self._draw_control.create(self.geo_json)
        self.assertEqual(len(self._draw_control.geometries), 1)
        self._draw_control.remove_geometry(None)
        self.assertEqual(len(self._draw_control.geometries), 1)

        # Geometry not found
        geometry2 = fake_ee.Geometry(self.geo_json2["geometry"])
        self._draw_control.remove_geometry(geometry2)
        self.assertEqual(len(self._draw_control.geometries), 1)

    def test_get_geometry_properties_none_or_not_found(self):
        self._draw_control.create(self.geo_json)
        self.assertIsNone(self._draw_control.get_geometry_properties(None))

        # Geometry not found
        geometry2 = fake_ee.Geometry(self.geo_json2["geometry"])
        self.assertIsNone(self._draw_control.get_geometry_properties(geometry2))

    def test_set_geometry_properties_none_or_not_found(self):
        self._draw_control.create(self.geo_json)
        self.assertEqual(self._draw_control.properties, [None])

        self._draw_control.set_geometry_properties(None, {"test": 1})
        self.assertEqual(self._draw_control.properties, [None])

        # Geometry not found
        geometry2 = fake_ee.Geometry(self.geo_json2["geometry"])
        self._draw_control.set_geometry_properties(geometry2, {"test": 1})
        self.assertEqual(self._draw_control.properties, [None])

    def test_callbacks(self):
        mock_callback = mock.Mock()

        self._draw_control.on_geometry_create(mock_callback)
        self._draw_control._geometry_create_dispatcher(self._draw_control, geometry=None)
        mock_callback.assert_called_once()

        mock_callback.reset_mock()
        self._draw_control.on_geometry_edit(mock_callback)
        self._draw_control._geometry_edit_dispatcher(self._draw_control, geometry=None)
        mock_callback.assert_called_once()

        mock_callback.reset_mock()
        self._draw_control.on_geometry_delete(mock_callback)
        self._draw_control._geometry_delete_dispatcher(self._draw_control, geometry=None)
        mock_callback.assert_called_once()

    def test_abstract_methods(self):
        with self.assertRaises(NotImplementedError):
            core.AbstractDrawControl(self.map)

        # Bypass init to test other abstract methods
        abstract_draw_control = core.AbstractDrawControl.__new__(core.AbstractDrawControl)
        with self.assertRaises(NotImplementedError):
            abstract_draw_control._bind_to_draw_control()
        with self.assertRaises(NotImplementedError):
            abstract_draw_control._remove_geometry_at_index_on_draw_control(0)
        with self.assertRaises(NotImplementedError):
            abstract_draw_control._clear_draw_control()
        with self.assertRaises(NotImplementedError):
            abstract_draw_control._get_synced_geojson_from_draw_control()

    def test_remove_geometry(self):
        self._draw_control.create(self.geo_json)
        self._draw_control.create(self.geo_json2)
        geometry1 = self._draw_control.geometries[0]
        geometry2 = self._draw_control.geometries[1]
        self.assertEqual(len(self._draw_control.geometries), 2)
        self.assertEqual(len(self._draw_control.properties), 2)
        self.assertEqual(self._draw_control.last_draw_action, core.DrawActions.CREATED)
        self.assertEqual(self._draw_control.last_geometry, geometry2)

        # When there are two geometries and the removed geometry is the last one, then
        # we treat it like an undo.
        self._draw_control.remove_geometry(geometry2)
        self.assertEqual(len(self._draw_control.geometries), 1)
        self.assertEqual(len(self._draw_control.properties), 1)
        self.assertEqual(
            self._draw_control.last_draw_action, core.DrawActions.REMOVED_LAST
        )
        self.assertEqual(self._draw_control.last_geometry, geometry1)

        # When there's only one geometry, last_geometry is the removed geometry.
        self._draw_control.remove_geometry(geometry1)
        self.assertEqual(len(self._draw_control.geometries), 0)
        self.assertEqual(len(self._draw_control.properties), 0)
        self.assertEqual(
            self._draw_control.last_draw_action, core.DrawActions.REMOVED_LAST
        )
        self.assertEqual(self._draw_control.last_geometry, geometry1)

        # When there are two geometries and the removed geometry is the first
        # one, then treat it like a normal delete.
        self._draw_control.create(self.geo_json)
        self._draw_control.create(self.geo_json2)
        geometry1 = self._draw_control.geometries[0]
        geometry2 = self._draw_control.geometries[1]
        self._draw_control.remove_geometry(geometry1)
        self.assertEqual(len(self._draw_control.geometries), 1)
        self.assertEqual(len(self._draw_control.properties), 1)
        self.assertEqual(self._draw_control.last_draw_action, core.DrawActions.DELETED)
        self.assertEqual(self._draw_control.last_geometry, geometry1)

    class TestDrawControl(core.AbstractDrawControl):
        """Implements an AbstractDrawControl for tests."""

        geo_jsons = []
        initialized = False

        def __init__(self, host_map, **kwargs):
            """Initialize the test draw control.

            Args:
                host_map (geemap.Map): The geemap.Map object
            """
            super().__init__(host_map=host_map, **kwargs)
            self.geo_jsons = []

        def _get_synced_geojson_from_draw_control(self):
            return [data.copy() for data in self.geo_jsons]

        def _bind_to_draw_control(self):
            # In a non-test environment, `_on_draw` would be used here.
            self.initialized = True

        def _remove_geometry_at_index_on_draw_control(self, index):
            geo_json = self.geo_jsons[index]
            del self.geo_jsons[index]
            self._on_draw("deleted", geo_json)

        def _clear_draw_control(self):
            self.geo_jsons = []

        def _on_draw(self, action, geo_json):
            """Mimics the ipyleaflet DrawControl handler."""
            if action == "created":
                self._handle_geometry_created(geo_json)
            elif action == "edited":
                self._handle_geometry_edited(geo_json)
            elif action == "deleted":
                self._handle_geometry_deleted(geo_json)

        def create(self, geo_json):
            self.geo_jsons.append(geo_json)
            self._on_draw("created", geo_json)

        def edit(self, i, geo_json):
            self.geo_jsons[i] = geo_json
            self._on_draw("edited", geo_json)

        def delete(self, i):
            geo_json = self.geo_jsons[i]
            del self.geo_jsons[i]
            self._on_draw("deleted", geo_json)


@mock.patch.object(ee, "FeatureCollection", fake_ee.FeatureCollection)
@mock.patch.object(ee, "Feature", fake_ee.Feature)
@mock.patch.object(ee, "Geometry", fake_ee.Geometry)
@mock.patch.object(ee, "Image", fake_ee.Image)
class TestMapDrawControl(unittest.TestCase):
    """Tests for the `MapDrawControl`."""

    geo_json = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [0, 1],
                    [0, -1],
                    [1, -1],
                    [1, 1],
                    [0, 1],
                ]
            ],
        },
        "properties": {"name": "Null Island"},
    }

    def setUp(self):
        super().setUp()
        self.map = fake_map.FakeMap()
        self._draw_control = core.MapDrawControl(self.map)

    def test_get_synced_geojson_from_draw_control(self):
        self._draw_control.data = [self.geo_json]
        synced_data = self._draw_control._get_synced_geojson_from_draw_control()
        self.assertEqual(synced_data, [self.geo_json])
        # Ensure it's a copy
        self.assertIsNot(synced_data[0], self.geo_json)

    def test_handle_draw_exception(self):
        self._draw_control.data = [self.geo_json]

        # Test exception catching in handle_draw
        with mock.patch.object(self._draw_control, "_handle_geometry_created", side_effect=Exception("Test Exception")):
            with self.assertRaisesRegex(Exception, "Test Exception"):
                # Call handle_draw which is bound to on_draw
                # We need to trigger the draw callback
                for callback in self._draw_control._draw_callbacks.callbacks:
                    callback(self._draw_control, "created", self.geo_json)

    def test_handle_data_update(self):
        # We need to test the observe callback for 'data'

        # Mock _sync_geometries and _redraw_layer
        self._draw_control._sync_geometries = mock.Mock()
        self._draw_control._redraw_layer = mock.Mock()

        # Call the update handler directly via traitlets notify
        # _trait_notifiers is a dict mapping names to a list of EventHandler objects or similar in traitlets
        # The easiest way is to trigger it by changing the data trait directly.

        # Test when last_draw_action is not EDITED
        self._draw_control.last_draw_action = core.DrawActions.CREATED
        self._draw_control.data = [self.geo_json]

        self._draw_control._sync_geometries.assert_called_once()
        self._draw_control._redraw_layer.assert_not_called()

        self._draw_control._sync_geometries.reset_mock()

        # Test when last_draw_action is EDITED
        self._draw_control.last_draw_action = core.DrawActions.EDITED
        self._draw_control.data = [self.geo_json, self.geo_json]

        self._draw_control._sync_geometries.assert_called_once()
        self._draw_control._redraw_layer.assert_called_once()

    def test_remove_geometry_at_index_on_draw_control(self):
        self._draw_control.data = [self.geo_json]
        self._draw_control.send_state = mock.Mock()
        self._draw_control._remove_geometry_at_index_on_draw_control(0)
        self.assertEqual(self._draw_control.data, [])
        self._draw_control.send_state.assert_called_once_with(key="data")

    def test_clear_draw_control(self):
        self._draw_control.data = [self.geo_json]
        self._draw_control.clear = mock.Mock()
        self._draw_control._clear_draw_control()
        self.assertEqual(self._draw_control.data, [])
        self._draw_control.clear.assert_called_once()

class TestMapInterface(unittest.TestCase):
    """Tests for the MapInterface."""

    def test_abstract_methods(self):
        map_interface = core.MapInterface()

        with self.assertRaises(NotImplementedError):
            map_interface.get_zoom()

        with self.assertRaises(NotImplementedError):
            map_interface.set_zoom(5)

        with self.assertRaises(NotImplementedError):
            map_interface.get_center()

        with self.assertRaises(NotImplementedError):
            map_interface.set_center(0, 0)

        with self.assertRaises(NotImplementedError):
            map_interface.center_object(None)

        with self.assertRaises(NotImplementedError):
            map_interface.get_scale()

        with self.assertRaises(NotImplementedError):
            map_interface.get_bounds()

        with self.assertRaises(NotImplementedError):
            _ = map_interface.width

        with self.assertRaises(NotImplementedError):
            map_interface.width = "100px"

        with self.assertRaises(NotImplementedError):
            _ = map_interface.height

        with self.assertRaises(NotImplementedError):
            map_interface.height = "100px"

        with self.assertRaises(NotImplementedError):
            map_interface.add("widget", "topleft")

        with self.assertRaises(NotImplementedError):
            map_interface.remove("widget")

        with self.assertRaises(NotImplementedError):
            map_interface.add_layer(None)

        with self.assertRaises(NotImplementedError):
            map_interface.remove_layer("layer")

if __name__ == "__main__":
    unittest.main()
