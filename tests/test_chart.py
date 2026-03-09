"""Tests for `chart` module."""

import unittest

import pandas as pd
from unittest.mock import patch, MagicMock

from geemap import chart


class ChartTest(unittest.TestCase):
    """Tests for `chart` module."""

    def test_data_table_dict(self):
        """Test DataTable with a dictionary."""
        data = {"col1": [1, 2], "col2": [3, 4], "date": ["2022-01-01", "2022-01-02"]}
        dt = chart.DataTable(data, date_column="date")
        self.assertIsInstance(dt, chart.DataTable)
        self.assertEqual(dt.shape, (2, 3))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(dt["date"]))

    def test_data_table_df(self):
        """Test DataTable with a pandas DataFrame."""
        data = {"col1": [1, 2], "col2": [3, 4], "date": ["2022-01-01", "2022-01-02"]}
        df = pd.DataFrame(data)
        dt = chart.DataTable(df, date_column="date")
        self.assertIsInstance(dt, chart.DataTable)
        self.assertEqual(dt.shape, (2, 3))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(dt["date"]))

    def test_transpose_df(self):
        """Test transpose_df function."""
        data = {"label": ["A", "B"], "val1": [1, 2], "val2": [3, 4]}
        df = pd.DataFrame(data)

        # Test basic transpose.
        transposed = chart.transpose_df(df, "label")
        self.assertEqual(transposed.shape, (2, 2))
        self.assertEqual(list(transposed.columns), ["A", "B"])
        self.assertEqual(list(transposed.index), ["val1", "val2"])
        self.assertEqual(transposed["A"]["val1"], 1)

        # Test with index_name.
        transposed_with_index_name = chart.transpose_df(
            df, "label", index_name="Metrics"
        )
        self.assertEqual(transposed_with_index_name.columns.name, "Metrics")

        # Test with custom indexes.
        transposed_with_indexes = chart.transpose_df(
            df, "label", indexes=["Value 1", "Value 2"]
        )
        self.assertEqual(list(transposed_with_indexes.index), ["Value 1", "Value 2"])

        # Test invalid label_col.
        with self.assertRaises(ValueError):
            chart.transpose_df(df, "invalid_col")

        # Test invalid indexes length.
        with self.assertRaises(ValueError):
            chart.transpose_df(df, "label", indexes=["Only one"])

    def test_pivot_df(self):
        """Test pivot_df function."""
        data = {
            "date": ["2022-01-01", "2022-01-01", "2022-01-02", "2022-01-02"],
            "variable": ["temp", "prec", "temp", "prec"],
            "value": [25, 5, 26, 3],
        }
        df = pd.DataFrame(data)

        pivoted = chart.pivot_df(df, index="date", columns="variable", values="value")

        self.assertEqual(pivoted.shape, (2, 3))
        self.assertEqual(list(pivoted.columns), ["date", "prec", "temp"])
        self.assertEqual(pivoted["temp"][0], 25)
        self.assertEqual(pivoted["prec"][1], 3)

    def test_array_to_df(self):
        """Test array_to_df function."""
        y_values = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        df = chart.array_to_df(y_values)
        self.assertEqual(df.shape, (3, 3))
        self.assertEqual(list(df.columns), ["x", "y1", "y2"])
        self.assertEqual(list(df["x"]), [1, 2, 3])
        self.assertEqual(list(df["y1"]), [1.0, 2.0, 3.0])
        self.assertEqual(list(df["y2"]), [4.0, 5.0, 6.0])

        x_values = [10, 20, 30]
        y_labels = ["a", "b"]
        df = chart.array_to_df(
            y_values, x_values=x_values, y_labels=y_labels, x_label="time"
        )
        self.assertEqual(df.shape, (3, 3))
        self.assertEqual(list(df.columns), ["time", "a", "b"])
        self.assertEqual(list(df["time"]), [10, 20, 30])
        self.assertEqual(list(df["a"]), [1.0, 2.0, 3.0])
        self.assertEqual(list(df["b"]), [4.0, 5.0, 6.0])

    @patch("geemap.chart.plt.show")
    @patch("geemap.chart.display")
    def test_chart_class(self, mock_display, mock_show):
        """Test the Chart class with different chart types."""
        data = {"x": ["1", "2", "3"], "y1": [4, 5, 6], "y2": [7, 8, 9]}

        for chart_type in [
            "LineChart",
            "ScatterChart",
            "ColumnChart",
            "BarChart",
            "PieChart",
            "AreaChart",
            "Table",
        ]:
            c = chart.Chart(
                data,
                chart_type=chart_type,
                x_cols="x",
                y_cols=["y1", "y2"],
                title=f"Test {chart_type}",
                x_label="X Axis",
                y_label="Y Axis",
            )
            self.assertIsInstance(c, chart.Chart)
            self.assertEqual(c.get_chart_type(), chart_type)
            self.assertEqual(c.title, f"Test {chart_type}")
            self.assertEqual(c.x_label, "X Axis")
            self.assertEqual(c.y_label, "Y Axis")

            c.display()
            self._ipython_display_ = getattr(c, "_ipython_display_", None)
            if self._ipython_display_:
                c._ipython_display_()

        # IntervalChart has a specific format.
        c = chart.Chart(
            {"x": [1, 2, 3], "y1": [4, 5, 6], "y2": [7, 8, 9]},
            chart_type="IntervalChart",
            x_cols=["x"],
            y_cols=["y1", "y2"],
        )
        self.assertEqual(c.get_chart_type(), "IntervalChart")

        # Test setting properties.
        c = chart.Chart(data, chart_type="LineChart", x_cols="x", y_cols=["y1"])
        c.set_options(title="New Title")
        self.assertEqual(c.figure.title, "New Title")

        dt = chart.DataTable({"x": [10], "y": [20]})
        c.set_data_table(dt)
        self.assertEqual(c.get_data_table().shape, (1, 2))

    @patch("geemap.chart.plt.Figure.save_png")
    def test_chart_save_png(self, mock_save_png):
        data = {"x": [1, 2], "y": [3, 4]}
        c = chart.Chart(data, chart_type="LineChart", x_cols="x", y_cols=["y"])
        c.save_png("test.png")
        mock_save_png.assert_called_once_with("test.png", scale=1.0)

    def test_base_chart_class(self):
        """Test BaseChartClass."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        base = chart.BaseChartClass(df, default_labels=["label1"], name="test_base")
        self.assertEqual(base.name, "test_base")
        self.assertEqual(base.labels, ["label1"])
        self.assertTrue(hasattr(base, "df"))
        self.assertEqual(repr(base), "test_base")
        base.get_data()
        base.plot_chart()

    @patch("geemap.chart.plt.show")
    def test_bar_chart(self, mock_show):
        """Test BarChart."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        bar = chart.BarChart(df, default_labels=["label1"], name="test_bar")
        bar.x_data = [1, 2]
        bar.y_data = [3, 4]
        bar.plot_chart()
        mock_show.assert_called()

        self.assertEqual(bar.get_ylim(), (3.0, 4.2))

        # Test specific naming for get_ylim
        bar.name = "feature.byFeature"
        self.assertEqual(bar.get_ylim(), (3.0, 4.2))

    @patch("geemap.chart.plt.show")
    def test_line_chart(self, mock_show):
        """Test LineChart."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        line = chart.LineChart(df, labels=["label1"], name="test_line")
        line.x_data = [1, 2]
        line.y_data = [3, 4]
        line.plot_chart()
        mock_show.assert_called()

    def test_feature_by_feature(self):
        """Test Feature_ByFeature."""
        df = pd.DataFrame({"x": [1, 2], "y1": [3, 4], "y2": [5, 6]})
        fb = chart.Feature_ByFeature(df, x_property="x", y_properties=["y1", "y2"])
        self.assertEqual(fb.x_data, [1, 2])
        self.assertEqual(len(fb.y_data), 2)

    def test_feature_by_property(self):
        """Test Feature_ByProperty."""
        df = pd.DataFrame({"x_prop": [1, 2], "y_prop": [3, 4], "series": ["A", "B"]})
        fb_list = chart.Feature_ByProperty(
            df, x_properties=["x_prop", "y_prop"], series_property="series"
        )
        self.assertEqual(fb_list.x_data, ["x_prop", "y_prop"])

        fb_dict = chart.Feature_ByProperty(
            df, x_properties={"x_prop": "X", "y_prop": "Y"}, series_property="series"
        )
        self.assertEqual(fb_dict.x_data, ["X", "Y"])

        with self.assertRaises(Exception):
            chart.Feature_ByProperty(df, x_properties="invalid", series_property="series")

        with self.assertRaises(Exception):
             chart.Feature_ByProperty(df, x_properties=["x"], series_property="s", labels=["1"])

    def test_feature_groups(self):
        """Test Feature_Groups."""
        df = pd.DataFrame(
            {"x": [1, 2, 3], "y": [10, 20, 30], "series": ["A", "A", "B"]}
        )
        fg = chart.Feature_Groups(df, x_property="x", y_property="y", series_property="series")
        self.assertEqual(fg.unique_series_values, ["A", "B"])
        self.assertEqual(len(fg.x_data), 3)
        self.assertEqual(len(fg.y_data), 2)

    @patch("geemap.chart.Feature_ByFeature.plot_chart")
    def test_feature_by_feature_func(self, mock_plot):
        """Test feature_by_feature function."""
        df = pd.DataFrame({"x": [1], "y1": [2]})
        chart.feature_by_feature(df, "x", ["y1"])
        mock_plot.assert_called_once()

    @patch("geemap.chart.Feature_ByProperty.plot_chart")
    def test_feature_by_property_func(self, mock_plot):
        """Test feature_by_property function."""
        df = pd.DataFrame({"x_prop": [1, 2], "y_prop": [3, 4], "series": ["A", "B"]})
        chart.feature_by_property(df, ["x_prop", "y_prop"], "series")
        mock_plot.assert_called_once()

    @patch("geemap.chart.Feature_Groups.plot_chart")
    def test_feature_groups_func(self, mock_plot):
        """Test feature_groups function."""
        df = pd.DataFrame(
            {"x": [1, 2, 3], "y": [10, 20, 30], "series": ["A", "A", "B"]}
        )
        chart.feature_groups(df, "x", "y", "series")
        mock_plot.assert_called_once()

    @patch("geemap.chart.array_to_df")
    @patch("geemap.chart.Chart")
    def test_array_values(self, mock_chart, mock_array_to_df):
        """Test array_values function."""
        mock_array_to_df.return_value = pd.DataFrame({"x": [1, 2], "y1": [3, 4]})
        chart.array_values([[1, 2], [3, 4]])
        mock_chart.assert_called_once()
        mock_array_to_df.assert_called_once()


if __name__ == "__main__":
    unittest.main()
