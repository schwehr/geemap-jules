#!/usr/bin/env python
"""Tests for `map_widgets` module."""
import unittest
from unittest import mock

import ee
import ipywidgets
from matplotlib import colorbar
from matplotlib import colors
from matplotlib import pyplot

from geemap import coreutils
from geemap import legends
from geemap import map_widgets
from tests import fake_ee
import json
from tests import fake_map
import ipyleaflet


def _get_colormaps() -> list[str]:
    """Gets the list of available colormaps."""
    colormap_options = pyplot.colormaps()
    colormap_options.sort()
    return ["Custom"] + colormap_options


class TestColorbar(unittest.TestCase):
    """Tests for the Colorbar class in the `map_widgets` module."""

    TEST_COLORS = ["blue", "red", "green"]
    TEST_COLORS_HEX = ["#0000ff", "#ff0000", "#008000"]

    def setUp(self):
        super().setUp()
        self.fig_mock = mock.MagicMock()
        self.ax_mock = mock.MagicMock()
        self.subplots_mock = mock.patch.object(pyplot, "subplots").start()
        self.subplots_mock.return_value = (self.fig_mock, self.ax_mock)

        self.colorbar_base_mock = mock.MagicMock()
        self.colorbar_base_class_mock = mock.patch.object(
            colorbar, "ColorbarBase"
        ).start()
        self.colorbar_base_class_mock.return_value = self.colorbar_base_mock

        self.normalize_mock = mock.MagicMock()
        self.normalize_class_mock = mock.patch.object(colors, "Normalize").start()
        self.normalize_class_mock.return_value = self.normalize_mock

        self.boundary_norm_mock = mock.MagicMock()
        self.boundary_norm_class_mock = mock.patch.object(
            colors, "BoundaryNorm"
        ).start()
        self.boundary_norm_class_mock.return_value = self.boundary_norm_mock

        self.listed_colormap = mock.MagicMock()
        self.listed_colormap_class_mock = mock.patch.object(
            colors, "ListedColormap"
        ).start()
        self.listed_colormap_class_mock.return_value = self.listed_colormap

        self.linear_segmented_colormap_mock = mock.MagicMock()
        self.colormap_from_list_mock = mock.patch.object(
            colors.LinearSegmentedColormap, "from_list"
        ).start()
        self.colormap_from_list_mock.return_value = self.linear_segmented_colormap_mock

        check_cmap_mock = mock.patch.object(coreutils, "check_cmap").start()
        check_cmap_mock.side_effect = lambda x: x

        self.cmap_mock = mock.MagicMock()
        self.get_cmap_mock = mock.patch.object(pyplot, "get_cmap").start()
        self.get_cmap_mock.return_value = self.cmap_mock

    def tearDown(self):
        mock.patch.stopall()
        super().tearDown()

    def test_colorbar_no_args(self):
        map_widgets.Colorbar()
        self.normalize_class_mock.assert_called_with(vmin=0, vmax=1)
        self.get_cmap_mock.assert_called_with("gray")
        self.subplots_mock.assert_called_with(figsize=(3.0, 0.3))
        self.ax_mock.set_axis_off.assert_not_called()
        self.ax_mock.tick_params.assert_called_with(labelsize=9)
        self.fig_mock.patch.set_alpha.assert_not_called()
        self.colorbar_base_mock.set_label.assert_not_called()
        self.colorbar_base_class_mock.assert_called_with(
            self.ax_mock,
            norm=self.normalize_mock,
            alpha=1,
            cmap=self.cmap_mock,
            orientation="horizontal",
        )

    def test_colorbar_orientation_horizontal(self):
        map_widgets.Colorbar(orientation="horizontal")
        self.subplots_mock.assert_called_with(figsize=(3.0, 0.3))

    def test_colorbar_orientation_vertical(self):
        map_widgets.Colorbar(orientation="vertical")
        self.subplots_mock.assert_called_with(figsize=(0.3, 3.0))

    def test_colorbar_orientation_override(self):
        map_widgets.Colorbar(orientation="horizontal", width=2.0)
        self.subplots_mock.assert_called_with(figsize=(2.0, 0.3))

    def test_colorbar_invalid_orientation(self):
        with self.assertRaisesRegex(ValueError, "orientation must be one of"):
            map_widgets.Colorbar(orientation="not an orientation")

    def test_colorbar_label(self):
        map_widgets.Colorbar(label="Colorbar lbl", font_size=42)
        self.colorbar_base_mock.set_label.assert_called_with(
            "Colorbar lbl", fontsize=42
        )

    def test_colorbar_label_as_bands(self):
        map_widgets.Colorbar(vis_params={"bands": "b1"})
        self.colorbar_base_mock.set_label.assert_called_with("b1", fontsize=9)

    def test_colorbar_label_with_caption(self):
        map_widgets.Colorbar(caption="Colorbar caption")
        self.colorbar_base_mock.set_label.assert_called_with(
            "Colorbar caption", fontsize=9
        )

    def test_colorbar_label_precedence(self):
        map_widgets.Colorbar(
            label="Colorbar lbl",
            vis_params={"bands": "b1"},
            caption="Colorbar caption",
            font_size=21,
        )
        self.colorbar_base_mock.set_label.assert_called_with(
            "Colorbar lbl", fontsize=21
        )

    def test_colorbar_axis(self):
        map_widgets.Colorbar(axis_off=True, font_size=24)
        self.ax_mock.set_axis_off.assert_called()
        self.ax_mock.tick_params.assert_called_with(labelsize=24)

    def test_colorbar_transparent_bg(self):
        map_widgets.Colorbar(transparent_bg=True)
        self.fig_mock.patch.set_alpha.assert_called_with(0.0)

    def test_colorbar_vis_params_palette(self):
        map_widgets.Colorbar(
            vis_params={
                "palette": self.TEST_COLORS,
                "min": 11,
                "max": 21,
                "opacity": 0.2,
            }
        )
        self.normalize_class_mock.assert_called_with(vmin=11, vmax=21)
        self.colormap_from_list_mock.assert_called_with(
            "custom", self.TEST_COLORS_HEX, N=256
        )
        self.colorbar_base_class_mock.assert_called_with(
            self.ax_mock,
            norm=self.normalize_mock,
            alpha=0.2,
            cmap=self.linear_segmented_colormap_mock,
            orientation="horizontal",
        )

    def test_colorbar_vis_params_discrete_palette(self):
        map_widgets.Colorbar(
            vis_params={"palette": self.TEST_COLORS, "min": -1}, discrete=True
        )
        self.boundary_norm_class_mock.assert_called_with([-1], mock.ANY)
        self.listed_colormap_class_mock.assert_called_with(self.TEST_COLORS_HEX)
        self.colorbar_base_class_mock.assert_called_with(
            self.ax_mock,
            norm=self.boundary_norm_mock,
            alpha=1,
            cmap=self.listed_colormap,
            orientation="horizontal",
        )

    def test_colorbar_vis_params_palette_as_list(self):
        map_widgets.Colorbar(vis_params=self.TEST_COLORS, discrete=True)
        self.boundary_norm_class_mock.assert_called_with([0], mock.ANY)
        self.listed_colormap_class_mock.assert_called_with(self.TEST_COLORS_HEX)
        self.colorbar_base_class_mock.assert_called_with(
            self.ax_mock,
            norm=self.boundary_norm_mock,
            alpha=1,
            cmap=self.listed_colormap,
            orientation="horizontal",
        )

    def test_colorbar_kwargs_colors(self):
        map_widgets.Colorbar(colors=self.TEST_COLORS, discrete=True)
        self.boundary_norm_class_mock.assert_called_with([0], mock.ANY)
        self.listed_colormap_class_mock.assert_called_with(self.TEST_COLORS_HEX)
        self.colorbar_base_class_mock.assert_called_with(
            self.ax_mock,
            norm=self.boundary_norm_mock,
            alpha=1,
            cmap=self.listed_colormap,
            orientation="horizontal",
            colors=self.TEST_COLORS,
        )

    def test_colorbar_min_max(self):
        map_widgets.Colorbar(
            vis_params={"palette": self.TEST_COLORS, "min": -1.5}, vmin=-1, vmax=2
        )
        self.normalize_class_mock.assert_called_with(vmin=-1.5, vmax=2)

    def test_colorbar_invalid_min(self):
        with self.assertRaisesRegex(ValueError, "min value must be scalar type"):
            map_widgets.Colorbar(vis_params={"min": "invalid_min"})

    def test_colorbar_invalid_max(self):
        with self.assertRaisesRegex(ValueError, "max value must be scalar type"):
            map_widgets.Colorbar(vis_params={"max": "invalid_max"})

    def test_colorbar_opacity(self):
        map_widgets.Colorbar(vis_params={"opacity": 0.5}, colors=self.TEST_COLORS)
        self.colorbar_base_class_mock.assert_called_with(
            mock.ANY,
            norm=mock.ANY,
            alpha=0.5,
            cmap=mock.ANY,
            orientation=mock.ANY,
            colors=mock.ANY,
        )

    def test_colorbar_alpha(self):
        map_widgets.Colorbar(alpha=0.5, colors=self.TEST_COLORS)
        self.colorbar_base_class_mock.assert_called_with(
            mock.ANY,
            norm=mock.ANY,
            alpha=0.5,
            cmap=mock.ANY,
            orientation=mock.ANY,
            colors=mock.ANY,
        )

    def test_colorbar_invalid_alpha(self):
        with self.assertRaisesRegex(
            ValueError, "opacity or alpha value must be scalar type"
        ):
            map_widgets.Colorbar(alpha="invalid_alpha", colors=self.TEST_COLORS)

    def test_colorbar_vis_params_throws_for_not_dict(self):
        with self.assertRaisesRegex(TypeError, "vis_params must be a dictionary"):
            map_widgets.Colorbar(vis_params="NOT a dict")


