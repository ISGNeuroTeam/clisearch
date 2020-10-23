#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Логика работы.
# +    При запуске разбираются аргументы командной строки (аргументы)
# +    Если не найдена опция указывающая на конфигурационный файл, то берется файл по умолчанию находящийся в той же директории где находится исполняемый файл.
# +    Разбирается конфигурационный файл (конфиг)
# +    Производится проверка корректности конфигурационного файла, не заданные значения заполняются значениями по умолчанию.
# +    Производится проверка аргументов, не заданные значения заполняются значениями по умолчанию.
# +    Инициализация системы логирования
#     Запускается запрос к ОТ.Платформе
#     Ожидается выполнение запроса
#     В случае сбоя выполнения запроса завершение с выдачей ошибки в лог файл и завершение с кодом возврата не равное нулю.
#     Преобразование данных в требуемый формат
#     Выдача в STDOUT результата
#
# При подготовке дистрибутива нужно проверить ssl для requests (чтобы при сборке была возможность его использовать)

import os
import sys
import argparse
import configparser
import re
import logging
from ot_simple_connector.connector import Connector
import time
import json

__author__ = "Alexander Matiakubov"
__copyright__ = "Copyright 2020, ISG Neuro"
__license__ = "LICENSE.md"
__version__ = "0.0.1"
__maintainer__ = "Alexander Matiakubov"
__email__ = "ma@makuba.ru"
__status__ = "Development"


def load_cfg(config_filename):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_filename)

    if 'main' not in config.sections():
        print("Configuration file error, section 'main' not defined")
        quit(255)

    for k in ('host', 'username', 'password'):
        v = config.get('main', k, fallback='')
        if not v or re.search(' ', v):
            print("Configuration file error, {} value is not correct '{}'".format(k, v))
            quit(255)

    try:
        if not config.getint('main', 'port', fallback=0):
            print("Configuration file error, host value is not correct")
            quit(255)
    except Exception:
        print("Configuration file error, port value is incorrect")
        quit(255)

    try:
        config.getboolean('main', 'ssl', fallback=False)
    except Exception:
        print("Configuration file error, ssl value is not defined or incorrect")
        quit(255)

    if 'logger' not in config.sections():
        config.add_section('logger')

    try:
        config.getboolean('logger', 'enable', fallback=False)
    except Exception:
        print("Configuration file error, ssl value is not defined or incorrect")
        quit(255)

    if config.getboolean('logger', 'enable', fallback=False):
        loglevel = config.get('logger', 'loglevel', fallback='')
        if not loglevel or not re.search('^(debug|info|warning|error|critical)$', loglevel,
                                         re.IGNORECASE):
            print("Configuration file error, {} value is not correct '{}'".format('loglevel', loglevel))
            quit(255)

        output = config.get('logger', 'output', fallback='')
        if not output or not re.search('^(stdout|stderr|file)$', output, re.IGNORECASE):
            print("Configuration file error, {} value is not correct '{}'".format('output', output))
            quit(255)

        if output.lower() == 'file':
            logfile = config.get('logger', 'logfile', fallback='')
            if not logfile or os.path.isdir(logfile):
                print("Configuration file error, {} value is not correct '{}'".format('logfile', logfile))
                quit(255)

    return config


def get_logger(cfg):
    logger = logging.getLogger('clisearch')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-s PID=%(process)d %(module)s:%(lineno)d func=%(funcName)s - %(message)s'
    )

    if cfg.getboolean('enable', fallback=False):
        if cfg.get('output').lower() in ('stderr', 'stdout'):
            if cfg.get('output').lower() == 'stderr':
                ch = logging.StreamHandler(stream=sys.stderr)
            else:
                ch = logging.StreamHandler(stream=sys.stdout)
            ch.setFormatter(formatter)
            ch.setLevel(cfg.get('loglevel').upper())
            logger.addHandler(ch)

        elif cfg.get('output').lower() == 'file':
            fh = logging.FileHandler(cfg.get('logfile'))
            fh.setFormatter(formatter)
            fh.setLevel(cfg.get('loglevel').upper())
            logger.addHandler(fh)
    else:
        logger.addHandler(logging.NullHandler())

    logger.setLevel(cfg.get('loglevel').upper())
    return logger


def dataset_as_csv(dataset):
    import csv
    writer = csv.writer(sys.stdout, delimiter=',')

    header_fields = re.findall(r'`(.+?)`', dataset.schema)
    writer.writerow(header_fields)

    for line in dataset:
        fields = []
        for field in header_fields:
            fields.append(str(line.get(field)))
        writer.writerow(fields)


def dataset_as_json(dataset):
    import json

    header_fields = re.findall(r'`(.+?)`', dataset.schema)
    print('[{}]'.format(', '.join(map(lambda y: json.dumps(dict(map(lambda x: (x, str(y.get(x))), header_fields))), dataset))))


def main():
    parser = argparse.ArgumentParser(add_help=True,
                                     allow_abbrev=False,
                                     description='CLI Search utility')
    parser.add_argument('--config', '-c', default='clisearch.cfg', help='Configuration file')
    parser.add_argument('--ttl', default=60, type=int, help='Time to live request search')
    parser.add_argument('--tws', default=0, type=int, help='Start search time (epoch)')
    parser.add_argument('--twf', default=0, type=int, help='End search time (epoch)')
    parser.add_argument('--tlast', default=0, type=int, help='Time in seconds from current time')
    parser.add_argument('--sid', default='', type=str, help='Search ID')
    parser.add_argument('--output', default='csv', choices=['csv', 'json'], help='Select output type')
    parser.add_argument('--query', type=str, required=True, help='OTL query text')
    args = parser.parse_args()

    if args.config == 'clisearch.cfg':
        args.config = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'clisearch.cfg')
    elif not (os.path.exists(args.config) and os.path.isfile(args.config)):
        print("File '{}' not exist or not regular file".format(args.config))
        parser.print_help()
        quit(255)

    cfg = load_cfg(args.config)

    logger = get_logger(cfg['logger'])
    logger.info("Started CLI search utility, version {}".format(__version__))

    logger.debug("Calculating search time range")
    job_params = {
        'query_text': args.query,
        'cache_ttl': args.ttl
    }

    if args.tlast:
        logger.debug("Found time last argument, with value {}".format(args.tlast))
        job_params['tws'] = int(time.time()) - int(args.tlast)
    else:
        if args.tws:
            logger.debug("Found start time search argument, with value {}".format(args.tws))
            job_params['tws'] = args.tws
        elif args.twf:
            logger.debug("Found end time search argument, with value {}".format(args.twf))
            job_params['twf'] = args.twf

    if args.sid:
        job_params['sid'] = args.sid

    logger.debug("Request with parameters: {}".format(job_params))
    logger.debug("Creating ot_simple_connector instance")
    connector = Connector(host=cfg.get('main', 'host'),
                          port=cfg.get('main', 'port'),
                          user=cfg.get('main', 'username'),
                          password=cfg.get('main', 'password'),
                          ssl=cfg.getboolean('main', 'ssl', fallback=False),
                          loglevel='DEBUG')

    logger.debug("Creating job instance")
    job = connector.jobs.create(**job_params)

    if args.output == 'csv':
        logger.debug("Select output as CSV")
        dataset_as_csv(job.dataset)
    elif args.output == 'json':
        logger.debug("Select output as JSON")
        dataset_as_json(job.dataset)

    logger.info("Finished CLI search utility")


if __name__ == '__main__':
    main()
