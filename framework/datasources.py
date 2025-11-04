from botcity.plugins.csv import BotCSVPlugin
from typing import Any, Dict, List
from framework.state import STATE
from functools import lru_cache
import datetime
import requests
import logging
import json
import time


logger = logging.getLogger(__name__)

'''
datasources.py
    Sets up data sources. Provides ready-to-use DatapoolSource and CSVSource classes.
    To create your own data source class, inherit from BaseSource.
'''


class BaseSource:
    """Base source for batch processing of items."""

    def report_success(self, status_message):
        raise NotImplementedError

    def report_error(self, error_type, status_message):
        raise NotImplementedError


class DatapoolSource(BaseSource):
    def __init__(self, label: str):
        self.dp = STATE.maestro.get_datapool(label)
        self.current_item = None

    def __str__(self):
        return f"Datapool {self.dp.label}"

    def __iter__(self):
        return self

    def __next__(self):
        if not self.dp.is_active():
            logger.info(f"Datapool {self.dp.label} isn't active.")
            raise StopIteration
        if not self.dp.has_next():
            return None
        item = self.dp.next(STATE.task_id)
        if not item:
            return None  # talvez tenha que usar stopiteration todo
        self.current_item = item
        STATE.item = item.values
        return item.values if item else None

    def report_success(self, status_message):
        if not self.current_item:
            return
        self.current_item.report_done()  # TODO send status message when available via API

    def report_error(self, error_type, status_message):
        if not self.current_item:
            return
        self.current_item.report_error()  # TODO send status message when available via API


class CSVSource(BaseSource):
    def __init__(self, file: str):
        self._file = file
        self.csv = BotCSVPlugin()
        self.csv_out = BotCSVPlugin()
        self.csv.read(file)
        self.csv_out_file = self.csv_result_file()
        self.csv_out.set_header(
            self.csv.header+["TIMESTAMP", "STATUS", "MESSAGE"])
        self.index = 0
        self.count = len(self.csv.as_dataframe().index)
        self.current_item = None

    def __str__(self):
        return f"CSV {self._file}"

    def __iter__(self):
        return self

    def __next__(self):
        """
        Fetch the next pending entry.
        Returns: item
        """
        if self.index >= self.count:
            logger.info(f"CSV {self._file} has no more items.")
            raise StopIteration
        item = self.csv.as_dataframe().loc[self.index].to_dict()
        self.index += 1
        STATE.item = item
        self.current_item = item
        return item

    def _report(self, status, status_message):
        if not self.current_item:
            return

        self.current_item.update({
            "TIMESTAMP": datetime.datetime.now().isoformat(),
            "STATUS": status,
            "MESSAGE": status_message
        })
        self.csv_out.add_row(self.current_item)
        self.csv_out.write(self.csv_out_file)

    def report_success(self, status_message):
        return self._report("SUCCESS", status_message)

    def report_error(self, error_type, status_message):
        return self._report(error_type, status_message)

    @staticmethod
    def csv_result_file():
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        task_id = STATE.task_id
        csv_result_file = f"./output/CSV_BotCity_task-{task_id}_date-{date}.csv"
        return csv_result_file


