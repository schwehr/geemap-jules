import subprocess
import unittest
from unittest import mock

# Simulate geemap.timelapse
class FakeTimelapse:
    def gif_to_mp4(self):
        print(f"Inside gif_to_mp4, subprocess is {subprocess}")
        subprocess.run(["echo", "hello"])

timelapse = FakeTimelapse()

class TestMock(unittest.TestCase):
    @mock.patch("test_mock.subprocess")
    def test_patch_global(self, mock_sub):
        print(f"In test, mock_sub is {mock_sub}")
        timelapse.gif_to_mp4()
        mock_sub.run.assert_called()

if __name__ == "__main__":
    unittest.main()
