import json
from typing import Optional, Union, Tuple

import requests
import logging
import sys
import argparse

logger = logging.getLogger("super_scheduler")

AUTH_URL, SUPER_SCHEDULER_URL, COMPLEX_REST_HOST, COMPLEX_REST_PORT, USERNAME, PASSWORD = [None] * 6


# class SuperScheduler:
#     AUTH_URL = AUTH_URL
#     SUPER_SCHEDULER_URL = SUPER_SCHEDULER_URL
#     COMPLEX_REST_HOST = COMPLEX_REST_HOST
#     COMPLEX_REST_PORT = COMPLEX_REST_PORT
#     USERNAME = USERNAME
#     PASSWORD = PASSWORD
#
#     logger = logger
#     split_chr = ','
#
#     # SCHEDULE_TASK = 'super_scheduler.tasks.otl_makejob'
#
#     @classmethod
#     def pretty_print(cls, data_str2dict: Optional[str] = None,
#                      data_dict2dict: Optional[dict] = None):
#         if data_str2dict:
#             data_dict2dict = json.loads(data_str2dict)
#         if data_dict2dict:
#             print(json.dumps(data_dict2dict, indent=4))
#
#     @classmethod
#     def auth(cls) -> str:
#         address = cls.COMPLEX_REST_HOST + ':' + cls.COMPLEX_REST_PORT
#         url = f'http://{address}/{cls.AUTH_URL}'
#
#         data = {
#             'login': cls.USERNAME,
#             'password': cls.PASSWORD
#         }
#
#         content = requests.post(url, data=data)
#
#         if content.status_code == 200:
#             token = content.json()['token']
#             return token
#
#         cls.logger.debug(f"{content.status_code}, {content.text}")
#         raise ValueError("Can't get token")
#
#     @classmethod
#     def parse_schedule(cls, schedule_parsers: dict, is_required: bool = True) -> Optional[dict]:
#         """
#         Return schedule.
#
#         :param schedule_parsers: schedule parsers
#         :return: schedule
#         """
#
#         def preprocess_schedule(schedule_dict):
#             if schedule_dict['name'] == 'crontab':
#                 if 'crontab_line' in schedule_dict and schedule_dict['crontab_line']:
#                     crontab_line = schedule_dict['crontab_line']
#                     crontab_line = crontab_line.split(' ')
#                     if len(crontab_line) != 5:
#                         raise ValueError("Enter 5 params in crontab line. "
#                                          "Example: '32 18 mon,wed 17,21,29 * *', '10 * * * *'")
#                     schedule_time_params = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')
#                     for param, value in zip(schedule_time_params, crontab_line):
#                         schedule_dict[param] = value
#             return schedule_dict
#
#         schedule_dict = None
#         for schedule_name in schedule_parsers:
#             if schedule_name in sys.argv[1:]:
#                 if schedule_dict is not None:
#                     raise ValueError("Use only one schedule type!")
#                 schedule_dict = schedule_parsers[schedule_name].parse_known_args()[0].__dict__
#                 schedule_dict['name'] = schedule_name
#                 preprocess_schedule(schedule_dict)
#                 return schedule_dict
#         if is_required:
#             raise ValueError("No schedule or can't parse it, see documentation and examples")
#         return schedule_dict
#
#     @classmethod
#     def data_construction(cls,
#                           task: Optional[str],
#                           task_name: Optional[str],
#                           schedule_parsers: dict,
#                           task_args: Optional[str] = None,
#                           task_kwargs: Optional[str] = None,
#                           one_off: Optional[bool] = None,
#                           required_one_off_schedules: Optional[list[str]] = None,
#                           is_required_schedule: bool = True) -> dict:
#         """
#
#         :param task:
#         :param schedule_parsers:
#         :param task_args:
#         :param task_kwargs:
#         :param task_name:
#         :param one_off:
#         :param required_one_off_schedules:
#         :param is_required_schedule:
#         :return:
#         """
#
#         # schedule
#         schedule_dict = cls.parse_schedule(schedule_parsers, is_required=is_required_schedule)
#         if schedule_dict and required_one_off_schedules and schedule_dict['name'] in required_one_off_schedules:
#             one_off = True
#
#         # construct data
#         data = {
#             'task':
#                 {
#                     'name': task_name,
#                     'task': task,
#                 },
#             'schedule': schedule_dict,
#         }
#
#         if one_off:
#             data['task']['one_off'] = one_off
#         if task_args:
#             task_args = task_args.split(cls.split_chr)
#             data['task']['args'] = task_args
#         if task_kwargs:
#             task_kwargs = task_kwargs.split(cls.split_chr)
#             task_kwargs = [kwarg.split('=') for kwarg in task_kwargs]
#             task_kwargs = {kwarg[0]: kwarg[-1] for kwarg in task_kwargs}
#             data['task']['kwargs'] = task_kwargs
#
#         return data
#
#     @classmethod
#     def send_request(cls, data, token, post: bool = False, delete: bool = False, get: bool = False):
#         address = cls.COMPLEX_REST_HOST + ':' + cls.COMPLEX_REST_PORT
#         url = f'http://{address}/{cls.SUPER_SCHEDULER_URL}'
#         headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
#         data = json.dumps(data)
#         content = None
#         if post:
#             content = requests.post(url, data=data, headers=headers)
#         elif delete:
#             content = requests.delete(url, data=data, headers=headers)
#         elif get:
#             content = requests.get(url, data=data, headers=headers)
#         if content is not None:
#             cls.logger.info(f"Finish request with code {content.status_code}.")
#             print("\nResult:")
#             if isinstance(content.text, str):
#                 cls.pretty_print(data_str2dict=content.text)
#             else:
#                 print(content.text)
#             return content.status_code
#         else:
#             raise ValueError("Finish request without content")
#
#     @classmethod
#     def create_schedule_subparsers(cls, subparsers) -> (dict, list):
#
#         # schedule subparsers
#         schedule_parsers = {}
#
#         crontab_schedule_name = 'crontab'
#         crontab_parser = subparsers.add_parser(crontab_schedule_name)
#         schedule_parsers[crontab_schedule_name] = crontab_parser
#         crontab_parser.add_argument('--minute', type=str, help=f'Default \'*\'', default='*')
#         crontab_parser.add_argument('--hour', type=str, help=f'Default \'*\'', default='*')
#         crontab_parser.add_argument('--day_of_week', type=str, help=f'Default \'*\'', default='*')
#         crontab_parser.add_argument('--day_of_month', type=str, help=f'Default \'*\'', default='*')
#         crontab_parser.add_argument('--month_of_year', type=str, help=f'Default \'*\'', default='*')
#         crontab_parser.add_argument('--crontab_line', type=str,
#                                     help=f"Short recording of all previous parameters in one line. Default empty. "
#                                          f"Example: '32 18 17,21,29 11 mon,wed', '10 * * * *'",
#                                     default=None)
#
#         interval_schedule_name = 'interval'
#         interval_parser = subparsers.add_parser(interval_schedule_name)
#         schedule_parsers[interval_schedule_name] = interval_parser
#         interval_parser.add_argument('--every', type=int, required=True, help='Run every N * time range')
#         interval_parser.add_argument('--period', type=str, required=True, help='Time range; example: minutes')
#
#         solar_schedule_name = 'solar'
#         solar_parser = subparsers.add_parser(solar_schedule_name)
#         schedule_parsers[solar_schedule_name] = solar_parser
#         solar_parser.add_argument('--event', type=str, required=True,
#                                   help="Solar events. Available: 'dawn_astronomical', 'dawn_nautical', 'dawn_civil', 'sunrise', 'solar_noon', 'sunset', 'dusk_civil', 'dusk_nautical', 'dusk_astronomical'. "
#                                        'For more info: https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#solar-schedules')
#         solar_parser.add_argument('--latitude', type=Union[int, float], required=True,
#                                   help='Current latitude. Value must be between -180 and 180.')
#         solar_parser.add_argument('--longitude', type=Union[int, float], required=True,
#                                   help='Current longitude. Value must be between -180 and 180.')
#
#         clocked_schedule_name = 'clocked'
#         clocked_parser = subparsers.add_parser(clocked_schedule_name)
#         schedule_parsers[clocked_schedule_name] = clocked_parser
#         clocked_parser.add_argument('--clocked_time', type=str, required=True,
#                                     help='Datetime format; example: 2023-11-28 01:01:01')
#
#         required_one_off_schedules = [clocked_schedule_name, ]
#
#         return schedule_parsers, required_one_off_schedules
#
#     @classmethod
#     def create_task_subparsers(cls, subparsers):
#
#         task_parser = subparsers.add_parser('task')
#
#         task_parser.add_argument('-T', '--task', type=str,
#                                  help="Task for schedule. Example: \'super_scheduler.tasks.test_logger\'. "
#                                       "To see all available tasks use flag '--get'.")
#         task_parser.add_argument('-N', '--name', type=str, help='Periodic task (scheduled) name. Must be unique.')
#         task_parser.add_argument('--args', type=str,
#                                  help="Task args if necessary. Only use with argument '--task'. "
#                                       "Example: '--args \"value1,value2,value3\"', '--args \"ls,-la\"'")
#         task_parser.add_argument('--kwargs', type=str, nargs="*",
#                                  help="Task kwargs if necessary. Only use with argument '--task'. "
#                                       "Example: '--kwargs \"arg1=value1,arg2=value2\"'")
#         task_parser.add_argument('--one_off', action='store_true', help="Run periodic task only ones. "
#                                                                         "Always use with 'clocked' schedule.")
#
#         return task_parser
#
#     @classmethod
#     def create_parsers(cls):
#         parser = argparse.ArgumentParser(
#             description='SuperScheduler client.\n'
#                         'To see schedule args.\n'
#                         "Use '--' to split positional arguments."
#         )
#
#         parser.add_argument('-U', '--username', type=str,
#                             help=f'Username for authorization. Default: \'{cls.USERNAME}\'.', default=cls.USERNAME)
#         parser.add_argument('-P', '--password', type=str,
#                             help=f'User password for authorization. Default: \'{cls.PASSWORD}\'.', default=cls.PASSWORD)
#
#         parser.add_argument('--host', type=str, help=f'Ip complex_rest. Default: \'{cls.COMPLEX_REST_HOST}\'.',
#                             default=cls.COMPLEX_REST_HOST)
#         parser.add_argument('--port', type=str, help=f'Port complex_rest. Default: \'{cls.COMPLEX_REST_PORT}\'.',
#                             default=cls.COMPLEX_REST_PORT)
#
#         parser.add_argument('--create', action='store_true',
#                             help="Create periodic task. Required argumets: '--task', '--name'. "
#                                  "Optional argumets: '--args', '--kwargs', '--one_off'.")
#         parser.add_argument('--delete', action='store_true',
#                             help="Delete periodic task. Required arguments: '--name'.")
#         parser.add_argument('--get', action='store_true',
#                             help='Get all available tasks and names of periodic tasks. Non required argumets.')
#
#         subparsers = parser.add_subparsers()
#         task_parser = SuperScheduler.create_task_subparsers(subparsers)
#         task_subparsers = task_parser.add_subparsers()
#         schedule_parsers, required_one_off_schedules = SuperScheduler.create_schedule_subparsers(task_subparsers)
#
#         return parser, subparsers, task_parser, task_subparsers, schedule_parsers, required_one_off_schedules


