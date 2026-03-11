with open("tests/test_timelapse.py", "r") as f:
    content = f.read()

new_content = content.replace(
    '            if path == os.path.abspath("in.gif"): return True\n            if "arial.ttf" in path: return True\n            if path == os.path.dirname(os.path.abspath("out.gif")): return False',
    '            if path == os.path.abspath("in.gif"):\n                return True\n            if "arial.ttf" in path:\n                return True\n            if path == os.path.dirname(os.path.abspath("out.gif")):\n                return False',
)

with open("tests/test_timelapse.py", "w") as f:
    f.write(new_content)
