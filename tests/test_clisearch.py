import unittest
import json

from lib_clisearch import dataset_converter
import ot_simple_connector


class MockDataset:

    def __init__(self, data: list):
        self.schema = None
        self.data = data
        self.g = self._dataiter()

    def _dataiter(self):
        for item in self.data:
            yield item

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        return self.g.__next__()


def mock_dataset():
    data = [{'A': str(i), 'B': str(j)} for i in range(10) for j in range(10)]
    ds = MockDataset(data)
    ds.schema = "`A` STRING,`B` STRING"
    return ds


class TestConnector(unittest.TestCase):

    def setUp(self) -> None:
        self.ds = mock_dataset()

    def test_json(self):
        d = dataset_converter.DatasetConverter(self.ds)
        self.assertEqual(
            json.loads(
                ''.join(d.get_json())
            ),
            self.ds.data
        )