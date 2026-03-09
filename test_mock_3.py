import unittest
from unittest import mock
import subprocess

# Module A
def run_cmd():
    subprocess.run(["echo", "A"])

# Module B (Tests)
class TestMock(unittest.TestCase):
    @mock.patch("subprocess.run")
    def test_patch(self, mock_run):
        run_cmd()
        mock_run.assert_called()

if __name__ == "__main__":
    unittest.main()
