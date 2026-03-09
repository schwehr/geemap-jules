#!/usr/bin/env python
"""Tests for `map_widgets` module."""
import dataclasses
import builtins
import ipyleaflet
import unittest
from unittest import mock

import geemap
from geemap import toolbar


class TestToolbar(unittest.TestCase):
    """Tests for the Toolbar class in the `toolbar` module."""

    callback_calls: int
    last_called_with_selected: bool | None
    last_called_item: toolbar.ToolbarItem | None
    item: toolbar.ToolbarItem
    reset_item: toolbar.ToolbarItem

    def setUp(self):
        super().setUp()
        self.callback_calls = 0
        self.last_called_with_selected = None
        self.last_called_item = None
        self.item = toolbar.ToolbarItem(
            icon="info", tooltip="dummy item", callback=self.dummy_callback
        )
        self.reset_item = toolbar.ToolbarItem(
            icon="question",
            tooltip="no reset item",
            callback=self.dummy_callback,
            reset=True,
        )

    def dummy_callback(self, m, selected, item):
        del m  # Unused.
        self.last_called_with_selected = selected
        self.last_called_item = item
        self.callback_calls += 1

    def test_no_tools_throws(self):
        a_map = geemap.Map(ee_initialize=False)
        self.assertRaises(ValueError, toolbar.Toolbar, a_map, [], [])

    def test_only_main_tools_exist_if_no_extra_tools(self):
        a_map = geemap.Map(ee_initialize=False)
        a_toolboor = toolbar.Toolbar(a_map, [self.item], [])
        self.assertNotIn(a_toolboor.toggle_widget, a_toolboor.main_tools)

    def test_all_tools_and_toggle_exist_if_extra_tools(self):
        a_map = geemap.Map(ee_initialize=False)
        a_toolboor = toolbar.Toolbar(a_map, [self.item], [self.reset_item])
        self.assertIsNotNone(a_toolboor.toggle_widget)

    def test_toggle_expands_and_collapses(self):
        """Toggle widget correctly expands and collapses the toolbar."""
        a_map = geemap.Map(ee_initialize=False)
        a_toolboor = toolbar.Toolbar(a_map, [self.item], [self.reset_item])
        self.assertIsNotNone(a_toolboor.toggle_widget)
        toggle = a_toolboor.toggle_widget
        self.assertEqual(toggle.icon, "add")
        self.assertEqual(toggle.tooltip_text, "Expand toolbar")
        self.assertFalse(a_toolboor.expanded)

        # Expand
        toggle.active = True
        self.assertTrue(a_toolboor.expanded)
        self.assertEqual(toggle.icon, "remove")
        self.assertEqual(toggle.tooltip_text, "Collapse toolbar")
        # After expanding, button is unselected.
        self.assertFalse(toggle.active)

        # Collapse
        toggle.active = True
        self.assertFalse(a_toolboor.expanded)
        self.assertEqual(toggle.icon, "add")
        self.assertEqual(toggle.tooltip_text, "Expand toolbar")
        # After collapsing, button is unselected.
        self.assertFalse(toggle.active)

    def test_triggers_callbacks(self):
        """Tests that toolbar item callbacks are triggered correctly."""
        a_map = geemap.Map(ee_initialize=False)
        a_toolboor = toolbar.Toolbar(a_map, [self.item, self.reset_item], [])
        self.assertIsNone(self.last_called_with_selected)
        self.assertIsNone(self.last_called_item)

        # Select first tool, which does not reset.
        a_toolboor.main_tools[0].active = True
        self.assertTrue(self.last_called_with_selected)
        self.assertEqual(self.callback_calls, 1)
        self.assertTrue(a_toolboor.main_tools[0].active)
        self.assertEqual(self.item, self.last_called_item)

        # Select second tool, which resets.
        a_toolboor.main_tools[1].active = True
        # Was reset by callback.
        self.assertFalse(self.last_called_with_selected)
        self.assertEqual(self.callback_calls, 3)
        self.assertFalse(a_toolboor.main_tools[1].active)
        self.assertEqual(self.reset_item, self.last_called_item)

    @dataclasses.dataclass
    class TestWidget:
        selected_count: int = 0
        cleanup_count: int = 0

        def cleanup(self):
            self.cleanup_count += 1

    def test_cleanup_toolbar_item_decorator(self):
        """Tests the _cleanup_toolbar_item decorator functionality."""
        widget = TestToolbar.TestWidget()

        # pylint: disable-next=protected-access
        @toolbar._cleanup_toolbar_item
        def callback(m, selected, item):
            del m, selected, item  # Unused.
            widget.selected_count += 1
            return widget

        item = toolbar.ToolbarItem(
            icon="info", tooltip="dummy item", callback=callback, reset=False
        )
        a_map = geemap.Map(ee_initialize=False)
        a_toolboor = toolbar.Toolbar(a_map, [item], [])
        a_toolboor.main_tools[0].active = True
        self.assertEqual(1, widget.selected_count)
        self.assertEqual(0, widget.cleanup_count)

        a_toolboor.main_tools[0].active = False
        self.assertEqual(1, widget.selected_count)
        self.assertEqual(1, widget.cleanup_count)

        a_toolboor.main_tools[0].active = True
        self.assertEqual(2, widget.selected_count)
        self.assertEqual(1, widget.cleanup_count)

        widget.cleanup()
        self.assertEqual(2, widget.selected_count)
        self.assertEqual(3, widget.cleanup_count)
        self.assertFalse(a_toolboor.main_tools[0].active)




