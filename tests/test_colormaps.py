"""Tests for `colormaps` module."""

import unittest
from geemap import colormaps


class ColormapsTest(unittest.TestCase):
    """Tests for `colormaps` module."""

    def test_get_palette_ndvi(self):
        """Test get_palette with ndvi."""
        palette = colormaps.get_palette("ndvi")
        self.assertEqual(len(palette), 17)
        self.assertEqual(palette[0], "FFFFFF")

    def test_get_palette_ndwi_hashtag(self):
        """Test get_palette with ndwi and hashtag."""
        palette = colormaps.get_palette("ndwi", hashtag=True)
        expect = [
            "#ece7f2",
            "#d0d1e6",
            "#a6bddb",
            "#74a9cf",
            "#3690c0",
            "#0570b0",
            "#045a8d",
            "#023858",
        ]
        self.assertEqual(expect, palette)

    def test_get_palette_dem(self):
        """Test get_palette with dem."""
        palette = colormaps.get_palette("dem")
        self.assertEqual(len(palette), 5)
        self.assertEqual(palette[0], "006633")

    def test_get_palette_dw(self):
        """Test get_palette with dw."""
        palette = colormaps.get_palette("dw")
        self.assertEqual(len(palette), 9)
        self.assertEqual(palette[0], "#419BDF")

    def test_get_palette_esri_lulc(self):
        """Test get_palette with esri_lulc."""
        palette = colormaps.get_palette("esri_lulc")
        self.assertEqual(len(palette), 11)
        self.assertEqual(palette[0], "#1A5BAB")

    def test_get_palette_viridis_nclass(self):
        """Test get_palette with viridis and n_class."""
        palette = colormaps.get_palette("viridis", n_class=5)
        self.assertEqual(len(palette), 5)
        self.assertEqual(palette[0], "440154")
        self.assertEqual(palette[4], "fde725")

    def test_get_palette_terrain_nclass_hashtag(self):
        """Test get_palette with terrain and n_class and hashtag."""
        palette = colormaps.get_palette("terrain", n_class=3, hashtag=True)
        self.assertEqual(len(palette), 3)
        self.assertEqual(palette[0], "#333399")
        self.assertEqual(palette[1], "#fefe98")
        self.assertEqual(palette[2], "#ffffff")

    def test_get_palette_no_nclass(self):
        """Test get_palette with no n_class."""
        palette = colormaps.get_palette("plasma")
        self.assertEqual(len(palette), 256)
        self.assertEqual(palette[0], "0d0887")
        self.assertEqual(palette[255], "f0f921")


    def test_get_colorbar(self):
        """Test get_colorbar."""
        from unittest.mock import patch
        import matplotlib.pyplot as plt

        colors = ["#ff0000", "#00ff00", "#0000ff"]

        # return_fig=True
        fig = colormaps.get_colorbar(colors, return_fig=True)
        self.assertIsNotNone(fig)

        # discrete=True, return_fig=True
        fig_discrete = colormaps.get_colorbar(colors, discrete=True, return_fig=True)
        self.assertIsNotNone(fig_discrete)

        # return_fig=False
        with patch.object(plt, "show") as mock_show:
            colormaps.get_colorbar(colors, return_fig=False)
            mock_show.assert_called_once()

    def test_list_colormaps(self):
        """Test list_colormaps."""
        cmaps = colormaps.list_colormaps()
        self.assertIn("viridis", cmaps)

        cmaps_extra = colormaps.list_colormaps(add_extra=True)
        self.assertIn("dem", cmaps_extra)
        self.assertIn("ndvi", cmaps_extra)

        cmaps_lower = colormaps.list_colormaps(lowercase=True)
        self.assertIn("viridis", cmaps_lower)

    def test_plot_colormap(self):
        """Test plot_colormap."""
        from unittest.mock import patch
        import matplotlib.pyplot as plt

        # return_fig=True, axis_off=True, show_name=True
        fig = colormaps.plot_colormap("viridis", axis_off=True, show_name=True, return_fig=True)
        self.assertIsNotNone(fig)

        # return_fig=True, axis_off=False, show_name=False
        fig = colormaps.plot_colormap("viridis", axis_off=False, show_name=False, return_fig=True)
        self.assertIsNotNone(fig)

        # return_fig=False
        with patch.object(plt, "show") as mock_show:
            colormaps.plot_colormap("viridis", return_fig=False)
            mock_show.assert_called_once()

    def test_plot_colormaps(self):
        """Test plot_colormaps."""
        from unittest.mock import patch
        import matplotlib.pyplot as plt

        with patch.object(colormaps, "list_colormaps") as mock_list, patch.object(plt, "show") as mock_show:
            mock_list.return_value = ["viridis", "plasma"]
            colormaps.plot_colormaps()
            mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