class TestLegend(unittest.TestCase):
    """Tests for the Legend class in the `map_widgets` module."""

    TEST_KEYS = ["developed", "forest", "open water"]
    TEST_COLORS_HEX = ["#ff0000", "#00ff00", "#0000ff"]
    TEST_COLORS_RGB = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    def test_legend_initializes(self):
        legend = map_widgets.Legend(
            title="My Legend",
            keys=self.TEST_KEYS,
            colors=self.TEST_COLORS_HEX,
            position="bottomleft",
            add_header=True,
            widget_args={"show_close_button": True},
        )
        self.assertEqual(legend.title, "My Legend")
        self.assertEqual(legend.position, "bottomleft")
        self.assertTrue(legend.add_header)
        self.assertTrue(legend.show_close_button)

    def test_legend_with_keys_and_colors(self):
        # Normal hex colors.
        legend = map_widgets.Legend(keys=self.TEST_KEYS, colors=self.TEST_COLORS_HEX)
        self.assertListEqual(legend.legend_keys, self.TEST_KEYS)
        self.assertListEqual(legend.legend_colors, self.TEST_COLORS_HEX)

        # Adds # when there are none.
        legend = map_widgets.Legend(
            keys=self.TEST_KEYS, colors=["ff0000", "00ff00", "0000ff"]
        )
        self.assertListEqual(legend.legend_colors, self.TEST_COLORS_HEX)

        # Three characters.
        legend = map_widgets.Legend(keys=self.TEST_KEYS, colors=["f00", "0f0", "00f"])
        self.assertListEqual(legend.legend_colors, ["#f00", "#0f0", "#00f"])

        # With alpha.
        legend = map_widgets.Legend(
            keys=self.TEST_KEYS, colors=["#ff0000ff", "#00ff00ff", "#0000ffff"]
        )
        self.assertListEqual(
            legend.legend_colors, ["#ff0000ff", "#00ff00ff", "#0000ffff"]
        )

        # CSS colors.
        legend = map_widgets.Legend(
            keys=self.TEST_KEYS, colors=["red", "green", "blue"]
        )
        self.assertListEqual(legend.legend_colors, ["red", "green", "blue"])

        # RGB tuples.
        legend = map_widgets.Legend(keys=self.TEST_KEYS, colors=self.TEST_COLORS_RGB)
        self.assertListEqual(legend.legend_colors, self.TEST_COLORS_HEX)

        # Mix of hex and tuples.
        legend = map_widgets.Legend(
            keys=self.TEST_KEYS * 2, colors=self.TEST_COLORS_HEX + self.TEST_COLORS_RGB
        )
        self.assertListEqual(legend.legend_keys, self.TEST_KEYS * 2)
        self.assertListEqual(legend.legend_colors, self.TEST_COLORS_HEX * 2)

    def test_legend_with_dictionary(self):
        legend = map_widgets.Legend(
            legend_dict=dict(zip(self.TEST_KEYS, self.TEST_COLORS_HEX))
        )
        self.assertListEqual(legend.legend_keys, self.TEST_KEYS)
        self.assertListEqual(legend.legend_colors, self.TEST_COLORS_HEX)

        legend = map_widgets.Legend(
            legend_dict=dict(zip(self.TEST_KEYS, self.TEST_COLORS_RGB))
        )
        self.assertListEqual(legend.legend_keys, self.TEST_KEYS)
        self.assertListEqual(legend.legend_colors, self.TEST_COLORS_HEX)

    def test_legend_with_builtin_legends(self):
        legend = map_widgets.Legend(builtin_legend="NLCD")
        self.assertListEqual(
            legend.legend_keys, list(legends.builtin_legends["NLCD"].keys())
        )
        self.assertListEqual(
            legend.legend_colors,
            [f"#{color}" for color in legends.builtin_legends["NLCD"].values()],
        )

    def test_legend_unable_to_convert_rgb_to_hex(self):
        with self.assertRaisesRegex(ValueError, "Unable to convert rgb value to hex."):
            test_keys = ["Key 1"]
            test_colors = [("invalid", "invalid")]
            map_widgets.Legend(keys=test_keys, colors=test_colors)

    def test_legend_keys_and_colors_not_same_length(self):
        with self.assertRaisesRegex(
            ValueError, ("The legend keys and colors must be the " + "same length.")
        ):
            test_keys = ["one", "two", "three", "four"]
            map_widgets.Legend(keys=test_keys, colors=TestLegend.TEST_COLORS_HEX)

    def test_legend_builtin_legend_not_allowed(self):
        expected_regex = "The builtin legend must be one of the following: {}".format(
            ", ".join(legends.builtin_legends)
        )
        with self.assertRaisesRegex(ValueError, expected_regex):
            map_widgets.Legend(builtin_legend="invalid_builtin_legend")

    def test_legend_position_not_allowed(self):
        expected_regex = (
            "The position must be one of the following: "
            + "topleft, topright, bottomleft, bottomright"
        )
        with self.assertRaisesRegex(ValueError, expected_regex):
            map_widgets.Legend(position="invalid_position")

    def test_legend_keys_not_a_dict(self):
        with self.assertRaisesRegex(TypeError, "The legend keys must be a list."):
            map_widgets.Legend(keys="invalid_keys")

    def test_legend_colors_not_a_list(self):
        with self.assertRaisesRegex(TypeError, "The legend colors must be a list."):
            map_widgets.Legend(keys=["test_key"], colors="invalid_colors")


