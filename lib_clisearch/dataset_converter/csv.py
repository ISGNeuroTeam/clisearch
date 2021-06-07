# -*- coding: utf-8 -*-

import logging
import csv
import io
import re

class CSV:
    @staticmethod
    def convert(dataset):
        logger = logging.getLogger(__name__)
        logger.debug('Converting dataset to csv...')
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
