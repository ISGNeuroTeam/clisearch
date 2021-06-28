# -*- coding: utf-8 -*-

from .csv import CSV
from .json import JSON
import logging
import sys


class DatasetConverter:
    def __init__(self, dataset):
        self.dataset = dataset
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Creating DatasetConverter instance")

    def get_csv(self, separator=','):
        return CSV.convert(self.dataset, separator)

    def get_json(self):
        return JSON.convert(self.dataset)

    def print_csv(self, separator):
        self.logger.debug("Printing dataset as CSV")
        for row in self.get_csv(separator):
            sys.stdout.write(row)

    def print_json(self):
        self.logger.debug("Printing dataset as JSON")
        for row in self.get_json():
            sys.stdout.write(row)
