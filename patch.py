with open('tests/test_timelapse.py', 'r') as f:
    content = f.read()

content = content.replace(
    "@mock.patch('geemap.coreutils.ee_initialize')",
    "from geemap import coreutils\n    @mock.patch.object(coreutils, 'ee_initialize')"
)

content = content.replace(
    "# We need to mock ee.ImageCollection etc because geemap.timelapse directly checks isinstance(collection, ee.ImageCollection)",
    "# We need to mock ee.ImageCollection etc because geemap.timelapse directly checks isinstance(collection, ee.ImageCollection)."
)

with open('tests/test_timelapse.py', 'w') as f:
    f.write(content)