@mock.patch.object(ee, "Algorithms", fake_ee.Algorithms)
@mock.patch.object(ee, "FeatureCollection", fake_ee.FeatureCollection)
@mock.patch.object(ee, "Feature", fake_ee.Feature)
@mock.patch.object(ee, "Geometry", fake_ee.Geometry)
@mock.patch.object(ee, "Image", fake_ee.Image)
@mock.patch.object(ee, "String", fake_ee.String)
class TestInspector(unittest.TestCase):
    """Tests for the Inspector class in the `map_widgets` module."""

    def setUp(self):
        super().setUp()
        # ee.Reducer is dynamically initialized (can't use @patch.object).
        ee.Reducer = fake_ee.Reducer

        self.map_fake = fake_map.FakeMap()
        self.inspector = map_widgets.Inspector(self.map_fake)

    def test_inspector_no_map(self):
        """Tests that a valid map must be passed in."""
        with self.assertRaisesRegex(ValueError, "valid map"):
            map_widgets.Inspector(None)

    def test_inspector(self):
        """Tests that the inspector's initial UI is set up properly."""
        self.assertEqual(self.map_fake.cursor_style, "crosshair")
        self.assertFalse(self.inspector.hide_close_button)

        self.assertFalse(self.inspector.expand_points)
        self.assertTrue(self.inspector.expand_pixels)
        self.assertFalse(self.inspector.expand_objects)

        self.assertEqual(self.inspector.point_info, {})
        self.assertEqual(self.inspector.pixel_info, {})
        self.assertEqual(self.inspector.object_info, {})

    def test_map_empty_click(self):
        """Tests that clicking the map triggers inspection."""
        self.map_fake.click((1, 2), "click")

        self.assertEqual(self.map_fake.cursor_style, "crosshair")

        expected_point_info = coreutils.new_tree_node(
            "Point (2.00, 1.00) at 1024m/px",
            [
                coreutils.new_tree_node("Longitude: 2"),
                coreutils.new_tree_node("Latitude: 1"),
                coreutils.new_tree_node("Zoom Level: 7"),
                coreutils.new_tree_node("Scale (approx. m/px): 1024"),
            ],
            top_level=True,
        )
        self.assertEqual(self.inspector.point_info, expected_point_info)

        expected_pixel_info = coreutils.new_tree_node(
            "Pixels", top_level=True, expanded=True
        )
        self.assertEqual(self.inspector.pixel_info, expected_pixel_info)

        expected_object_info = coreutils.new_tree_node(
            "Objects", top_level=True, expanded=True
        )
        self.assertEqual(self.inspector.object_info, expected_object_info)

    def test_map_click(self):
        """Tests that clicking the map triggers inspection."""
        self.map_fake.ee_layers = {
            "test-map-1": {
                "ee_object": ee.Image(1),
                "ee_layer": fake_map.FakeEeTileLayer(visible=True),
                "vis_params": None,
            },
            "test-map-2": {
                "ee_object": ee.Image(2),
                "ee_layer": fake_map.FakeEeTileLayer(visible=False),
                "vis_params": None,
            },
            "test-map-3": {
                "ee_object": ee.FeatureCollection([]),
                "ee_layer": fake_map.FakeEeTileLayer(visible=True),
                "vis_params": None,
            },
        }
        self.map_fake.click((1, 2), "click")

        expected_point_info = coreutils.new_tree_node(
            "Point (2.00, 1.00) at 1024m/px",
            [
                coreutils.new_tree_node("Longitude: 2"),
                coreutils.new_tree_node("Latitude: 1"),
                coreutils.new_tree_node("Zoom Level: 7"),
                coreutils.new_tree_node("Scale (approx. m/px): 1024"),
            ],
            top_level=True,
        )
        self.assertEqual(self.inspector.point_info, expected_point_info)

        expected_pixel_info = coreutils.new_tree_node(
            "Pixels",
            [
                coreutils.new_tree_node(
                    "test-map-1: Image (2 bands)",
                    [
                        coreutils.new_tree_node("B1: 42", expanded=True),
                        coreutils.new_tree_node("B2: 3.14", expanded=True),
                    ],
                    expanded=True,
                ),
            ],
            top_level=True,
            expanded=True,
        )
        self.assertEqual(self.inspector.pixel_info, expected_pixel_info)

        expected_object_info = coreutils.new_tree_node(
            "Objects",
            [
                coreutils.new_tree_node(
                    "test-map-3: Feature",
                    [
                        coreutils.new_tree_node("type: Feature"),
                        coreutils.new_tree_node("id: 00000000000000000001"),
                        coreutils.new_tree_node(
                            "properties: Object (4 properties)",
                            [
                                coreutils.new_tree_node("fullname: some-full-name"),
                                coreutils.new_tree_node("linearid: 110469267091"),
                                coreutils.new_tree_node("mtfcc: S1400"),
                                coreutils.new_tree_node("rttyp: some-rttyp"),
                            ],
                        ),
                    ],
                ),
            ],
            top_level=True,
            expanded=True,
        )
        self.assertEqual(self.inspector.object_info, expected_object_info)

    def test_map_click_twice(self):
        """Tests that clicking the map a second time resets the point info."""
        self.map_fake.ee_layers = {
            "test-map-1": {
                "ee_object": ee.Image(1),
                "ee_layer": fake_map.FakeEeTileLayer(visible=True),
                "vis_params": None,
            },
        }
        self.map_fake.scale = 32
        self.map_fake.click((1, 2), "click")
        self.map_fake.click((4, 1), "click")

        expected_point_info = coreutils.new_tree_node(
            "Point (1.00, 4.00) at 32m/px",
            [
                coreutils.new_tree_node("Longitude: 1"),
                coreutils.new_tree_node("Latitude: 4"),
                coreutils.new_tree_node("Zoom Level: 7"),
                coreutils.new_tree_node("Scale (approx. m/px): 32"),
            ],
            top_level=True,
        )
        self.assertEqual(self.inspector.point_info, expected_point_info)

    def test_map_click_expanded(self):
        """Tests that nodes are expanded when the expand boolean is true."""
        self.inspector.expand_points = True

        self.map_fake.click((4, 1), "click")

        expected_point_info = coreutils.new_tree_node(
            "Point (1.00, 4.00) at 1024m/px",
            [
                coreutils.new_tree_node("Longitude: 1"),
                coreutils.new_tree_node("Latitude: 4"),
                coreutils.new_tree_node("Zoom Level: 7"),
                coreutils.new_tree_node("Scale (approx. m/px): 1024"),
            ],
            top_level=True,
            expanded=True,
        )
        self.assertEqual(self.inspector.point_info, expected_point_info)


def _create_fake_map() -> fake_map.FakeMap:
    ret = fake_map.FakeMap()
    ret.layers = [
        fake_map.FakeTileLayer("OpenStreetMap"),  # Basemap
        fake_map.FakeTileLayer("GMaps", False, 0.5),  # Extra basemap
        fake_map.FakeEeTileLayer("test-layer", True, 0.8),
        fake_map.FakeGeoJSONLayer(
            "test-geojson-layer",
            False,
            {"some-style": "red", "opacity": 0.3, "fillOpacity": 0.2},
        ),
    ]
    ret.ee_layers = {
        "test-layer": {"ee_object": None, "ee_layer": ret.layers[2], "vis_params": None}
    }
    ret.geojson_layers = [ret.layers[3]]
    return ret