class SuperScheduler:
    AUTH_URL = None
    SUPER_SCHEDULER_URL = None
    COMPLEX_REST_HOST = None
    COMPLEX_REST_PORT = None
    USERNAME = None
    PASSWORD = None

    logger = logger
    split_chr = ','

    # SCHEDULE_TASK = 'super_scheduler.tasks.otl_makejob'

    def __init__(self):
        self.token = None
        self.data = None

    @classmethod
    def init_cls_variables(
            cls,
            auth_url: Optional[str] = None,
            super_scheduler_url: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[str] = None):
        cls.AUTH_URL = auth_url
        cls.SUPER_SCHEDULER_URL = super_scheduler_url
        cls.USERNAME = username
        cls.PASSWORD = password
        cls.COMPLEX_REST_HOST = host
        cls.COMPLEX_REST_PORT = port

    @property
    def address(self) -> str:
        return self.COMPLEX_REST_HOST + ':' + self.COMPLEX_REST_PORT

    @property
    def header(self) -> Optional[dict]:
        return {"Authorization": f"Bearer {self.token}", 'Content-Type': 'application/json'}

    @classmethod
    def pretty_print(cls, data_str2dict: Optional[str] = None,
                     data_dict2dict: Optional[dict] = None):
        if data_str2dict:
            data_dict2dict = json.loads(data_str2dict)
        if data_dict2dict:
            print(json.dumps(data_dict2dict, indent=4))

    def send_request(self, data: dict, url: str, post: bool = False, delete: bool = False, get: bool = False) -> \
            Tuple[requests.models.Response, int]:
        """
        Send request to url with data.

        :param data:
        :param url:
        :param post:
        :param delete:
        :param get:
        :return:
        """
        data = json.dumps(data)
        if post:
            content = requests.post(url, data=data, headers=self.header)
        elif delete:
            content = requests.delete(url, data=data, headers=self.header)
        elif get:
            content = requests.get(url, data=data, headers=self.header)
        else:
            content = None

        return content, content.status_code

    def auth(self) -> str:

        self.data = {
            'login': self.USERNAME,
            'password': self.PASSWORD
        }
        url = f'http://{self.address}/{self.AUTH_URL}'
        content, status_code = self.send_request(url=url, data=self.data, post=True)

        if status_code == 200:
            token = content.json()['token']
            self.token = token
            return token

        self.logger.debug(f"Can't get token; {status_code}, {content.text}")
        raise ValueError("Can't get token")

    def new_data_construction(self,
                              task_args: dict, schedule_args: dict,
                              required_one_off_schedules: Optional[list[str]] = None,):
        if schedule_args.get('name') and schedule_args['name'] in required_one_off_schedules:
            task_args['one_off'] = True
        data = {
            'task': task_args,
            'schedule': schedule_args,
        }
        self.data = data
        return data

    def send_request_to_super_scheduler(self, post: bool = False, delete: bool = False, get: bool = False):
        url = f'http://{self.address}/{self.SUPER_SCHEDULER_URL}'
        content, status_code = self.send_request(url=url, data=self.data, post=post, delete=delete, get=get)

        if content is not None:
            self.logger.info(f"Finish request with code {content.status_code}.")
            print("\nResult:")
            if isinstance(content.text, str):
                self.pretty_print(data_str2dict=content.text)
            else:
                print(content.text)
            return content.status_code

        else:
            raise ValueError("Finish request without content")
