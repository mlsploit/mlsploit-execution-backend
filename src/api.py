import json
import os
from urllib.parse import urlparse, ParseResult

from cachetools import TTLCache
import requests


API_BASE_URL = os.getenv("MLSPLOIT_API_BASE_URL")
assert API_BASE_URL, """
    MLSPLOIT_API_BASE_URL environment variable not found.
    $ export MLSPLOIT_API_BASE_URL='http://localhost:8000/api/v1'
    """


class RestClient:
    _token = None
    _cache = TTLCache(maxsize=1000, ttl=2)

    @classmethod
    def _make_auth_header(cls):
        headers = dict()
        if cls._token is not None:
            headers["Authorization"] = "Token %s" % cls._token
        return headers

    @classmethod
    def set_token(cls, token):
        cls._token = token

    @classmethod
    def get(cls, url, params=None, headers=None):
        params = params or dict()
        headers = headers or dict()
        headers.update(cls._make_auth_header())

        key = (url, tuple(params.items()), tuple(headers.items()))

        if key not in cls._cache:
            r = requests.get(url, params=params, headers=headers)

            cls._cache[key] = r.text
        data = json.loads(cls._cache[key])

        return data

    @classmethod
    def post(cls, url, payload, files=None, headers=None):
        cls._cache.clear()

        headers = headers or dict()
        headers.update(cls._make_auth_header())

        url += "/" if not url.endswith("/") else ""

        r = requests.post(url, data=payload, files=files, headers=headers)

        data = json.loads(r.text)
        return data

    @classmethod
    def patch(cls, url, payload, files=None, headers=None):
        cls._cache.clear()

        headers = headers or dict()
        headers.update(cls._make_auth_header())

        url += "/" if not url.endswith("/") else ""

        r = requests.patch(url, data=payload, files=files, headers=headers)

        data = json.loads(r.text)
        return data

    @staticmethod
    def make_path(*args):
        p = "/".join(map(lambda x: x.strip("/"), args))
        return p


class ApiDataModel(object):
    _endpoint = None
    _expandable = dict()
    _json_props = list()

    def __init__(self, url):
        endpoint = urlparse(self._endpoint)
        endpoint = ParseResult("", *endpoint[1:]).geturl()
        assert endpoint in url
        super(ApiDataModel, self).__setattr__("_url", url)

    def __getattr__(self, item):
        data = RestClient.get(self._url)

        val = data[item]
        if item in self._expandable:
            if type(self._expandable[item]) is list:
                klass = self._expandable[item][0]
                val = list(klass(v) for v in val)

            elif val is not None:
                klass = self._expandable[item]
                val = klass(val)

        elif item in self._json_props:
            val = json.loads(val)

        return val

    def __setattr__(self, key, value):
        if key in self._json_props:
            value = json.dumps(value)

        RestClient.patch(self.url, {key: value})

    def __repr__(self):
        return self._url

    @property
    def url(self):
        return self._url

    @classmethod
    def from_id(cls, id_):
        url = RestClient.make_path(cls._endpoint, str(id_)) + "/"
        return cls(url)

    @classmethod
    def create(cls, **kwargs):
        files = None
        if "blob" in kwargs:
            files = {"blob": kwargs["blob"]}
            del kwargs["blob"]

        for k in cls._json_props:
            if k in kwargs and type(kwargs[k]) in {dict, list}:
                kwargs[k] = json.dumps(kwargs[k])

        r = RestClient.post(cls._endpoint, payload=kwargs, files=files)

        return cls(r["url"])

    @classmethod
    def get_all(cls, params=None):
        all_data = RestClient.get(cls._endpoint, params=params)

        items = list()

        if type(all_data) is not list:
            return items

        for item_data in all_data:
            items.append(cls(item_data["url"]))

        return items


class Module(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "modules")
    _json_props = ["config"]


class Function(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "functions")
    _expandable = {"module": Module}
    _json_props = ["options", "optional_filetypes", "output_tags"]


class User(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "users")

    @classmethod
    def get_current(cls):
        try:
            current_user_endpoint = RestClient.make_path(
                API_BASE_URL.replace("/api/v1", ""), "auth", "user"
            )
            current_user_data = RestClient.get(current_user_endpoint)
            current_user_url = current_user_data["url"]
            return cls(current_user_url)
        except:
            return None


class File(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "files")
    _expandable = {"owner": User}
    _json_props = ["tags"]


class Task(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "tasks")
    _expandable = {"owner": User, "function": Function}
    _json_props = ["arguments"]


class Run(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "runs")
    _expandable = {"owner": User, "files": [File]}


class Job(ApiDataModel):
    _endpoint = RestClient.make_path(API_BASE_URL, "jobs")
    _expandable = {"owner": User, "task": Task, "run": Run, "output_files": [File]}
    _json_props = ["output"]

    @property
    def parent_job(self):
        parent_job_url = self.__getattr__("parent_job")
        if parent_job_url is None:
            return None

        return Job(parent_job_url)

    @classmethod
    def get_all_actionable(cls):
        all_pending_jobs = cls.get_all(params={"status": "PENDING"})

        return list(
            filter(
                lambda j: j.parent_job is None or j.parent_job.status == "FINISHED",
                all_pending_jobs,
            )
        )