@mock.patch.object(
    map_widgets.LayerManagerRow,
    "_traitlet_link_type",
    new=mock.Mock(return_value=ipywidgets.link),
)  # jslink isn't supported in ipywidgets
class TestLayerManagerRow(unittest.TestCase):
    """Tests for the LayerManagerRow class in the `layer_manager` module."""

    def setUp(self):
        super().setUp()
        self.fake_map = _create_fake_map()

    def test_row_invalid_map_or_layer(self):
        """Tests that a valid map and layer must be passed in."""
        with self.assertRaisesRegex(ValueError, "valid map and layer"):
            map_widgets.LayerManagerRow(None, None)

    def test_row(self):
        """Tests LayerManagerRow is initialized correctly for a standard layer."""
        layer = fake_map.FakeTileLayer(name="layer-name", visible=False, opacity=0.2)
        row = map_widgets.LayerManagerRow(self.fake_map, layer)

        self.assertFalse(row.is_loading)
        self.assertEqual(row.name, layer.name)
        self.assertEqual(row.visible, layer.visible)
        self.assertEqual(row.opacity, layer.opacity)

    def test_geojson_row(self):
        """Tests LayerManagerRow is initialized correctly for a GeoJSON layer."""
        layer = fake_map.FakeGeoJSONLayer(
            name="layer-name", visible=True, style={"opacity": 0.2, "fillOpacity": 0.4}
        )
        self.fake_map.geojson_layers.append(layer)
        row = map_widgets.LayerManagerRow(self.fake_map, layer)

        self.assertEqual(row.name, layer.name)
        self.assertTrue(row.visible)
        self.assertEqual(row.opacity, 0.4)

    def test_layer_update_row_properties(self):
        """Tests layer updates update row traitlets."""
        layer = fake_map.FakeTileLayer(name="layer-name", visible=False, opacity=0.2)
        row = map_widgets.LayerManagerRow(self.fake_map, layer)

        layer.loading = True
        layer.opacity = 0.42
        layer.visible = True
        self.assertTrue(row.is_loading)
        self.assertEqual(row.opacity, 0.42)
        self.assertTrue(row.visible)

    def test_row_update_layer_properties(self):
        """Tests row updates update layer traitlets."""
        layer = fake_map.FakeTileLayer(name="layer-name", visible=False, opacity=0.2)
        row = map_widgets.LayerManagerRow(self.fake_map, layer)

        row.opacity = 0.42
        row.visible = True
        self.assertEqual(layer.opacity, 0.42)
        self.assertTrue(layer.visible)

    def test_geojson_row_update_layer_properties(self):
        """Tests GeoJSON row updates update layer traitlets."""
        layer = fake_map.FakeGeoJSONLayer(
            name="layer-name", visible=True, style={"opacity": 0.2, "fillOpacity": 0.4}
        )
        self.fake_map.geojson_layers.append(layer)
        row = map_widgets.LayerManagerRow(self.fake_map, layer)

        row.opacity = 0.42
        row.visible = True
        self.assertEqual(layer.style["opacity"], 0.42)
        self.assertEqual(layer.style["fillOpacity"], 0.42)
        self.assertTrue(layer.visible)

    def test_settings_button_clicked_non_ee_layer(self):
        """Tests that the layer vis editor is opened when settings is clicked."""
        row = map_widgets.LayerManagerRow(self.fake_map, self.fake_map.layers[0])

        msg = {"type": "click", "id": "settings"}
        row._handle_custom_msg(msg, [])  # pylint: disable=protected-access

        self.fake_map.add.assert_called_once_with(
            "layer_editor", position="bottomright", layer_dict=None
        )

    def test_settings_button_clicked_ee_layer(self):
        """Tests that the layer vis editor is opened when settings is clicked."""
        row = map_widgets.LayerManagerRow(self.fake_map, self.fake_map.layers[2])

        msg = {"type": "click", "id": "settings"}
        row._handle_custom_msg(msg, [])  # pylint: disable=protected-access

        self.fake_map.add.assert_called_once_with(
            "layer_editor",
            position="bottomright",
            layer_dict={
                "ee_object": None,
                "ee_layer": self.fake_map.layers[2],
                "vis_params": None,
            },
        )

    def test_delete_button_clicked(self):
        """Tests that the layer is removed when delete is clicked."""
        row = map_widgets.LayerManagerRow(self.fake_map, self.fake_map.layers[0])

        msg = {"type": "click", "id": "delete"}
        row._handle_custom_msg(msg, [])  # pylint: disable=protected-access

        self.assertEqual(len(self.fake_map.layers), 3)
        self.assertEqual(self.fake_map.layers[0].name, "GMaps")
        self.assertEqual(self.fake_map.layers[1].name, "test-layer")
        self.assertEqual(self.fake_map.layers[2].name, "test-geojson-layer")


class TestLayerManager(unittest.TestCase):
    """Tests for the LayerManager class in the `layer_manager` module."""

    def setUp(self):
        super().setUp()
        self.fake_map = _create_fake_map()
        self.layer_manager = map_widgets.LayerManager(self.fake_map)

    def test_layer_manager_no_map(self):
        """Tests that a valid map must be passed in."""
        with self.assertRaisesRegex(ValueError, "valid map"):
            map_widgets.LayerManager(None)

    def _validate_row(
        self, index: int, name: str, visible: bool, opacity: float
    ) -> None:
        child = self.layer_manager.children[index]
        self.assertEqual(child.host_map, self.fake_map)
        self.assertEqual(child.layer, self.fake_map.layers[index])
        self.assertEqual(child.name, name)
        self.assertEqual(child.visible, visible)
        self.assertAlmostEqual(child.opacity, opacity)

    def test_refresh_layers_updates_children(self):
        """Tests that refresh layers updates children."""
        self.layer_manager.refresh_layers()

        self.assertEqual(len(self.layer_manager.children), len(self.fake_map.layers))
        self._validate_row(0, name="OpenStreetMap", visible=True, opacity=1.0)
        self._validate_row(1, name="GMaps", visible=False, opacity=0.5)
        self._validate_row(2, name="test-layer", visible=True, opacity=0.8)
        self._validate_row(3, name="test-geojson-layer", visible=False, opacity=0.3)

    def test_visibility_updates_children(self):
        """Tests that tweaking the visibility updates children visibilities."""
        self.layer_manager.refresh_layers()
        self.assertTrue(self.layer_manager.visible)

        self.layer_manager.visible = False
        for child in self.layer_manager.children:
            self.assertFalse(child.visible)

        self.layer_manager.visible = True
        for child in self.layer_manager.children:
            self.assertTrue(child.visible)