class TestToolbarCallbacks(unittest.TestCase):
    @mock.patch.object(geemap.common, 'planet_tiles')
    @mock.patch.object(toolbar, 'split_basemaps')
    def test_split_basemaps_tool_callback(self, mock_split_basemaps, mock_planet_tiles):
        m = mock.MagicMock()
        item = mock.MagicMock()

        toolbar._split_basemaps_tool_callback(m, True, item)
        mock_split_basemaps.assert_called_once()
        mock_split_basemaps.reset_mock()
        toolbar._split_basemaps_tool_callback(m, False, item)
        mock_split_basemaps.assert_not_called()

    def test_open_help_page_callback(self):
        m = mock.MagicMock()
        item = mock.MagicMock()
        with mock.patch('webbrowser.open_new_tab') as mock_open_new_tab:
            toolbar._open_help_page_callback(m, True, item)
            mock_open_new_tab.assert_called_once_with("https://geemap.org")
            mock_open_new_tab.reset_mock()
            toolbar._open_help_page_callback(m, False, item)
            mock_open_new_tab.assert_not_called()

    @mock.patch.object(toolbar, 'ee_plot_gui')
    def test_plotting_tool_callback(self, mock_ee_plot_gui):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._plotting_tool_callback(m, True, item)
        mock_ee_plot_gui.assert_called_once_with(m)
        self.assertEqual(item.control, m._plot_dropdown_control)

    def test_inspector_tool_callback(self):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._inspector_tool_callback(m, True, item)
        m.add_inspector.assert_called_once()
        self.assertEqual(item.control, m._inspector)

    @mock.patch.object(toolbar, 'timelapse_gui')
    def test_timelapse_tool_callback(self, mock_timelapse_gui):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._timelapse_tool_callback(m, True, item)
        mock_timelapse_gui.assert_called_once_with(m)
        self.assertEqual(item.control, m.tool_control)

    @mock.patch.object(toolbar, 'convert_js2py')
    def test_convert_js_tool_callback(self, mock_convert_js2py):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._convert_js_tool_callback(m, True, item)
        mock_convert_js2py.assert_called_once_with(m)
        self.assertEqual(item.control, m._convert_ctrl)

    def test_basemap_tool_callback(self):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._basemap_tool_callback(m, True, item)
        m.add_basemap_widget.assert_called_once()
        self.assertEqual(item.control, m._basemap_selector)

    @mock.patch.object(toolbar, 'open_data_widget')
    def test_open_data_tool_callback(self, mock_open_data_widget):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._open_data_tool_callback(m, True, item)
        mock_open_data_widget.assert_called_once_with(m)
        self.assertEqual(item.control, m._tool_output_ctrl)

    @mock.patch.object(toolbar, 'build_toolbox')
    @mock.patch.object(toolbar, 'get_tools_dict')
    @mock.patch.object(ipyleaflet, 'WidgetControl')
    def test_gee_toolbox_tool_callback(self, mock_WidgetControl, mock_get_tools_dict, mock_build_toolbox):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._gee_toolbox_tool_callback(m, True, item)
        mock_build_toolbox.assert_called_once()
        mock_get_tools_dict.assert_called_once()
        m.add.assert_called_once_with(mock_WidgetControl.return_value)

    @mock.patch.object(toolbar, 'time_slider')
    def test_time_slider_tool_callback(self, mock_time_slider):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._time_slider_tool_callback(m, True, item)
        mock_time_slider.assert_called_once_with(m)
        self.assertEqual(item.control, m.tool_control)

    @mock.patch.object(toolbar, 'collect_samples')
    def test_collect_samples_tool_callback(self, mock_collect_samples):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._collect_samples_tool_callback(m, True, item)
        mock_collect_samples.assert_called_once_with(m)
        self.assertEqual(item.control, m.training_ctrl)

    @mock.patch.object(toolbar, 'plot_transect')
    def test_plot_transect_tool_callback(self, mock_plot_transect):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._plot_transect_tool_callback(m, True, item)
        mock_plot_transect.assert_called_once_with(m)
        self.assertEqual(item.control, m.tool_control)

    @mock.patch.object(toolbar, 'sankee_gui')
    def test_sankee_tool_callback(self, mock_sankee_gui):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._sankee_tool_callback(m, True, item)
        mock_sankee_gui.assert_called_once_with(m)
        self.assertEqual(item.control, m.tool_control)

    @mock.patch.object(toolbar, 'inspector_gui')
    def test_cog_stac_inspector_callback(self, mock_inspector_gui):
        m = mock.MagicMock()
        item = mock.MagicMock()
        toolbar._cog_stac_inspector_callback(m, True, item)
        mock_inspector_gui.assert_called_once_with(m)
        self.assertEqual(item.control, m.tool_control)

    @mock.patch.object(ipyleaflet, 'WidgetControl')
    def test_whitebox_tool_callback(self, mock_WidgetControl):
        m = mock.MagicMock()
        item = mock.MagicMock()
        with mock.patch.dict('sys.modules', {'whiteboxgui': mock.MagicMock(), 'whiteboxgui.whiteboxgui': mock.MagicMock()}):
            toolbar._whitebox_tool_callback(m, True, item)
            m.add.assert_called_once()


class TestToolbarGetTools(unittest.TestCase):
    def test_get_main_tools(self):
        tools = toolbar.get_main_tools()
        self.assertIsInstance(tools, list)
        self.assertTrue(len(tools) > 0)
        self.assertIsInstance(tools[0], toolbar.ToolbarItem)

    def test_get_extra_tools(self):
        tools = toolbar.get_extra_tools()
        self.assertIsInstance(tools, list)
        self.assertTrue(len(tools) > 0)
        self.assertIsInstance(tools[0], toolbar.ToolbarItem)


if __name__ == "__main__":
    unittest.main()
