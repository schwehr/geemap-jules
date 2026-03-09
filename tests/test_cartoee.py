import pathlib
import tempfile
import unittest
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np

from geemap import cartoee
from tests import fake_ee

try:
    import cartopy.crs as ccrs

    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False


@unittest.skipIf(not CARTOPY_AVAILABLE, "cartopy is not installed")
class TestCartoee(unittest.TestCase):

    def test_build_palette(self):
        palette = cartoee.build_palette("viridis", 5)
        self.assertEqual(len(palette), 5)
        self.assertEqual(palette[0], "#440154")
        self.assertEqual(palette[-1], "#fde725")

    def test_add_colorbar(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

        # basic right
        vis_params = {"min": 0, "max": 10, "palette": ["#440154", "#fde725"]}
        cartoee.add_colorbar(ax, vis_params, loc="right")
        self.assertEqual(len(fig.axes), 2)

        # with cax
        cax = fig.add_axes([0.1, 0.1, 0.8, 0.05])
        cartoee.add_colorbar(ax, vis_params, cax=cax)
        self.assertEqual(len(fig.axes), 3)

        # loc left, bottom, top
        cartoee.add_colorbar(ax, vis_params, loc="left", label="Left Label", tick_font_size=10)
        self.assertEqual(len(fig.axes), 4)
        cartoee.add_colorbar(ax, vis_params, loc="bottom", discrete=True)
        self.assertEqual(len(fig.axes), 5)
        cartoee.add_colorbar(ax, vis_params, loc="top", cmap="viridis")
        self.assertEqual(len(fig.axes), 6)

        # invalid ax
        with self.assertRaises(ValueError):
            cartoee.add_colorbar("not an ax", vis_params, loc="right")

        # invalid loc
        with self.assertRaises(ValueError):
            cartoee.add_colorbar(ax, vis_params, loc="invalid")

        # missing loc or cax
        with self.assertRaises(ValueError):
            cartoee.add_colorbar(ax, vis_params)

        # min not scalar
        with self.assertRaises(ValueError):
            cartoee.add_colorbar(ax, {"min": "not scalar"}, loc="right")

        # max not scalar
        with self.assertRaises(ValueError):
            cartoee.add_colorbar(ax, {"max": "not scalar"}, loc="right")

        # opacity not scalar
        with self.assertRaises(ValueError):
            cartoee.add_colorbar(ax, {"opacity": "not scalar"}, loc="right")

        # no cmap or palette
        with self.assertRaises(ValueError):
            cartoee.add_colorbar(ax, {"min": 0, "max": 10}, loc="right", cmap=None)


    def test_buffer_box(self):
        bbox = [1.1, 2.9, 3.1, 4.9]
        interval = 1
        # pylint: disable-next: protected-access
        self.assertEqual(cartoee._buffer_box(bbox, interval), (1.0, 3.0, 3.0, 5.0))
        bbox = [1.0, 3.0, 3.0, 5.0]
        # pylint: disable-next: protected-access
        self.assertEqual(cartoee._buffer_box(bbox, interval), (1.0, 3.0, 3.0, 5.0))

    def test_bbox_to_extent(self):
        self.assertEqual(cartoee.bbox_to_extent([1, 2, 3, 4]), (1, 3, 2, 4))

    def test_add_gridlines(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        ax.set_extent([-180, 180, -90, 90])

        # Test with interval float
        cartoee.add_gridlines(ax, interval=60)
        self.assertEqual(len(ax.get_xticks()), 7)

        # Test with interval list
        cartoee.add_gridlines(ax, interval=[60, 30])
        self.assertEqual(len(ax.get_xticks()), 7)

        # Test with n_ticks
        cartoee.add_gridlines(ax, n_ticks=5)
        self.assertEqual(len(ax.get_xticks()), 5)
        cartoee.add_gridlines(ax, n_ticks=[5, 5])
        self.assertEqual(len(ax.get_xticks()), 5)

        # Test with xs and ys
        cartoee.add_gridlines(ax, xs=np.array([-100, 0, 100]), ys=np.array([-50, 0, 50]))
        self.assertEqual(len(ax.get_xticks()), 3)

        # missing arguments
        with self.assertRaises(ValueError):
            cartoee.add_gridlines(ax, interval=None, xs=None, n_ticks=None, ys=[-50, 0, 50])
        with self.assertRaises(ValueError):
            cartoee.add_gridlines(ax, interval=None, xs=[-100, 0, 100], n_ticks=None, ys=None)

    def test_pad_view(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        ax.set_extent([-10, 10, -10, 10], crs=ccrs.PlateCarree())

        # factor float
        cartoee.pad_view(ax, factor=0.1)
        result = ax.get_xlim()
        self.assertAlmostEqual(result[0], -12.0)
        self.assertAlmostEqual(result[1], 12.0)
        result = ax.get_ylim()
        self.assertAlmostEqual(result[0], -12.0)
        self.assertAlmostEqual(result[1], 12.0)

        # factor list
        cartoee.pad_view(ax, factor=[0.2, 0.3])
        result = ax.get_xlim()
        self.assertAlmostEqual(result[0], -16.8)
        self.assertAlmostEqual(result[1], 16.8)

    def test_add_scale_bar(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        ax.set_extent([-10, 10, -10, 10], crs=ccrs.PlateCarree())

        # normal scale bar
        cartoee.add_scale_bar(ax, 10)
        self.assertTrue(len(ax.patches) > 0)

    def test_add_scale_bar_lite(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        ax.set_extent([-10, 10, -10, 10], crs=ccrs.PlateCarree())

        # normal lite scale bar
        cartoee.add_scale_bar_lite(ax)
        self.assertTrue(len(ax.texts) > 0)

        # with length
        cartoee.add_scale_bar_lite(ax, length=50)
        self.assertTrue(len(ax.texts) > 1)

        # invalid unit
        cartoee.add_scale_bar_lite(ax, unit="invalid")

    def test_add_north_arrow(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        cartoee.add_north_arrow(ax)
        self.assertEqual(len(ax.texts), 1)

    def test_create_legend(self):
        with self.assertRaises(ValueError):
            cartoee.create_legend()

        # the function create_legend currently just returns None
        cartoee.create_legend(linewidth=2)

    def test_add_legend(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

        # Test with default elements
        cartoee.add_legend(ax, title="Test Legend")
        self.assertIsNotNone(ax.get_legend())

        # Test with title_fontize and title_fontproperties (should raise error)
        with self.assertRaises(ValueError):
            cartoee.add_legend(ax, title="Test", title_fontize=10, title_fontproperties={})

        # Test font_color
        cartoee.add_legend(ax, font_color="blue", font_family="Arial")
        self.assertIsNotNone(ax.get_legend())

        # Test title_fontproperties
        cartoee.add_legend(ax, title="Test", title_fontize=None, title_fontproperties={"weight": "bold"})

    @mock.patch("geemap.cartoee.plt.savefig")
    @mock.patch("geemap.cartoee.common.png_to_gif")
    @mock.patch("geemap.cartoee.get_map")
    @mock.patch("geemap.cartoee.add_layer")
    @mock.patch("geemap.cartoee.ee", fake_ee)
    def test_get_image_collection_gif(self, mock_add_layer, mock_get_map, mock_png_to_gif, mock_savefig):
        ic = fake_ee.ImageCollection([fake_ee.Image()])

        # mock ax
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        mock_get_map.return_value = ax

        # Mock Date function inside get_image_collection_gif
        with tempfile.TemporaryDirectory() as tmpdir:
            out_gif = "test.gif"

            # Simple run
            with mock.patch.object(fake_ee, "Date", return_value=mock.Mock(format=lambda x: mock.Mock(getInfo=lambda: "2020-01-01")), create=True):
                cartoee.get_image_collection_gif(
                    ic, tmpdir, out_gif, vis_params={}, region=[-10, -10, 10, 10],
                    plot_title="Title"
                )
            mock_png_to_gif.assert_called_once()

            # Run with mp4 and overlays
            with mock.patch.object(fake_ee, "Date", return_value=mock.Mock(format=lambda x: mock.Mock(getInfo=lambda: "2020-01-01")), create=True):
                with mock.patch.dict("sys.modules", {"cv2": mock.MagicMock()}):
                    import cv2
                    cv2.imread.return_value = np.zeros((10, 10, 3), dtype=np.uint8)
                    mock_video_writer = mock.Mock()
                    cv2.VideoWriter.return_value = mock_video_writer

                    cartoee.get_image_collection_gif(
                        ic, tmpdir, "test2.gif", vis_params={"min": 0, "max": 10}, region=[-10, -10, 10, 10],
                        mp4=True, overlay_layers=[fake_ee.FeatureCollection()], overlay_styles=[{}],
                        grid_interval=10, colorbar_dict={"loc": "bottom", "cmap": "viridis"},
                        north_arrow_dict={"text": "N"}, scale_bar_dict={"length": 10}
                    )
                    mock_video_writer.release.assert_called_once()

                # Test mismatch length of overlay layers and styles
                with self.assertRaises(ValueError):
                    cartoee.get_image_collection_gif(
                        ic, tmpdir, "test3.gif", vis_params={}, region=[-10, -10, 10, 10],
                        overlay_layers=[fake_ee.FeatureCollection()], overlay_styles=[]
                    )

                # Test invalid overlay type
                with self.assertRaises(ValueError):
                    cartoee.get_image_collection_gif(
                        ic, tmpdir, "test4.gif", vis_params={}, region=[-10, -10, 10, 10],
                        overlay_layers=["invalid object"], overlay_styles=[{}]
                    )


    def test_convert_si(self):
        self.assertEqual(cartoee.convert_SI(1, "km", "m"), 1000.0)

    def test_savefig(self):
        fig = plt.figure()
        fig.add_subplot(111, projection=ccrs.PlateCarree())
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = pathlib.Path(tmpdir) / "test.png"
            cartoee.savefig(fig, str(outfile))
            self.assertTrue(outfile.exists())

    @mock.patch("geemap.cartoee.ee", fake_ee)
    @mock.patch("geemap.cartoee.add_layer")
    def test_get_map(self, mock_add_layer):
        # test image
        img = fake_ee.Image()
        ax = cartoee.get_map(img, region=[-180, -90, 180, 90])
        self.assertIsNotNone(ax)
        mock_add_layer.assert_called_once()

        # test feature collection
        fc = fake_ee.FeatureCollection()
        ax = cartoee.get_map(fc)
        self.assertIsNotNone(ax)

        # test image collection
        ic = fake_ee.ImageCollection([fake_ee.Image()])
        ax = cartoee.get_map(ic)
        self.assertIsNotNone(ax)

        # test basemap
        # Just pass the custom custom_tiles to get_map's internal mock somehow,
        # or we can mock out basemaps directly.
        with mock.patch("geemap.cartoee.basemaps") as mock_basemaps:
            mock_basemaps.custom_tiles = {"xyz": {"ROADMAP": {"url": "http://mock"}}}
            ax = cartoee.get_map(img, basemap="ROADMAP")
            self.assertIsNotNone(ax)

    @mock.patch("geemap.cartoee.ee", fake_ee)
    @mock.patch("requests.get")
    def test_add_layer(self, mock_get):
        # mock requests
        mock_response = mock.Mock()
        mock_response.status_code = 200
        # create a dummy image (2x2 with 3 channels)
        from PIL import Image
        import io
        img_arr = np.zeros((2, 2, 3), dtype=np.uint8)
        img = Image.fromarray(img_arr)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        mock_response.content = img_bytes.getvalue()
        mock_get.return_value = mock_response

        fig = plt.figure()
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

        ee_img = fake_ee.Image()

        # Test basic add_layer
        cartoee.add_layer(ax, ee_img)
        self.assertTrue(mock_get.called)
        self.assertTrue(len(ax.images) > 0)

        # Test with region
        cartoee.add_layer(ax, ee_img, region=[-10, -10, 10, 10])
        self.assertTrue(len(ax.images) > 1)

        # Test with feature collection
        fc = fake_ee.FeatureCollection()
        cartoee.add_layer(ax, fc)
        self.assertTrue(len(ax.images) > 2)

        # Test with vis params
        cartoee.add_layer(ax, ee_img, vis_params={"min": 0, "max": 100})
        self.assertTrue(len(ax.images) > 3)

        # Test exceptions
        with self.assertRaises(ValueError):
            cartoee.add_layer(ax, ee_img, dims="invalid")

        with self.assertRaises(ValueError):
            cartoee.add_layer("not an ax", ee_img)

        with self.assertRaises(ValueError):
            cartoee.add_layer(ax, "not an ee object")


if __name__ == "__main__":
    unittest.main()
