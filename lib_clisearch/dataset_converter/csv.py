# -*- coding: utf-8 -*-

import logging
import csv
import re


class OneLineBuffer:

    def __init__(self):
        self.buffer = ''

    def write(self, data):
        self.buffer = data

    def read(self):
        res = self.buffer
        self.buffer = ''
        return res


class CSV:

    @staticmethod
    def convert(dataset, separator):
        logger = logging.getLogger(__name__)
        logger.debug('Converting dataset to csv...')
        buffer = OneLineBuffer()
        writer = csv.writer(buffer, delimiter=separator, lineterminator='\n')

        header_fields = re.findall(r'`(.+?)`', dataset.schema)
        writer.writerow(header_fields)
        yield buffer.read()

        for line in dataset:
            fields = []
            for field in header_fields:
                fields.append(str(line.get(field)))
            writer.writerow(fields)
            yield buffer.read()

