import unittest
from unittest import mock
import pandas as pd
import plotly.graph_objs as go

from geemap import plot
from geemap import coreutils
from geemap import common


class TestPlot(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame(
            {
                "category": ["A", "B", "C", "D"],
                "value": [10, 20, 15, 30],
                "extra": [1, 2, 3, 4],
            }
        )

    def test_bar_chart_dataframe(self):
        fig = plot.bar_chart(
            data=self.df.copy(),
            x="category",
            y="value",
            color="category",
            descending=True,
            x_label="Category",
            y_label="Value",
            title="Bar Chart",
            legend_title="Legend",
            layout_args={"title": "Custom Title"},
            max_rows=2,
        )
        self.assertIsInstance(fig, go.Figure)

    def test_bar_chart_y_list(self):
        fig = plot.bar_chart(
            data=self.df.copy(),
            x="category",
            y=["value", "extra"],
            descending=True,
            y_label="Multiple Values",
        )
        self.assertIsInstance(fig, go.Figure)

    def test_bar_chart_invalid_data(self):
        with self.assertRaises(ValueError):
            plot.bar_chart(data=123)

    @mock.patch.object(coreutils, "github_raw_url")
    @mock.patch.object(common, "get_direct_url")
    @mock.patch.object(pd, "read_csv")
    def test_bar_chart_url(
        self, mock_read_csv, mock_get_direct_url, mock_github_raw_url
    ):
        mock_github_raw_url.return_value = "https://example.com/data.csv"
        mock_get_direct_url.return_value = "https://example.com/data.csv"
        mock_read_csv.return_value = self.df.copy()

        fig = plot.bar_chart(
            data="https://example.com/data.csv",
            x="category",
            y="value",
        )
        self.assertIsInstance(fig, go.Figure)
        mock_github_raw_url.assert_called_once_with("https://example.com/data.csv")
        mock_get_direct_url.assert_called_once_with("https://example.com/data.csv")
        mock_read_csv.assert_called_once_with("https://example.com/data.csv")

    def test_line_chart_dataframe(self):
        fig = plot.line_chart(
            data=self.df.copy(),
            x="category",
            y="value",
            color="category",
            descending=True,
            x_label="Category",
            y_label="Value",
            title="Line Chart",
            legend_title="Legend",
            max_rows=3,
            layout_args={"title": "Custom Line Title"},
        )
        self.assertIsInstance(fig, go.Figure)

    def test_line_chart_invalid_data(self):
        with self.assertRaises(ValueError):
            plot.line_chart(data=None)

    @mock.patch.object(pd, "read_csv")
    def test_line_chart_local_csv(self, mock_read_csv):
        mock_read_csv.return_value = self.df.copy()
        fig = plot.line_chart(data="local_data.csv", x="category", y="value")
        self.assertIsInstance(fig, go.Figure)
        mock_read_csv.assert_called_once_with("local_data.csv")

    def test_histogram_dataframe(self):
        fig = plot.histogram(
            data=self.df.copy(),
            x="value",
            y="extra",
            color="category",
            descending=True,
            x_label="Value",
            y_label="Extra",
            title="Histogram",
            max_rows=2,
            layout_args={"title": "Custom Histogram Title"},
        )
        self.assertIsInstance(fig, go.Figure)

    def test_histogram_invalid_data(self):
        with self.assertRaises(ValueError):
            plot.histogram(data=12.34)

    def test_pie_chart_dataframe(self):
        fig = plot.pie_chart(
            data=self.df.copy(),
            names="category",
            values="value",
            descending=True,
            title="Pie Chart",
            legend_title="Legend",
            layout_args={"title": "Custom Pie Title"},
        )
        self.assertIsInstance(fig, go.Figure)

    def test_pie_chart_invalid_data(self):
        with self.assertRaises(ValueError):
            plot.pie_chart(data=[1, 2, 3])

    def test_pie_chart_max_rows(self):
        df_large = pd.DataFrame(
            {"category": ["A", "B", "C", "D", "E"], "value": [50, 40, 30, 20, 10]}
        )
        fig = plot.pie_chart(
            data=df_large,
            names="category",
            values="value",
            max_rows=3,
            other_label="Other Category",
        )
        self.assertIsInstance(fig, go.Figure)


if __name__ == "__main__":
    unittest.main()
