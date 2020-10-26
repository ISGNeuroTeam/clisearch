# -*- coding: utf-8 -*-

import logging
import json as library_json
import re


class JSON:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def convert(self, dataset):
        self.logger.debug('Converting dataset to json...')
        header_fields = re.findall(r'`(.+?)`', dataset.schema)
        line = dataset.next()
        yield '['
        yield library_json.dumps(dict(map(lambda field: (field, str(line.get(field))), header_fields)))
        for line in dataset:
            yield library_json.dumps(dict(map(lambda field: (field, str(line.get(field))), header_fields)))
        yield ']'
