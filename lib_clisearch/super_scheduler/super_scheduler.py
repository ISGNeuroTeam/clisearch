import json
import time
from typing import Optional

import requests


class SuperScheduler:

    SCHEDULE_TASK = 'super_scheduler.tasks.otl_makejob'

    def __init__(self, args, cfg, logger, schedule):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        self.schedule = schedule

    @staticmethod
    def auth(address, username, password):

        url = f'http://{address}/auth/login'

        data = {
            'login': username,
            'password': password
        }

        content = requests.post(url, data=data)
        if content.status_code == 200:
            token = content.json()['token']
            return token
        print(content.status_code, content.text)
        raise ValueError("Can't get token")

    @staticmethod
    def get_schedule(args, schedule_parsers) -> Optional[dict]:
        if 'schedule_name' in args:
            schedule_name = args.schedule_name

            schedule_dict = schedule_parsers[schedule_name].parse_known_args()[0].__dict__
            schedule_dict['name'] = schedule_dict['schedule_name']
            return schedule_dict
        return None

    @classmethod
    def construct_data(cls, otl: str, schedule: Optional[dict], complex_rest_address: str,
                       tws: int = 0, twf: int = 0, sid: int = 999999, ttl: int = 100, timeout: int = 100,
                       username: str = 'admin') -> dict:
        data = {
            'task':
                {
                    'name': f'schedule_otl_clisearch_{time.time()}',
                    'task': cls.SCHEDULE_TASK,
                    'args': [otl, complex_rest_address, tws, twf, sid, ttl, timeout, username]
                },
            'schedule': schedule,
        }
        return data

    @staticmethod
    def send_request(data, address, token, post: bool = False, delete: bool = False, get: bool = False):
        url = f'http://{address}/super_scheduler/v1/task/'
        headers = {"Authorization": f"Bearer {token}", 'Content-Type': 'application/json'}
        data = json.dumps(data)
        content = None
        if post:
            content = requests.post(url, data=data, headers=headers)
        elif delete:
            content = requests.delete(url, data=data, headers=headers)
        elif get:
            content = requests.get(url, data=data, headers=headers)
        print(content)
        if content is not None:
            # print(content.status_code, content.text)
            return content.status_code
        return None

    def process(self):
        self.logger.info("Creating schedule periodic task with otl queue...")
        host, port = self.cfg.get('main', 'host'), self.cfg.get('main', 'port')
        address = f'{host}:{port}'
        username, password = self.cfg.get('main', 'username'), self.cfg.get('main', 'password')
        token = SuperScheduler.auth(address, username, password)
        data = SuperScheduler.construct_data(self.args.query,
                                             self.schedule,
                                             complex_rest_address=address,)
        # print(data)
        status_code = SuperScheduler.send_request(data, address, token, post=True)
        self.logger.info(f"Finish. Status code: {status_code}")
        return status_code
