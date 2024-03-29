#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import re
import sys
from pathlib import Path
import site

import lib_clisearch.clisearch_cfg as config
import lib_clisearch.clisearch_logger as cs_logger
import lib_clisearch.dataset_converter as dc
from lib_clisearch.query import OTPQuery
from clisearch import __version__


def get_args():
    parser = argparse.ArgumentParser(add_help=True,
                                     allow_abbrev=False,
                                     description='CLI Search utility')
    parser.add_argument('--config', '-c', default='clisearch.cfg', help='Configuration file')
    parser.add_argument('--ttl', type=int, help='Time to live request search')
    parser.add_argument('--tws', type=int, help='Start search time (epoch)')
    parser.add_argument('--twf', type=int, help='End search time (epoch)')
    parser.add_argument('--tlast', type=int, help='Time in seconds from current time')
    parser.add_argument('--sid', type=str, help='Search ID')
    parser.add_argument('--loglevel', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Select loglevel')
    parser.add_argument('--logoutput', type=str, help='Logger output destination (STDERR, STDOUT, NULL or filename)')
    parser.add_argument('--output', choices=['csv', 'json'], help='Select output type')
    parser.add_argument('--query', type=str, required=True, help='OTL query text')

    # parser.add_argument('--ttl', default=60, type=int, help='Time to live request search')
    # parser.add_argument('--tws', default=0, type=int, help='Start search time (epoch)')
    # parser.add_argument('--twf', default=0, type=int, help='End search time (epoch)')
    # parser.add_argument('--tlast', default=0, type=int, help='Time in seconds from current time')
    # parser.add_argument('--sid', default='', type=str, help='Search ID')
    # parser.add_argument('--loglevel', default='critical', choices=['debug', 'info', 'warning', 'error', 'critical'],
    #                     help='Select loglevel')
    # parser.add_argument('--logoutput', default='STDERR', type=str,
    #                     help='Logger output destination (STDERR, STDOUT, NULL or filename')
    # parser.add_argument('--output', default='csv', choices=['csv', 'json'], help='Select output type')
    # parser.add_argument('--query', type=str, required=True, help='OTL query text')
    return parser.parse_args()


def get_config(args):
    cfg = config.Config()
    cfg.additem(key='host', section='main', defined=True, type='text_re',
                func_check=lambda x: re.search('^[^\s]+$', x))
    cfg.additem(key='username', section='main', defined=True, type='text_re',
                func_check=lambda x: re.search('^[^\s]+$', x))
    cfg.additem(key='password', section='main', defined=True, type='text_re',
                func_check=lambda x: re.search('^[^\s]+$', x))
    cfg.additem(key='port', section='main', defined=True, type='uint')
    cfg.additem(key='ssl', section='main', default=False, type='boolean')

    cfg.additem(key='loglevel', section='main', default='info', replace=args.loglevel, defined=False, type='text_re',
                func_check=lambda x: re.search('^(debug|info|warning|error|critical)$', x, re.IGNORECASE))
    cfg.additem(key='logoutput', section='main', default='STDERR', replace=args.logoutput, defined=False,
                type='text_re',
                func_check=lambda x: re.search('^(STDOUT|STDERR|.+)$', x))

    cfg.additem(key='ttl', section='main', default=60, type='uint', replace=args.ttl)
    cfg.additem(key='tws', section='main', default=0, type='uint', replace=args.tws)
    cfg.additem(key='twf', section='main', default=0, type='uint', replace=args.twf)
    cfg.additem(key='tlast', section='main', default=0, type='uint', replace=args.tlast)
    cfg.additem(key='sid', section='main', default='', type='text', replace=args.sid)
    cfg.additem(key='query', section='main', type='text', replace=args.query)
    cfg.additem(key='output', section='main', default='csv', type='text', replace=args.output)

    cfg.read(args.config)
    return cfg


def main():
    args = get_args()
    logger = cs_logger.get_logger('STDERR' if args.logoutput is None else args.logoutput,
                                  'CRITICAL' if args.loglevel is None else args.loglevel)
    # logger = cs_logger.get_logger(args.logoutput, args.loglevel)

    if args.config == 'clisearch.cfg':
        config_file = Path('./', 'clisearch.cfg')
        if not config_file.exists():
            env_path = os.environ.get('VIRTUAL_ENV', '/usr/local')
            config_file = Path(env_path, 'clisearch.cfg')
            if not config_file.exists():
                print("File '{}' does not exist or is not a regular file".format(args.config))
                sys.exit(255)
        args.config = config_file


    try:
        cfg = get_config(args)
    except:
        logger.critical("Unexpected error", exc_info=True)
        print('exception')
        sys.exit(255)

    logger = cs_logger.get_logger(cfg.get('main', 'logoutput'), cfg.get('main', 'loglevel'), reinit=True)
    logger.info("Started CLI search utility, version {}, loglevel {}".format(__version__, cfg.get('main', 'loglevel')))

    try:
        otp = OTPQuery(cfg)
        dataset = otp.get_dataset()

        conv = dc.DatasetConverter(dataset)
        if cfg.get('main', 'output').lower() == 'csv':
            conv.print_csv(separator=cfg.get('main', 'csv separator'))
        elif cfg.get('main', 'output').lower() == 'json':
            conv.print_json()
    except:
        logger.critical("Unexpected error", exc_info=True)
        print('exception')
        sys.exit(255)

    logger.info("Finished CLI search utility")


if __name__ == '__main__':
    main()