class TestBasemapSelector(unittest.TestCase):
    """Tests for the BasemapSelector class in the `map_widgets` module."""

    def setUp(self):
        super().setUp()
        self.basemap_list = [
            "DEFAULT",
            "provider.resource-1",
            "provider.resource-2",
            "another-provider",
        ]

    def test_basemap_default(self):
        """Tests that the default values are set."""
        widget = map_widgets.BasemapSelector(self.basemap_list, "provider.resource-1")
        self.assertEqual(
            widget.basemaps,
            {
                "DEFAULT": [],
                "provider": ["resource-1", "resource-2"],
                "another-provider": [],
            },
        )
        self.assertEqual(widget.provider, "provider")
        self.assertEqual(widget.resource, "resource-1")

    def test_basemap_default_no_resource(self):
        """Tests that the default values are set for no resource."""
        widget = map_widgets.BasemapSelector(self.basemap_list, "DEFAULT")
        self.assertEqual(widget.provider, "DEFAULT")
        self.assertEqual(widget.resource, "")

    def test_basemap_close(self):
        """Tests that triggering the closing button fires the close callback."""
        widget = map_widgets.BasemapSelector(self.basemap_list, "DEFAULT")
        on_close_mock = mock.Mock()
        widget.on_close = on_close_mock
        msg = {"type": "click", "id": "close"}
        widget._handle_custom_msg(msg, [])  # pylint: disable=protected-access
        on_close_mock.assert_called_once()

    def test_basemap_change(self):
        """Tests that value change fires the basemap_changed callback."""
        widget = map_widgets.BasemapSelector(self.basemap_list, "provider.resource-2")
        on_apply_mock = mock.Mock()
        widget.on_basemap_changed = on_apply_mock
        msg = {"type": "click", "id": "apply"}
        widget._handle_custom_msg(msg, [])  # pylint: disable=protected-access
        on_apply_mock.assert_called_once_with("provider.resource-2")


