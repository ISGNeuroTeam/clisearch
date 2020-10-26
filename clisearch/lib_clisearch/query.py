# -*- coding: utf-8 -*-

import time
import logging
from ot_simple_connector.connector import Connector


class OTPQuery:
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Creating OTPQuery instance")

    def __prepare_params(self):
        job_params = {
            'query_text': self.cfg.get('main', 'query'),
            'cache_ttl': self.cfg.get('main', 'ttl')
        }
        if self.cfg.get('main', 'tlast'):
            self.logger.debug("Found time last argument, with value {}".format(self.cfg.get('main', 'tlast')))
            job_params['tws'] = int(time.time()) - int(self.cfg.get('main', 'tlast'))
        else:
            if self.cfg.get('main', 'tws'):
                self.logger.debug("Found start time search argument, with value {}".format(self.cfg.get('main', 'tws')))
                job_params['tws'] = self.cfg.get('main', 'tws')
            if self.cfg.get('main', 'twf'):
                self.logger.debug("Found end time search argument, with value {}".format(self.cfg.get('main', 'twf')))
                job_params['twf'] = self.cfg.get('main', 'twf')

        if self.cfg.get('main', 'sid'):
            job_params['sid'] = self.cfg.get('main', 'sid')

        self.logger.debug("Prepared parameters for OTL query: {}".format(job_params))
        return job_params

    def get_dataset(self):
        self.logger.debug("Calculating search time range")
        job_params = self.__prepare_params()

        self.logger.debug("Creating ot_simple_connector instance")
        connector = Connector(host=self.cfg.get('main', 'host'),
                              port=self.cfg.get('main', 'port'),
                              user=self.cfg.get('main', 'username'),
                              password=self.cfg.get('main', 'password'),
                              ssl=self.cfg.getboolean('main', 'ssl', fallback=False),
                              loglevel='DEBUG')

        self.logger.debug("Creating job instance")
        job = connector.jobs.create(**job_params)
        return job.dataset
