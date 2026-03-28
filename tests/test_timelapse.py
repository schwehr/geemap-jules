"""Tests for the timelapse module."""

import os
import shutil
import sys
import unittest
from unittest import mock

# To allow mock testing when ffmpeg-python is not installed.
sys.modules["ffmpeg"] = mock.MagicMock()

from geemap import timelapse
from geemap import coreutils
from tests import fake_ee
import ee


class TestTimelapse(unittest.TestCase):
    @mock.patch.object(os.path, "exists")
    @mock.patch.object(shutil, "which")
    @mock.patch.object(timelapse, "subprocess")
    @mock.patch.object(timelapse.Image, "open")
    def test_gif_to_mp4(self, mock_image_open, mock_subprocess, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True

        mock_img = mock.MagicMock()
        mock_img.size = (100, 100)
        mock_image_open.return_value = mock_img

        timelapse.gif_to_mp4("in.gif", "out.mp4")
        mock_subprocess.run.assert_called()
        self.assertIn("ffmpeg", mock_subprocess.run.call_args[0][0])

    @mock.patch.object(os.path, "exists")
    @mock.patch.object(shutil, "which")
    @mock.patch.object(timelapse, "subprocess")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_merge_gifs(self, mock_open, mock_subprocess, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True
        timelapse.merge_gifs(["in1.gif", "in2.gif"], "out.gif")
        mock_subprocess.run.assert_called_once()
        self.assertIn("gifsicle", mock_subprocess.run.call_args[0][0])

    @mock.patch.object(os.path, "exists")
    @mock.patch.object(shutil, "which")
    def test_reduce_gif_size(self, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True

        # the ffmpeg inside geemap.timelapse is locally imported and used inside the function.
        import ffmpeg

        with (
            mock.patch.object(ffmpeg, "input") as mock_input,
            mock.patch.object(ffmpeg, "output") as mock_output,
            mock.patch.object(ffmpeg, "run") as mock_run,
        ):

            timelapse.reduce_gif_size("in.gif", "out.gif")
            mock_run.assert_called_once()

    @mock.patch("geemap.timelapse.os.path.isdir")
    @mock.patch("geemap.timelapse.glob.glob")
    @mock.patch("geemap.timelapse.Image.open")
    @mock.patch("geemap.timelapse.is_tool")
    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.system")
    @mock.patch("geemap.timelapse.os.remove")
    def test_make_gif(
        self,
        mock_remove,
        mock_system,
        mock_exists,
        mock_is_tool,
        mock_image_open,
        mock_glob,
        mock_isdir,
    ):
        # Test directory input.
        mock_isdir.return_value = True
        mock_glob.return_value = ["img1.jpg", "img2.jpg"]
        mock_img1 = mock.MagicMock()
        mock_img2 = mock.MagicMock()
        mock_image_open.side_effect = [mock_img1, mock_img2]

        timelapse.make_gif("in_dir", "out.gif", mp4=False, clean_up=False)
        mock_img1.save.assert_called_once()
        self.assertEqual(mock_img1.save.call_args[0][0], "out.gif")

        # Test list input and mp4 and cleanup.
        mock_isdir.return_value = False
        mock_is_tool.return_value = True
        mock_exists.return_value = True
        mock_img1.reset_mock()
        mock_image_open.side_effect = [mock_img1, mock_img2]

        timelapse.make_gif(["img1.jpg", "img2.jpg"], "out.gif", mp4=True, clean_up=True)
        mock_img1.save.assert_called_once()
        mock_system.assert_called_once()
        self.assertIn("ffmpeg", mock_system.call_args[0][0])
        self.assertEqual(mock_remove.call_count, 2)

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.makedirs")
    @mock.patch("geemap.timelapse.os.system")
    def test_gif_to_png(self, mock_system, mock_makedirs, mock_exists):
        mock_exists.side_effect = [True, False]  # in_gif exists, out_dir doesn't

        timelapse.gif_to_png("in.gif", "out_dir", prefix="test_", verbose=False)
        mock_makedirs.assert_called_once_with("out_dir")
        mock_system.assert_called_once()
        self.assertIn("ffmpeg", mock_system.call_args[0][0])
        self.assertIn("test_%d.png", mock_system.call_args[0][0])

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.makedirs")
    @mock.patch("geemap.timelapse.gif_to_png")
    @mock.patch("geemap.timelapse.os.chdir")
    @mock.patch("geemap.timelapse.glob.glob")
    @mock.patch("geemap.timelapse.os.system")
    @mock.patch("geemap.timelapse.shutil.rmtree")
    @mock.patch("geemap.timelapse.os.getcwd")
    def test_gif_fading(
        self,
        mock_getcwd,
        mock_rmtree,
        mock_system,
        mock_glob,
        mock_chdir,
        mock_gif_to_png,
        mock_makedirs,
        mock_exists,
    ):
        mock_getcwd.return_value = "/current/dir"
        mock_exists.return_value = True  # For all exists checks (in_gif, temp_dir)
        mock_glob.return_value = ["1.png", "2.png"]

        timelapse.gif_fading("in.gif", "out.gif", duration=2.0, verbose=False)
        mock_gif_to_png.assert_called_once()
        mock_system.assert_called_once()
        self.assertIn("ffmpeg", mock_system.call_args[0][0])
        self.assertIn("-loop 1 -t 2.0 -i 1.png", mock_system.call_args[0][0])
        self.assertEqual(mock_rmtree.call_count, 2)

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.makedirs")
    @mock.patch("geemap.timelapse.Image.open")
    @mock.patch("geemap.timelapse.ImageDraw.Draw")
    @mock.patch("geemap.timelapse.ImageSequence.Iterator")
    @mock.patch("geemap.timelapse.io.BytesIO")
    def test_add_progress_bar_to_gif(
        self,
        mock_bytesio,
        mock_iterator,
        mock_draw,
        mock_open,
        mock_makedirs,
        mock_exists,
    ):
        mock_exists.side_effect = [True, False]  # in_gif exists, out_dir doesn't
        mock_img = mock.MagicMock()
        mock_img.n_frames = 2
        mock_img.size = (100, 100)
        mock_open.return_value = mock_img

        mock_frame1 = mock.MagicMock()
        mock_frame2 = mock.MagicMock()
        mock_iterator.return_value = [mock_frame1, mock_frame2]

        mock_bytes = mock.MagicMock()
        mock_bytesio.return_value = mock_bytes

        timelapse.add_progress_bar_to_gif("in.gif", "out.gif")

        mock_open.assert_called()
        self.assertEqual(mock_draw.call_count, 2)

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.makedirs")
    @mock.patch("geemap.timelapse.ImageFont.truetype")
    @mock.patch("geemap.timelapse.Image.open")
    @mock.patch("geemap.timelapse.ImageSequence.Iterator")
    @mock.patch("geemap.timelapse.ImageDraw.Draw")
    @mock.patch("geemap.timelapse.io.BytesIO")
    def test_add_text_to_gif(
        self,
        mock_bytesio,
        mock_draw,
        mock_iterator,
        mock_open,
        mock_font,
        mock_makedirs,
        mock_exists,
    ):
        # We need exists to return True for in_gif, True for font, False for out_dir.
        def exists_side_effect(path):
            if path == os.path.abspath("in.gif"):
                return True
            if "arial.ttf" in path:
                return True
            if path == os.path.dirname(os.path.abspath("out.gif")):
                return False
            return True

        mock_exists.side_effect = exists_side_effect

        mock_img = mock.MagicMock()
        mock_img.n_frames = 2
        mock_img.size = (100, 100)
        mock_open.return_value = mock_img

        mock_frame1 = mock.MagicMock()
        mock_frame2 = mock.MagicMock()
        mock_iterator.return_value = [mock_frame1, mock_frame2]

        mock_bytes = mock.MagicMock()
        mock_bytesio.return_value = mock_bytes

        timelapse.add_text_to_gif(
            "in.gif", "out.gif", xy=("10%", "10%"), text_sequence=["A", "B"]
        )

        mock_font.assert_called()
        self.assertEqual(mock_draw.call_count, 2)

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.makedirs")
    @mock.patch("geemap.timelapse.Image.open")
    @mock.patch("geemap.timelapse.ImageSequence.Iterator")
    @mock.patch("geemap.timelapse.ImageDraw.Draw")
    @mock.patch("geemap.timelapse.io.BytesIO")
    @mock.patch("geemap.timelapse.has_transparency")
    def test_add_image_to_gif(
        self,
        mock_transparency,
        mock_bytesio,
        mock_draw,
        mock_iterator,
        mock_open,
        mock_makedirs,
        mock_exists,
    ):
        mock_exists.return_value = True
        mock_transparency.return_value = False

        mock_gif = mock.MagicMock()
        mock_gif.n_frames = 2
        mock_gif.size = (100, 100)

        mock_logo = mock.MagicMock()
        mock_logo.size = (20, 20)

        # open is called twice: once for gif, once for logo.
        mock_open.side_effect = [mock_gif, mock_logo, mock_logo, mock_logo]

        mock_frame1 = mock.MagicMock()
        mock_frame2 = mock.MagicMock()
        mock_iterator.return_value = [mock_frame1, mock_frame2]

        timelapse.add_image_to_gif(
            "in.gif", "out.gif", "logo.png", xy=(10, 10), circle_mask=True
        )

        # Verify paste is called on each frame.
        mock_frame1.convert().paste.assert_called_once()
        mock_frame2.convert().paste.assert_called_once()

    @mock.patch.object(coreutils, "ee_initialize")
    def test_add_overlay(self, mock_ee_initialize):
        # We need to mock ee.ImageCollection etc because geemap.timelapse directly checks isinstance(collection, ee.ImageCollection).
        with mock.patch("geemap.timelapse.ee") as mock_ee:
            # Must mock coreutils.geojson_to_ee if it's called.
            with mock.patch("geemap.coreutils.geojson_to_ee") as mock_geojson_to_ee:
                mock_geojson_to_ee.return_value = fake_ee.FeatureCollection(
                    [fake_ee.Feature(fake_ee.Geometry.Point([0, 0]))]
                )

                # Setup fake collection.
                fake_img = mock.MagicMock()
                fake_col = mock.MagicMock(spec=fake_ee.ImageCollection)
                mock_ee.ImageCollection = fake_ee.ImageCollection
                mock_ee.FeatureCollection = fake_ee.FeatureCollection
                mock_ee.Feature = fake_ee.Feature
                mock_ee.Geometry = fake_ee.Geometry
                mock_ee.Image = fake_ee.Image
                mock_ee.ErrorMargin = mock.MagicMock()

                fake_col = fake_ee.ImageCollection([fake_img])

                # Bad collection type.
                with self.assertRaises(Exception):
                    timelapse.add_overlay(fake_img, "countries")

                # Mock inner methods used in the try block.
                mock_img_class = mock.MagicMock()
                mock_ee.Image = mock_img_class
                mock_byte = mock_img_class.return_value.byte.return_value
                mock_proj = mock_byte.setDefaultProjection.return_value
                mock_paint = mock_proj.paint.return_value
                mock_vis = mock_paint.visualize.return_value
                mock_vis.setDefaultProjection.return_value = mock.MagicMock()

                # We need to ensure fake_col.map works and fake_col.first().projection() works.
                # Add mock methods to fake_col.
                fake_col.first = mock.MagicMock()
                fake_col.first.return_value.projection.return_value = "mock_proj"
                fake_col.map = mock.MagicMock(return_value=fake_col)

                with mock.patch("geemap.coreutils.check_color") as mock_check_color:
                    mock_check_color.return_value = "000000"

                    # String overlay_data - public assets.
                    res_col = timelapse.add_overlay(fake_col, "countries")
                    self.assertEqual(res_col, fake_col)

                    # String overlay_data - http URL.
                    res_col2 = timelapse.add_overlay(
                        fake_col, "http://example.com/test.geojson"
                    )
                    self.assertEqual(res_col2, fake_col)
                    mock_geojson_to_ee.assert_called_once_with(
                        "http://example.com/test.geojson"
                    )

                    # String overlay_data - normal asset path.
                    res_col3 = timelapse.add_overlay(fake_col, "users/test/asset")
                    self.assertEqual(res_col3, fake_col)

                    # FeatureCollection.
                    fake_fc = fake_ee.FeatureCollection(
                        [fake_ee.Feature(fake_ee.Geometry.Point([0, 0]))]
                    )
                    res_col4 = timelapse.add_overlay(fake_col, fake_fc)
                    self.assertEqual(res_col4, fake_col)

                    # Feature.
                    fake_f = fake_ee.Feature(fake_ee.Geometry.Point([0, 0]))
                    res_col5 = timelapse.add_overlay(fake_col, fake_f)
                    self.assertEqual(res_col5, fake_col)

                    # Geometry.
                    fake_geom = fake_ee.Geometry.Point([0, 0])
                    res_col6 = timelapse.add_overlay(fake_col, fake_geom)
                    self.assertEqual(res_col6, fake_col)

                    # We need to mock FeatureCollection methods.
                    fake_fc.filterBounds = mock.MagicMock(return_value=fake_fc)
                    fake_fc.map = mock.MagicMock(return_value=fake_fc)

                    # With region.
                    res_col7 = timelapse.add_overlay(
                        fake_col, fake_fc, region=fake_geom
                    )
                    self.assertEqual(res_col7, fake_col)

                    # With region as FeatureCollection.
                    res_col8 = timelapse.add_overlay(fake_col, fake_fc, region=fake_fc)
                    self.assertEqual(res_col8, fake_col)

    from geemap import coreutils

    @mock.patch.object(coreutils, "ee_initialize")
    def test_valid_roi(self, mock_ee_initialize):
        with mock.patch("geemap.timelapse.ee") as mock_ee:
            mock_ee.Geometry = fake_ee.Geometry
            mock_ee.FeatureCollection = fake_ee.FeatureCollection
            mock_ee.Feature = fake_ee.Feature

            with (
                mock.patch("geemap.timelapse.ee_to_geojson") as mock_ee_to_geojson,
                mock.patch(
                    "geemap.timelapse.adjust_longitude"
                ) as mock_adjust_longitude,
            ):

                mock_ee_to_geojson.return_value = {
                    "type": "Point",
                    "coordinates": [0, 0],
                }
                mock_adjust_longitude.return_value = {
                    "type": "Point",
                    "coordinates": [0, 0],
                }

                # Geometry format.
                roi3 = fake_ee.Geometry.Point([0, 0])
                res3 = timelapse.valid_roi(roi3)
                self.assertIsInstance(res3, fake_ee.Geometry)

                # Feature format.
                roi4 = mock.MagicMock()
                roi4.geometry.return_value = roi3
                res4 = timelapse.valid_roi(roi4)
                self.assertIsInstance(res4, fake_ee.Geometry)

                # FeatureCollection format.
                roi5 = mock.MagicMock()
                roi5.geometry.return_value = roi3
                res5 = timelapse.valid_roi(roi5)
                self.assertIsInstance(res5, fake_ee.Geometry)

                # Invalid format.
                res6 = timelapse.valid_roi("invalid")
                self.assertIsNone(res6)

    @mock.patch.object(ee.Geometry, "Polygon")
    def test_sentinel1_defaults(self, mock_polygon):
        mock_polygon.return_value = fake_ee.Geometry.Polygon([[0, 0]])
        year, roi = timelapse.sentinel1_defaults()
        self.assertIsInstance(year, int)
        self.assertEqual(roi, mock_polygon.return_value)

    def test_get_default_index_vis_params(self):
        vis_params = timelapse.get_default_index_vis_params()
        self.assertIsInstance(vis_params, dict)
        self.assertIn("NDVI", vis_params)
        self.assertIn("palette", vis_params["NDVI"])

    def test_get_index_chart_labels(self):
        labels = timelapse.get_index_chart_labels()
        self.assertIsInstance(labels, dict)
        self.assertIn("NDVI", labels)

    def test_get_default_landsat_index_vis_params(self):
        vis_params = timelapse.get_default_landsat_index_vis_params()
        self.assertIsInstance(vis_params, dict)
        self.assertIn("NDVI", vis_params)
        self.assertIn("palette", vis_params["NDVI"])

    def test_get_default_landsat_band_labels(self):
        labels = timelapse.get_default_landsat_band_labels()
        self.assertIsInstance(labels, dict)
        self.assertIn("Blue", labels)
        self.assertEqual(labels["Blue"], "Blue")

    def test_get_landsat_index_chart_labels(self):
        labels = timelapse.get_landsat_index_chart_labels()
        self.assertIsInstance(labels, dict)
        self.assertIn("NDVI", labels)

    def test_draw_cross_marker(self):
        mock_draw = mock.MagicMock()
        timelapse.draw_cross_marker(mock_draw, 10, 10, 5, "red")
        self.assertEqual(mock_draw.line.call_count, 4)

    def test_draw_circle_marker(self):
        mock_draw = mock.MagicMock()
        timelapse.draw_circle_marker(mock_draw, 10, 10, 5, "blue")
        self.assertEqual(mock_draw.ellipse.call_count, 2)

    def test_draw_square_marker(self):
        mock_draw = mock.MagicMock()
        timelapse.draw_square_marker(mock_draw, 10, 10, 5, "green")
        self.assertEqual(mock_draw.rectangle.call_count, 2)

    def test_get_pixel_coordinates_from_geo(self):
        roi_bounds = [0, 0, 100, 100]  # [min_lon, min_lat, max_lon, max_lat]
        gif_width = 1000
        gif_height = 1000

        # Test center.
        x, y = timelapse.get_pixel_coordinates_from_geo(
            50, 50, roi_bounds, gif_width, gif_height
        )
        self.assertEqual(x, 500)
        self.assertEqual(y, 500)

        # Test boundaries.
        x, y = timelapse.get_pixel_coordinates_from_geo(
            0, 100, roi_bounds, gif_width, gif_height
        )
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

        # Test out of bounds (should be clamped).
        x, y = timelapse.get_pixel_coordinates_from_geo(
            -10, 110, roi_bounds, gif_width, gif_height
        )
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

        x, y = timelapse.get_pixel_coordinates_from_geo(
            110, -10, roi_bounds, gif_width, gif_height
        )
        self.assertEqual(x, 999)
        self.assertEqual(y, 999)


if __name__ == "__main__":
    unittest.main()
