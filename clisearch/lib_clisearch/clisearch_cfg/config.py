#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging


class Config(configparser.ConfigParser):
    def __init__(self):
        super().__init__(allow_no_value=True)
        self.__predefined = {}
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Creating Config instance")

    def additem(self, key, **kwargs):
        """
        additem(self, key, section='DEFAULT', default=None, defined=False, type='text', func_check=None):
        :param key:
        :param default:
        :param type:
            int
            uint
            text
            text_re
            host    hostname or IP address
            cred
            boolean

        :param func_check:

        :return:
        """
        if 'section' in kwargs:
            section = kwargs['section']
        else:
            section = 'DEFAULT'
        if section not in self.__predefined:
            self.__predefined[section] = {}
        self.__predefined[section][key] = kwargs
        self.logger.debug(
            'Add key template in section "{}", key "{}", with params: {}'.format(section, key, str(kwargs)))

    def read(self, filenames, encoding=None):
        self.logger.debug('Reading configuration file from file "{}"'.format(filenames))
        super().read(filenames, encoding)
        self._check_all()

    def _check_all(self):
        self.logger.debug('Checking configuration file on template correctly')
        for section in self.__predefined:
            for key in self.__predefined[section]:
                value = self.__predefined[section][key]

                if 'replace' in value and not value['replace'] is None:
                    self.set(section, key, str(value['replace']))
                    self.logger.debug('Section "{}", key "{}", set replace value "{}"'.
                                      format(section, key, str(value['replace'])))

                try:
                    self.get(section, key)
                except:
                    self.logger.debug('Section "{}", key "{}", not defined in configuration file'.format(section, key))
                    if 'defined' in value and value['defined']:
                        self.logger.error("Key '{}' in section '{}' not defined".format(key, section))
                        raise BaseException("Key '{}' in section '{}' not defined".format(key, section))
                    elif 'default' in value:
                        self.logger.debug('Section "{}", key "{}", set default value "{}"'.
                                          format(section, key, str(value['default'])))
                        self.set(section, key, str(value['default']))

                if 'type' not in value:
                    self.logger.error("Type for key '{}' in section '{}' not defined, please, contact to developer".
                                      format(key, section))
                    raise BaseException("Type for key '{}' in section '{}' not defined, please, contact to developer".
                                        format(key, section))

                elif value['type'] == 'text':
                    # no need check text fields
                    pass

                elif value['type'] == 'text_re':
                    v = self.get(section, key)
                    if not value['func_check'](v):
                        self.logger.error("Key '{}' in section '{}' not correct '{}'".format(key, section, v))
                        raise BaseException("Key '{}' in section '{}' not correct '{}'".format(key, section, v))

                elif value['type'] == 'int' \
                        or value['type'] == 'uint':
                    try:
                        v = self.getint(section, key)
                    except Exception:
                        self.logger.error("Key '{}' in section '{}' not integer value".format(key, section))
                        raise BaseException("Key '{}' in section '{}' not integer value".format(key, section))

                    if value['type'] == 'uint' and (v is None or v < 0):
                        self.logger.error("Key '{}' in section '{}' not unsigned integer, '{}'".
                                          format(key, section, v))
                        raise (BaseException("Key '{}' in section '{}' not unsigned integer, '{}'".
                                             format(key, section, v)))

                elif value['type'] == 'boolean':
                    try:
                        self.getboolean(section, key)
                    except Exception:
                        self.logger.error("Key '{}' in section '{}' not boolean value".format(key, section))
                        raise BaseException("Key '{}' in section '{}' not boolean value".format(key, section))

                else:
                    self.logger.error("Value type not defined Key '{}' in section '{}' not defined, "
                                      "please, contact to developer".format(key, section))
                    raise BaseException("Value type not defined Key '{}' in section '{}' not defined, "
                                        "please, contact to developer".format(key, section))

    def dump(self):
        return dict(map(lambda x: (x, dict(self[x])), self.sections()))

    def dump_items(self):
        return self.__predefined
