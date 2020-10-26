# -*- coding: utf-8 -*-

import logging
import csv
import io
import re

class CSV:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def convert(self, dataset):
        self.logger.debug('Converting dataset to csv...')
        data = io.StringIO()
        writer = csv.writer(data, delimiter=',')

        header_fields = re.findall(r'`(.+?)`', dataset.schema)
        writer.writerow(header_fields)

        for line in dataset:
            fields = []
            for field in header_fields:
                fields.append(str(line.get(field)))
            writer.writerow(fields)
            yield data.getvalue()
            data.truncate(0)
