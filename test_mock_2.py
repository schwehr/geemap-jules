import unittest
from unittest import mock

# Module A
import subprocess
def run_cmd():
    subprocess.run(["echo", "A"])

# Module B (Tests)
class TestMock(unittest.TestCase):
    @mock.patch("test_mock_2.subprocess")
    def test_patch(self, mock_sub):
        run_cmd()
        mock_sub.run.assert_called()

if __name__ == "__main__":
    unittest.main()