@mock.patch.object(ee, "Feature", fake_ee.Feature)
@mock.patch.object(ee, "FeatureCollection", fake_ee.FeatureCollection)
@mock.patch.object(ee, "Geometry", fake_ee.Geometry)
@mock.patch.object(ee, "Image", fake_ee.Image)
class TestLayerEditor(unittest.TestCase):
    """Tests for the `LayerEditor` class in the `map_widgets` module."""

    def _fake_layer_dict(self, ee_object):
        return {
            "ee_object": ee_object,
            "ee_layer": fake_map.FakeEeTileLayer(name="fake-ee-layer-name"),
            "vis_params": {},
        }

    def setUp(self):
        super().setUp()
        self._fake_map = fake_map.FakeMap()
        pyplot.show = mock.Mock()  # Plotting isn't captured by output widgets.

    def test_layer_editor_no_map(self):
        """Tests that a valid map must be passed in."""
        with self.assertRaisesRegex(
            ValueError, "valid map when creating a LayerEditor widget"
        ):
            map_widgets.LayerEditor(None, {})

    def test_layer_editor_feature(self):
        """Tests that an ee.Feature can be passed in."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Feature())
        )
        self.assertEqual(widget.layer_name, "fake-ee-layer-name")
        self.assertEqual(widget.layer_type, "vector")
        self.assertEqual(widget.band_names, [])
        self.assertEqual(widget.colormaps, _get_colormaps())

    def test_layer_editor_geometry(self):
        """Tests that an ee.Geometry can be passed in."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Geometry())
        )
        self.assertEqual(widget.layer_name, "fake-ee-layer-name")
        self.assertEqual(widget.layer_type, "vector")
        self.assertEqual(widget.band_names, [])
        self.assertEqual(widget.colormaps, _get_colormaps())

    def test_layer_editor_feature_collection(self):
        """Tests that an ee.FeatureCollection can be passed in."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.FeatureCollection())
        )
        self.assertEqual(widget.layer_name, "fake-ee-layer-name")
        self.assertEqual(widget.layer_type, "vector")
        self.assertEqual(widget.band_names, [])
        self.assertEqual(widget.colormaps, _get_colormaps())

    def test_layer_editor_image(self):
        """Tests that an ee.Image can be passed in."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        self.assertEqual(widget.layer_name, "fake-ee-layer-name")
        self.assertEqual(widget.layer_type, "raster")
        self.assertEqual(widget.band_names, ["B1", "B2"])
        self.assertEqual(widget.colormaps, _get_colormaps())

    def test_layer_editor_handle_calculate_band_stats(self):
        """Tests that calculate band stats works."""
        send_mock = mock.MagicMock()
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        widget.send = send_mock
        event = {
            "id": "band-stats",
            "type": "calculate",
            "detail": {"bands": ["B1"], "stretch": "sigma-1"},
        }
        widget._handle_message_event(None, event, None)

        response = {
            "type": "calculate",
            "id": "band-stats",
            "response": {"stretch": "sigma-1", "min": 21, "max": 42},
        }
        widget.send.assert_called_once_with(response)

    def test_layer_editor_handle_calculate_palette(self):
        """Tests that calculate palette works."""
        send_mock = mock.MagicMock()
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        widget.send = send_mock
        event = {
            "detail": {
                "bandMax": 0.742053968164132,
                "bandMin": 0.14069852859491755,
                "classes": "3",
                "colormap": "Blues",
                "palette": "",
            },
            "id": "palette",
            "type": "calculate",
        }
        widget._handle_message_event(None, event, None)

        response = {
            "type": "calculate",
            "id": "palette",
            "response": {"palette": "#f7fbff, #6baed6, #08306b"},
        }
        widget.send.assert_called_once_with(response)

    def test_layer_editor_handle_calculate_field(self):
        """Tests that calculate fields works."""
        send_mock = mock.MagicMock()
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.FeatureCollection())
        )
        widget.send = send_mock
        event = {"detail": {}, "id": "fields", "type": "calculate"}
        widget._handle_message_event(None, event, None)

        response = {
            "type": "calculate",
            "id": "fields",
            "response": {
                "fields": ["prop-1", "prop-2"],
                "field-values": ["aggregation-one", "aggregation-two"],
            },
        }
        widget.send.assert_called_once_with(response)

    def test_layer_editor_handle_calculate_field_values(self):
        """Tests that calculate field values works."""
        send_mock = mock.MagicMock()
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.FeatureCollection())
        )
        widget.send = send_mock
        event = {
            "detail": {"field": "prop-1"},
            "id": "field-values",
            "type": "calculate",
        }
        widget._handle_message_event(None, event, None)

        response = {
            "type": "calculate",
            "id": "field-values",
            "response": {"field-values": ["aggregation-one", "aggregation-two"]},
        }
        widget.send.assert_called_once_with(response)

    def test_layer_editor_handle_close_click(self):
        """Tests that close click events are handled."""
        on_close_mock = mock.MagicMock()
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.FeatureCollection())
        )
        widget.on_close = on_close_mock
        event = {"id": "close", "type": "click"}
        widget._handle_message_event(None, event, None)

        on_close_mock.assert_called_once_with()

    def test_calculate_band_stats(self):
        """Tests calculating band stats with various stretches."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        # Custom stretch returns None.
        event = {"id": "band-stats", "type": "calculate"}
        detail = {"bands": ["B1"], "stretch": "custom"}
        self.assertIsNone(widget._calculate_band_stats(detail))

        # Percent stretch
        detail = {"bands": ["B1"], "stretch": "percent (98%)"}
        with mock.patch.object(widget._ee_layer, 'calculate_vis_minmax') as minmax_mock:
            minmax_mock.return_value = (0, 100)
            result = widget._calculate_band_stats(detail)
            self.assertEqual(result, {"stretch": "percent (98%)", "min": 0, "max": 100})
            minmax_mock.assert_called_once()
            self.assertEqual(minmax_mock.call_args[1]["percent"], 0.98)

        # Sigma stretch
        detail = {"bands": ["B1"], "stretch": "sigma (2)"}
        with mock.patch.object(widget._ee_layer, 'calculate_vis_minmax') as minmax_mock:
            minmax_mock.return_value = (10, 20)
            result = widget._calculate_band_stats(detail)
            self.assertEqual(result, {"stretch": "sigma (2)", "min": 10, "max": 20})
            minmax_mock.assert_called_once()
            self.assertEqual(minmax_mock.call_args[1]["sigma"], 2)

    @mock.patch.object(map_widgets.pyplot, "subplots")
    def test_render_colorbar(self, subplots_mock):
        """Tests rendering of a colorbar."""
        fig_mock = mock.MagicMock()
        ax_mock = mock.MagicMock()
        subplots_mock.return_value = (fig_mock, ax_mock)

        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )

        # Test short list.
        widget._render_colorbar(["#ff0000"], 0, 1)
        self.assertEqual(list(widget.children), [])

        # Test valid list.
        with mock.patch("matplotlib.colors.LinearSegmentedColormap.from_list") as from_list_mock, \
             mock.patch("matplotlib.colors.Normalize") as norm_mock, \
             mock.patch("matplotlib.colorbar.ColorbarBase") as colorbar_mock:

            widget._render_colorbar(["#ff0000", "#00ff00"], 0, 1)
            from_list_mock.assert_called_once_with("custom", ["#ff0000", "#00ff00"], N=256)
            norm_mock.assert_called_once_with(vmin=0, vmax=1)
            colorbar_mock.assert_called_once()
            self.assertEqual(len(widget.children), 1)

    def test_calculate_palette(self):
        """Tests calculating palettes with predefined and custom colormaps."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        widget._render_colorbar = mock.MagicMock()

        # Custom palette.
        detail = {"colormap": "Custom", "palette": "#ff0000,#00ff00", "bandMin": 0.0, "bandMax": 1.0}
        res = widget._calculate_palette(detail)
        self.assertEqual(res, {"palette": "#ff0000,#00ff00"})
        widget._render_colorbar.assert_called_once_with(["#ff0000", "#00ff00"], 0.0, 1.0)

        # Named palette.
        widget._render_colorbar.reset_mock()
        detail = {"colormap": "viridis", "classes": "3"}
        with mock.patch.object(map_widgets.pyplot, "get_cmap") as get_cmap_mock:
            cmap_mock = mock.MagicMock()
            cmap_mock.N = 3
            # We must return different mock values when it's called with an index
            # Mock it to return simple tuples to keep rgb2hex happy.
            cmap_mock.side_effect = [(0, 0, 0, 1), (0.5, 0.5, 0.5, 1), (1, 1, 1, 1)]
            get_cmap_mock.return_value = cmap_mock

            res = widget._calculate_palette(detail)
            get_cmap_mock.assert_called_once_with("viridis", 3)
            self.assertIn("palette", res)
            widget._render_colorbar.assert_called_once()

    @mock.patch.object(coreutils, "create_code_cell")
    def test_on_import_click(self, create_code_cell_mock):
        """Tests the import click event handlers."""
        # Raster
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        widget._on_import_click_raster({"opacity": 0.5, "min": 0, "max": 1})
        create_code_cell_mock.assert_called_once_with("vis_params = {'min': 0, 'max': 1}")

        # Vector
        create_code_cell_mock.reset_mock()
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.FeatureCollection([]))
        )
        widget._on_import_click_vector({"color": "#ff0000", "fillColor": "#00ff00", "opacity": 0.5})
        create_code_cell_mock.assert_called_once()
        self.assertIn("style = ", create_code_cell_mock.call_args[0][0])
        self.assertIn("'color': 'ff00007f'", create_code_cell_mock.call_args[0][0]) # 0.5 * 255 = 127 = 7f

    @mock.patch.object(fake_map.FakeMap, "add_layer")
    @mock.patch.object(fake_map.FakeMap, "remove_layer")
    def test_on_apply_click_vector(self, remove_mock, add_layer_mock):
        """Tests apply vector changes."""
        # Style by attribute False.
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.FeatureCollection([]))
        )
        widget._host_map.remove = remove_mock
        widget._host_map.ee_layers = {widget.layer_name: {}}

        detail = {
            "shouldStyleByAttribute": False,
            "layerName": "new_layer",
            "color": "#ff0000",
            "opacity": 1.0,
            "fillColor": "#00ff00",
        }
        widget._on_apply_click_vector(detail)
        remove_mock.assert_called_once_with(widget._ee_layer)
        add_layer_mock.assert_called_once()
        self.assertEqual(add_layer_mock.call_args[0][2], "new_layer")

        # Style by attribute True
        remove_mock.reset_mock()
        add_layer_mock.reset_mock()
        detail2 = {
            "shouldStyleByAttribute": True,
            "layerName": "styled_layer",
            "color": "#000000",
            "fillColor": "#ffffff",
            "palette": ["#ff0000", "#00ff00"],
            "field": "test_field"
        }
        # Avoid full ee tracing by mocking ee methods
        with mock.patch.object(widget._ee_object, "aggregate_array") as agg_mock, \
             mock.patch.object(widget._ee_object, "map", create=True) as map_mock, \
             mock.patch("ee.Number") as ee_num_mock, \
             mock.patch("ee.List") as ee_list_mock:
            distinct_mock = mock.MagicMock()
            sort_mock = mock.MagicMock()
            sort_mock.size.return_value = mock.MagicMock()
            distinct_mock.sort.return_value = sort_mock
            agg_mock.return_value.distinct.return_value = distinct_mock

            map_res_mock = mock.MagicMock()
            map_res_mock.style.return_value = "styled_fc"
            # It chains `fc.map(f1).map(f2)`
            map_res_mock.map.return_value = map_res_mock
            map_mock.return_value = map_res_mock

            widget._on_apply_click_vector(detail2)
            add_layer_mock.assert_called_once()
            self.assertEqual(add_layer_mock.call_args[0][0], "styled_fc")
            self.assertEqual(add_layer_mock.call_args[0][2], "styled_layer")

    @mock.patch("tests.fake_map.FakeMap.add_layer")
    def test_on_apply_click_raster(self, add_layer_mock):
        """Tests applying raster properties."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        with mock.patch.object(widget, "_apply_legend") as apply_legend_mock:
            detail = {"opacity": 0.8, "min": 0, "max": 1, "legend": {"type": "linear"}}
            widget._on_apply_click_raster(detail)

            add_layer_mock.assert_called_once_with(
                widget._ee_object, {"min": 0, "max": 1}, widget.layer_name, True, 0.8
            )
            self.assertFalse(widget._ee_layer.visible)
            apply_legend_mock.assert_called_once()

    def test_apply_legend(self):
        """Tests legend application."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        with mock.patch.object(widget._host_map, "_add_colorbar", create=True) as add_colorbar_mock, \
             mock.patch.object(widget._host_map, "_add_legend", create=True) as add_legend_mock:
            # Linear legend
            widget._apply_legend({"type": "linear"}, "palette", 0, 1)
            add_colorbar_mock.assert_called_once()

            # Step legend
            widget._apply_legend({"type": "step"}, "palette", 0, 1)
            add_legend_mock.assert_called_once()

    def test_handle_message_event_extra(self):
        """Tests remaining handle_message_event branches."""
        widget = map_widgets.LayerEditor(
            self._fake_map, self._fake_layer_dict(ee.Image())
        )
        widget._on_apply_click_raster = mock.MagicMock()
        widget._on_import_click_raster = mock.MagicMock()
        widget._calculate_palette = mock.MagicMock()
        widget._calculate_palette.return_value = {"palette": "res"}

        widget._handle_message_event(None, {"type": "click", "id": "apply"}, None)
        widget._on_apply_click_raster.assert_called_once()

        widget._handle_message_event(None, {"type": "click", "id": "import"}, None)
        widget._on_import_click_raster.assert_called_once()

        widget.send = mock.MagicMock()
        widget._handle_message_event(None, {"type": "calculate", "id": "palette"}, None)
        widget._calculate_palette.assert_called_once()
        widget.send.assert_called_once_with({"type": "calculate", "id": "palette", "response": {"palette": "res"}})

