import re

with open("tests/test_foliumap.py", "r") as f:
    content = f.read()

# Replace mocked map object patch object with with mock.patch.object(m, ...
def replace_patch_object(func_name, method_to_mock, calls_on_mock=None):
    global content
    pattern = r'@mock\.patch\.object\(foliumap\.Map, "([^"]+)"\)\s+def (test_[a-zA-Z0-9_]+)\(self,\s*([^,\)]+)(?:,\s*([^,\)]+))?(?:,\s*([^,\)]+))?\):'

    # We'll just do it manually with regexes
    pass

import sys
sys.exit(0)
