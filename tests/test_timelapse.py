"""Tests for the timelapse module."""
import unittest
from unittest import mock
import sys

# To allow mock testing when ffmpeg-python is not installed
sys.modules['ffmpeg'] = mock.MagicMock()

from geemap import timelapse

class TestTimelapse(unittest.TestCase):
    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.shutil.which")
    @mock.patch("geemap.timelapse.os.system")
    @mock.patch("geemap.timelapse.Image.open")
    def test_gif_to_mp4(self, mock_image_open, mock_system, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True

        mock_img = mock.MagicMock()
        mock_img.size = (100, 100)
        mock_image_open.return_value = mock_img

        timelapse.gif_to_mp4("in.gif", "out.mp4")
        mock_system.assert_called_once()
        self.assertIn("ffmpeg", mock_system.call_args[0][0])

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.shutil.which")
    @mock.patch("geemap.timelapse.os.system")
    def test_merge_gifs(self, mock_system, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True
        timelapse.merge_gifs(["in1.gif", "in2.gif"], "out.gif")
        mock_system.assert_called_once()
        self.assertIn("gifsicle", mock_system.call_args[0][0])

    @mock.patch("geemap.timelapse.os.path.exists")
    @mock.patch("geemap.timelapse.shutil.which")
    def test_reduce_gif_size(self, mock_which, mock_exists):
        mock_exists.return_value = True
        mock_which.return_value = True

        # the ffmpeg inside geemap.timelapse is locally imported and used inside the function
        with mock.patch("ffmpeg.input") as mock_input, \
             mock.patch("ffmpeg.output") as mock_output, \
             mock.patch("ffmpeg.run") as mock_run:

            timelapse.reduce_gif_size("in.gif", "out.gif")
            mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