class TestSearchBar(unittest.TestCase):
    """Tests for the SearchBar class in the `map_widgets` module."""

    def setUp(self) -> None:
        super().setUp()
        self._fake_map = fake_map.FakeMap()
        # Mock the missing attributes for FakeMap
        setattr(fake_map.FakeMap, 'search_locations', [])
        setattr(fake_map.FakeMap, 'search_loc_marker', None)
        setattr(fake_map.FakeMap, 'search_loc_geom', None)
        setattr(fake_map.FakeMap, 'search_datasets', [])
        setattr(fake_map.FakeMap, 'center', (0, 0))
        setattr(fake_map.FakeMap, 'remove', mock.MagicMock())
        setattr(fake_map.FakeMap, '_var_name', 'Map')

        self._fake_map.search_locations = []
        self._fake_map.search_loc_marker = None
        self._fake_map.search_loc_geom = None
        self._fake_map.search_datasets = []
        self._fake_map.center = (0, 0)
        self._fake_map.remove = mock.MagicMock()
        self._fake_map._var_name = 'Map'

    def test_search_bar_init(self):
        """Tests that the SearchBar initializes correctly."""
        widget = map_widgets.SearchBar(self._fake_map)
        self.assertEqual(widget.host_map, self._fake_map)
        self.assertEqual(widget.host_map.search_locations, None)
        self.assertEqual(widget.host_map.search_loc_marker, None)
        self.assertEqual(widget.host_map.search_loc_geom, None)
        self.assertEqual(widget.host_map.search_datasets, None)

    @mock.patch("geemap.common.geocode")
    def test_search_location_success(self, geocode_mock):
        """Tests searching for a valid location."""
        mock_result = mock.MagicMock()
        mock_result.address = "Test Address"
        mock_result.lat = 10.0
        mock_result.lng = 20.0
        geocode_mock.return_value = [mock_result]

        widget = map_widgets.SearchBar(self._fake_map)
        widget._search_location("Test Query")

        geocode_mock.assert_called_once_with("Test Query")
        self.assertEqual(self._fake_map.search_locations, [mock_result])

        location_model = json.loads(widget.location_model)
        self.assertEqual(location_model["results"], ["Test Address"])

    @mock.patch("geemap.common.geocode")
    def test_search_location_failure(self, geocode_mock):
        """Tests searching for an invalid location."""
        geocode_mock.return_value = None

        widget = map_widgets.SearchBar(self._fake_map)
        widget._search_location("Invalid Query")

        geocode_mock.assert_called_once_with("Invalid Query")

        location_model = json.loads(widget.location_model)
        self.assertEqual(location_model["results"], [])
        self.assertEqual(location_model["selected"], "")
        self.assertEqual(location_model["additional_html"], "No results could be found.")

    @mock.patch("ee.Geometry.Point")
    def test_set_selected_location(self, ee_point_mock):
        """Tests selecting a searched location."""
        mock_result = mock.MagicMock()
        mock_result.address = "Selected Address"
        mock_result.lat = 30.0
        mock_result.lng = 40.0
        self._fake_map.search_locations = [mock_result]
        self._fake_map.search_loc_marker = None

        widget = map_widgets.SearchBar(self._fake_map)
        # Ensure it's mocked
        widget.host_map.add = mock.MagicMock()
        widget.host_map.search_locations = [mock_result]

        widget._set_selected_location("Selected Address")

        self.assertIsNotNone(self._fake_map.search_loc_marker)
        self.assertEqual(list(self._fake_map.search_loc_marker.location), [30.0, 40.0])
        self.assertEqual(self._fake_map.center, (30.0, 40.0))
        widget.host_map.add.assert_called_once()

        # Test update existing marker
        mock_result_2 = mock.MagicMock()
        mock_result_2.address = "Selected Address 2"
        mock_result_2.lat = 50.0
        mock_result_2.lng = 60.0
        self._fake_map.search_locations.append(mock_result_2)
        widget._set_selected_location("Selected Address 2")
        self.assertEqual(list(self._fake_map.search_loc_marker.location), [50.0, 60.0])
        self.assertEqual(self._fake_map.center, (50.0, 60.0))

        # Test invalid location
        widget._set_selected_location("Non-existent Address")
        self.assertEqual(self._fake_map.center, (50.0, 60.0)) # Unchanged

    @mock.patch("geemap.common.geocode")
    @mock.patch("geemap.common.latlon_from_text")
    @mock.patch("ee.Geometry.Point")
    def test_search_lat_lon(self, ee_point_mock, latlon_from_text_mock, geocode_mock):
        """Tests searching for a lat/lon coordinate."""
        latlon_from_text_mock.return_value = (12.3, 45.6)

        mock_result = mock.MagicMock()
        mock_result.address = "Lat/Lon Address"
        mock_result.lat = 12.3
        mock_result.lng = 45.6
        geocode_mock.return_value = [mock_result]

        widget = map_widgets.SearchBar(self._fake_map)
        widget.host_map.add = mock.MagicMock()
        widget.host_map.search_locations = []
        widget._search_lat_lon("12.3, 45.6")

        geocode_mock.assert_called_once_with("12.3, 45.6", reverse=True)

        location_model = json.loads(widget.location_model)
        self.assertEqual(location_model["results"], ["Lat/Lon Address"])
        self.assertEqual(location_model["selected"], "Lat/Lon Address")
        self.assertEqual(location_model["additional_html"], "")

        self.assertIsNotNone(self._fake_map.search_loc_marker)
        self.assertEqual(list(self._fake_map.search_loc_marker.location), [12.3, 45.6])
        self.assertEqual(self._fake_map.center, (12.3, 45.6))

        # Update existing marker
        widget._search_lat_lon("12.3, 45.6")
        self.assertEqual(list(self._fake_map.search_loc_marker.location), [12.3, 45.6])

        # No geocode results
        geocode_mock.return_value = None
        widget._search_lat_lon("12.3, 45.6")
        location_model = json.loads(widget.location_model)
        self.assertEqual(location_model["results"], [])
        self.assertEqual(location_model["selected"], "")
        self.assertEqual(location_model["additional_html"], "No results could be found.")

    @mock.patch("geemap.common.latlon_from_text")
    def test_search_lat_lon_invalid(self, latlon_from_text_mock):
        """Tests searching for an invalid lat/lon coordinate."""
        latlon_from_text_mock.return_value = False

        widget = map_widgets.SearchBar(self._fake_map)
        widget._search_lat_lon("invalid_lat_lon")

        location_model = json.loads(widget.location_model)
        self.assertEqual(location_model["results"], [])
        self.assertEqual(location_model["selected"], "")
        self.assertIn("The lat-lon coordinates should be numbers only", location_model["additional_html"])

    @mock.patch("geemap.common.ee_data_html")
    @mock.patch("geemap.common.search_ee_data")
    def test_search_dataset(self, search_ee_data_mock, ee_data_html_mock):
        """Tests searching for an Earth Engine dataset."""
        mock_dataset = {"title": "Dataset 1", "id": "test/dataset1", "type": "image"}
        search_ee_data_mock.return_value = [mock_dataset]
        ee_data_html_mock.return_value = "<p>Dataset 1 Info</p>"

        widget = map_widgets.SearchBar(self._fake_map)
        widget._search_dataset("Test Dataset Search")

        search_ee_data_mock.assert_called_once_with("Test Dataset Search", source="all")
        self.assertEqual(self._fake_map.search_datasets, [mock_dataset])

        dataset_model = json.loads(widget.dataset_model)
        self.assertEqual(dataset_model["results"], ["Dataset 1"])
        self.assertEqual(dataset_model["selected"], "Dataset 1")
        self.assertEqual(dataset_model["additional_html"], "<p>Dataset 1 Info</p>")

        # Test no results
        search_ee_data_mock.return_value = []
        widget._search_dataset("Empty Dataset")
        dataset_model = json.loads(widget.dataset_model)
        self.assertEqual(dataset_model["results"], [])
        self.assertEqual(dataset_model["selected"], "")
        self.assertEqual(dataset_model["additional_html"], "No results found.")

    @mock.patch("geemap.common.ee_data_html")
    def test_select_dataset(self, ee_data_html_mock):
        """Tests selecting a searched Earth Engine dataset."""
        mock_dataset = {"title": "Selected Dataset", "id": "test/selected", "type": "image"}
        self._fake_map.search_datasets = [mock_dataset]
        ee_data_html_mock.return_value = "<p>Selected Info</p>"

        widget = map_widgets.SearchBar(self._fake_map)
        widget.host_map.search_datasets = [mock_dataset]
        widget._select_dataset("Selected Dataset")

        dataset_model = json.loads(widget.dataset_model)
        self.assertEqual(dataset_model["additional_html"], "<p>Selected Info</p>")

        # Test non-existent dataset
        widget._select_dataset("Non-existent")
        dataset_model_2 = json.loads(widget.dataset_model)
        self.assertEqual(dataset_model_2["additional_html"], "<p>Selected Info</p>") # Unchanged

    @mock.patch("geemap.coreutils.random_string")
    def test_import_button_clicked_image(self, random_string_mock):
        """Tests the import button click for a dataset."""
        random_string_mock.return_value = "123"
        mock_dataset = {"title": "To Import", "id": "test/import_img", "type": "image"}
        self._fake_map.search_datasets = [mock_dataset]

        widget = map_widgets.SearchBar(self._fake_map)
        widget.host_map.search_datasets = [mock_dataset]
        dataset_model = json.loads(widget.dataset_model)
        dataset_model["selected"] = "To Import"
        with mock.patch.object(widget, '_select_dataset'):
            widget.dataset_model = json.dumps(dataset_model)

        widget.import_button_clicked()

        updated_model = json.loads(widget.dataset_model)
        self.assertIn("dataset_123 = ee.Image('test/import_img')", updated_model["additional_html"])
        self.assertIn("addLayer(dataset_123, {}, 'test/import_img')", updated_model["additional_html"])

        # Test unselected
        dataset_model["selected"] = ""
        with mock.patch.object(widget, '_select_dataset'):
            widget.dataset_model = json.dumps(dataset_model)
        widget.import_button_clicked()

    @mock.patch("geemap.coreutils.random_string")
    def test_import_button_clicked_table(self, random_string_mock):
        """Tests the import button click for a dataset."""
        random_string_mock.return_value = "123"
        mock_dataset = {"title": "To Import", "id": "test/import_tbl", "type": "table"}
        self._fake_map.search_datasets = [mock_dataset]

        widget = map_widgets.SearchBar(self._fake_map)
        widget.host_map.search_datasets = [mock_dataset]
        dataset_model = json.loads(widget.dataset_model)
        dataset_model["selected"] = "To Import"
        with mock.patch.object(widget, '_select_dataset'):
            widget.dataset_model = json.dumps(dataset_model)

        widget.import_button_clicked()

        updated_model = json.loads(widget.dataset_model)
        self.assertIn("dataset_123 = ee.FeatureCollection('test/import_tbl')", updated_model["additional_html"])
        self.assertIn("addLayer(dataset_123, {}, 'test/import_tbl')", updated_model["additional_html"])

    def test_observe_location_model(self):
        """Tests observing the location model traits."""
        widget = map_widgets.SearchBar(self._fake_map)
        widget._search_location = mock.MagicMock()
        widget._search_lat_lon = mock.MagicMock()
        widget._set_selected_location = mock.MagicMock()

        # Test search changes (normal text)
        with mock.patch("geemap.common.latlon_from_text", return_value=False):
            change = {
                "old": json.dumps({"search": "", "selected": ""}),
                "new": json.dumps({"search": "New Query", "selected": ""}),
            }
            widget._observe_location_model(change)
            widget._search_location.assert_called_once_with("New Query")

        # Test search changes (lat/lon)
        with mock.patch("geemap.common.latlon_from_text", return_value=True):
            change = {
                "old": json.dumps({"search": "", "selected": ""}),
                "new": json.dumps({"search": "10, 20", "selected": ""}),
            }
            widget._observe_location_model(change)
            widget._search_lat_lon.assert_called_once_with("10, 20")

        # Test clear search
        marker = ipyleaflet.Marker(location=(0,0))
        widget.host_map.search_loc_marker = marker
        widget.host_map.remove = mock.MagicMock()
        change = {
            "old": json.dumps({"search": "old", "selected": ""}),
            "new": json.dumps({"search": "", "selected": ""}),
        }
        widget._observe_location_model(change)
        self.assertIsNone(widget.host_map.search_loc_marker)
        widget.host_map.remove.assert_called_once_with(marker)

        # Test selection changes
        change = {
            "old": json.dumps({"search": "Same", "selected": "Old"}),
            "new": json.dumps({"search": "Same", "selected": "New Selected"}),
        }
        widget._observe_location_model(change)
        widget._set_selected_location.assert_called_once_with("New Selected")

    def test_observe_dataset_model(self):
        """Tests observing the dataset model traits."""
        widget = map_widgets.SearchBar(self._fake_map)
        widget._search_dataset = mock.MagicMock()
        widget._select_dataset = mock.MagicMock()

        # Test search changes
        change = {
            "old": json.dumps({"search": "", "selected": ""}),
            "new": json.dumps({"search": "New Dataset", "selected": ""}),
        }
        widget._observe_dataset_model(change)
        widget._search_dataset.assert_called_once_with("New Dataset")

        # Test clear search
        change = {
            "old": json.dumps({"search": "old", "selected": ""}),
            "new": json.dumps({"search": "", "selected": ""}),
        }
        widget._observe_dataset_model(change)
        dataset_model = json.loads(widget.dataset_model)
        self.assertEqual(dataset_model["search"], "")

        # Test selection changes
        change = {
            "old": json.dumps({"search": "Same", "selected": "Old"}),
            "new": json.dumps({"search": "Same", "selected": "New Selected Dataset"}),
        }
        widget._observe_dataset_model(change)
        widget._select_dataset.assert_called_once_with("New Selected Dataset")

    def test_handle_message_event(self):
        """Tests handling message events from the widget."""
        widget = map_widgets.SearchBar(self._fake_map)
        widget.import_button_clicked = mock.MagicMock()
        widget.cleanup = mock.MagicMock()

        widget.handle_message_event(widget, {"type": "click", "id": "import"}, [])
        widget.import_button_clicked.assert_called_once()

        widget.handle_message_event(widget, {"type": "click", "id": "close"}, [])
        widget.cleanup.assert_called_once()

    def test_cleanup(self):
        widget = map_widgets.SearchBar(self._fake_map)
        widget.on_close = mock.MagicMock()
        widget.cleanup()
        widget.on_close.assert_called_once()
