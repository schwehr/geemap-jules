"""Tests for the timelapse module."""
import os
import shutil
import sys
import unittest
from unittest import mock

# To allow mock testing when ffmpeg-python is not installed
sys.modules['ffmpeg'] = mock.MagicMock()

from geemap import timelapse

class TestTimelapse(unittest.TestCase):
    @mock.patch.object(os.path, "exists")
    @mock.patch.object(shutil, "which")
    @mock.patch.object(os, "system")
    @mock.patch.object(timelapse.Image, "open")
    def test_gif_to_mp4(self, mock_image_open, mock_system, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True

        mock_img = mock.MagicMock()
        mock_img.size = (100, 100)
        mock_image_open.return_value = mock_img

        timelapse.gif_to_mp4("in.gif", "out.mp4")
        mock_system.assert_called_once()
        self.assertIn("ffmpeg", mock_system.call_args[0][0])

    @mock.patch.object(os.path, "exists")
    @mock.patch.object(shutil, "which")
    @mock.patch.object(os, "system")
    def test_merge_gifs(self, mock_system, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True
        timelapse.merge_gifs(["in1.gif", "in2.gif"], "out.gif")
        mock_system.assert_called_once()
        self.assertIn("gifsicle", mock_system.call_args[0][0])

    @mock.patch.object(os.path, "exists")
    @mock.patch.object(shutil, "which")
    def test_reduce_gif_size(self, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True

        # the ffmpeg inside geemap.timelapse is locally imported and used inside the function
        import ffmpeg
        with mock.patch.object(ffmpeg, "input") as mock_input, \
             mock.patch.object(ffmpeg, "output") as mock_output, \
             mock.patch.object(ffmpeg, "run") as mock_run:

            timelapse.reduce_gif_size("in.gif", "out.gif")
            mock_run.assert_called_once()

    @mock.patch("geemap.timelapse.os.path.isdir")
    @mock.patch("geemap.timelapse.glob.glob")
    @mock.patch("geemap.timelapse.Image.open")
    @mock.patch("geemap.timelapse.is_tool")
    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.system")
    @mock.patch("geemap.timelapse.os.remove")
    def test_make_gif(self, mock_remove, mock_system, mock_exists, mock_is_tool, mock_image_open, mock_glob, mock_isdir):
        # Test directory input
        mock_isdir.return_value = True
        mock_glob.return_value = ["img1.jpg", "img2.jpg"]
        mock_img1 = mock.MagicMock()
        mock_img2 = mock.MagicMock()
        mock_image_open.side_effect = [mock_img1, mock_img2]

        timelapse.make_gif("in_dir", "out.gif", mp4=False, clean_up=False)
        mock_img1.save.assert_called_once()
        self.assertEqual(mock_img1.save.call_args[0][0], "out.gif")

        # Test list input and mp4 and cleanup
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
        mock_exists.side_effect = [True, False] # in_gif exists, out_dir doesn't

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
    def test_gif_fading(self, mock_getcwd, mock_rmtree, mock_system, mock_glob, mock_chdir, mock_gif_to_png, mock_makedirs, mock_exists):
        mock_getcwd.return_value = "/current/dir"
        mock_exists.return_value = True # For all exists checks (in_gif, temp_dir)
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
    def test_add_progress_bar_to_gif(self, mock_bytesio, mock_iterator, mock_draw, mock_open, mock_makedirs, mock_exists):
        mock_exists.side_effect = [True, False] # in_gif exists, out_dir doesn't
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
    def test_add_text_to_gif(self, mock_bytesio, mock_draw, mock_iterator, mock_open, mock_font, mock_makedirs, mock_exists):
        # We need exists to return True for in_gif, True for font, False for out_dir
        def exists_side_effect(path):
            if path == os.path.abspath("in.gif"): return True
            if "arial.ttf" in path: return True
            if path == os.path.dirname(os.path.abspath("out.gif")): return False
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

        timelapse.add_text_to_gif("in.gif", "out.gif", xy=("10%", "10%"), text_sequence=["A", "B"])


        mock_font.assert_called()
        self.assertEqual(mock_draw.call_count, 2)





    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.os.makedirs")
    @mock.patch("geemap.timelapse.Image.open")
    @mock.patch("geemap.timelapse.ImageSequence.Iterator")
    @mock.patch("geemap.timelapse.ImageDraw.Draw")
    @mock.patch("geemap.timelapse.io.BytesIO")
    @mock.patch("geemap.timelapse.has_transparency")
    def test_add_image_to_gif(self, mock_transparency, mock_bytesio, mock_draw, mock_iterator, mock_open, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        mock_transparency.return_value = False

        mock_gif = mock.MagicMock()
        mock_gif.n_frames = 2
        mock_gif.size = (100, 100)

        mock_logo = mock.MagicMock()
        mock_logo.size = (20, 20)

        # open is called twice: once for gif, once for logo
        mock_open.side_effect = [mock_gif, mock_logo, mock_logo, mock_logo]

        mock_frame1 = mock.MagicMock()
        mock_frame2 = mock.MagicMock()
        mock_iterator.return_value = [mock_frame1, mock_frame2]

        timelapse.add_image_to_gif("in.gif", "out.gif", "logo.png", xy=(10, 10), circle_mask=True)



        # Verify paste is called on each frame
        mock_frame1.convert().paste.assert_called_once()
        mock_frame2.convert().paste.assert_called_once()


if __name__ == '__main__':
    unittest.main()
