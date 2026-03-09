import ee
from unittest import mock

collection_mock = mock.MagicMock(spec=ee.ImageCollection)
print(callable(collection_mock.size))