class APISource:
    API_URL = f'{STATE.maestro.server}/api/v2'
    TOKEN_EXPIRATION_TIME = 3600

    def __init__(self, login: str, key: str):
        self._login = login
        self._key = key
        self._token = None
        self._start_time = None

    def _get_access_token(self):
        if self._start_time is not None:
            if time.time() - self._start_time > self.TOKEN_EXPIRATION_TIME:
                self._token = None

        if self._token is None:
            url = f'{self.API_URL}/workspace/login'

            payload = json.dumps({
                'login': self._login,
                'key': self._key
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()

            self._token = response.json().get('accessToken')
            self._start_time = time.time()

        return self._token

    def _get(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        headers = {
            'organization': STATE.maestro.organization,
            'token': self._get_access_token()
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _list(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        params = params or {}
        result = None

        limit = params.pop('limit', 0)

        while True:
            page_result = self._get(url, params)

            is_last = page_result.get('last', True)
            is_empty = page_result.get('empty', True)

            page = page_result.get('number', 0)
            params['page'] = page + 1

            if result is None:
                result = page_result
            else:
                content = result.get('content', [])
                content.extend(page_result.get('content', []))
                result['content'] = content

            if is_last or is_empty or (limit is not None and len(result.get('content', [])) >= limit):
                break

        content = result.get('content', [])[:limit]
        result['content'] = content

        return result

    def get_tasks(self, *,
                  days: int = None, state_filter: str = None, activity_label: str = None, machine_id: str = None,
                  page: int = None, size: int = None, sort: List[str] = None,
                  limit: int = None) -> Dict[str, Any]:
        url = f'{self.API_URL}/task'

        params = {
            'days': days,
            'stateFilter': state_filter,
            'activityLabel': activity_label,
            'machineId': machine_id,
            'page': page,
            'size': size,
            'sort': sort,
            'limit': limit
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._list(url, params)

    def get_bots(self, *,
                 bot_id: str = None,
                 page: int = None, size: int = None, sort: List[str] = None,
                 limit: int = None) -> Dict[str, Any]:
        url = f'{self.API_URL}/bot/pagination'

        params = {
            'botId': bot_id,
            'page': page,
            'size': size,
            'sort': sort,
            'limit': limit
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._list(url, params)

    def get_activities(self, *,
                       automation: str = None, label: str = None, name: str = None,
                       page: int = None, size: int = None, sort: List[str] = None,
                       limit: int = None) -> Dict[str, Any]:
        url = f'{self.API_URL}/activity/pagination'

        params = {
            'automation': automation,
            'label': label,
            'name': name,
            'page': page,
            'size': size,
            'sort': sort,
            'limit': limit
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._list(url, params)

    def get_runners(self, *,
                    machine_id: str = None, is_online: bool = None, runner_type: str = None,
                    page: int = None, size: int = None, sort: List[str] = None,
                    limit: int = None) -> Dict[str, Any]:
        url = f'{self.API_URL}/machine/pagination'

        params = {
            'machineId': machine_id,
            'isOnline': is_online,
            'type': runner_type,
            'page': page,
            'size': size,
            'sort': sort,
            'limit': limit
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._list(url, params)

    def get_schedulings(self, *,
                        page: int = None, size: int = None, sort: List[str] = None,
                        limit: int = None) -> Dict[str, Any]:
        url = f'{self.API_URL}/scheduling'

        params = {
            'page': page,
            'size': size,
            'sort': sort,
            'limit': limit
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._list(url, params)

    def get_errors(self, *,
                   page: int = None, size: int = None, sort: List[str] = None,
                   days: int = None, task_id: str = None, automation_label: str = None,
                   limit: int = None) -> Dict[str, Any]:
        url = f'{self.API_URL}/error'

        params = {
            'page': page,
            'size': size,
            'sort': sort,
            'days': days,
            'taskId': task_id,
            'automationLabel': automation_label,
            'limit': limit
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._list(url, params)

    @lru_cache(maxsize=2000)
    def get_error_by_id(self, error_id: str) -> Dict[str, Any]:
        url = f'{self.API_URL}/error/{error_id}'
        return self._get(url)

    @staticmethod
    def get_datapool_values(self, datapool_label: str) -> Any | None:
        """
        Get the DataPool Label itens
        Returns: dict | None

        """
        url = f'{self.API_URL}/api/v2/datapool/{datapool_label}/view?displayValue=Henrique'

        headers = {'token':  self._get_access_token(), 'organization': self.login}

        with requests.get(url, headers=headers, timeout=3600) as req:
            if req.ok:
                return json.loads(req.content)
            req.raise_for_status()

        return None
"""
Setting Datasource: Datapool | CSV
"""

# data_source = DatapoolSource("BeaPro-Datapool")
data_source = [] # CSVSource(r"./resources/USPS_Zip_Codes.csv")
logger.info(f"Datasource set to {data_source}.")
