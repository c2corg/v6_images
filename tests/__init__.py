import logging
import os
import requests
import subprocess
import time

BASE_WSGI_URL = 'http://localhost:8480/'
LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(levelname)5s %(name)s %(message)s")
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARN)

data_folder = os.path.dirname(__file__)


class Composition(object):
    def __init__(self, request, composition="docker-compose.test.yml"):
        self.composition = composition
        if os.environ.get("docker_stop", "1") == "1":
            request.addfinalizer(self.stop_all)
        if os.environ.get("docker_start", "1") == "1":
            subprocess.check_call(['docker-compose', '--file', composition, 'rm', '-f'])

            # to rebuild testDB, if needed
            subprocess.check_call(['docker-compose', '--file', composition, 'build'])

            subprocess.check_call(['docker-compose', '--file', composition, 'up', '-d'])

    def stop_all(self):
        subprocess.check_call(['docker-compose', '--file', self.composition, 'stop'])

    def stop(self, container):
        subprocess.check_call(['docker', '--log-level=warn', 'stop', 'c2corg_images_%s_1' % container])

    def restart(self, container):
        subprocess.check_call(['docker', '--log-level=warn', 'restart', 'c2corg_images_%s_1' % container])


def wait_wsgi():
    timeout = time.time() + 7.0
    while True:
        try:
            LOG.info("Trying to connect to WSGI... ")
            r = requests.get(BASE_WSGI_URL)
            if r.status_code == 200 or r.status_code == 404:
                LOG.info("WSGI service started")
                break
        except:
            pass
        if time.time() > timeout:
            assert False, "Timeout"
        time.sleep(0.2)


class WsgiConnection:
    def __init__(self, compo, base_url=BASE_WSGI_URL):
        self.base_url = base_url
        self.composition = compo

    def _cors_headers(self, cors):
        if cors:
            return {
                "Origin": "http://camptocamp.org"
            }
        else:
            return None

    def _check_cors(self, cors, r):
        if cors:
            assert r.headers["Access-Control-Allow-Origin"] == "*"

    def get(self, url, expected_status=200, cors=True):
        """
        get the given URL (relative to the root of WSGI).
        """
        r = requests.get(self.base_url + url, headers=self._cors_headers(cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.text
        finally:
            r.close()

    def get_json(self, url, cors=True):
        """
        get the given URL (relative to the root of WSGI).
        """
        r = requests.get(self.base_url + url, headers=self._cors_headers(cors))
        try:
            check_response(r)
            self._check_cors(cors, r)
            return r.json() if r.status_code != 204 else None
        finally:
            r.close()

    def post(self, url, data, expected_status=200, cors=True):
        """
        POST the given URL (relative to the root of WSGI).
        """
        r = requests.post(self.base_url + url, data=data, headers=self._cors_headers(cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.text
        finally:
            r.close()

    def post_json(self, url, json, expected_status=200, cors=True):
        """
        POST the given URL (relative to the root of WSGI).
        """
        r = requests.post(self.base_url + url, json=json, headers=self._cors_headers(cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.json() if r.status_code != 204 else None
        finally:
            r.close()

    def post_file(self, url, files, expected_status=200, cors=True):
        """
        POST the given URL (relative to the root of WSGI).
        """
        r = requests.post(self.base_url + url, files=files, headers=self._cors_headers(cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.json() if r.status_code != 204 else None
        finally:
            r.close()

    def put_json(self, url, json, expected_status=200, cors=True):
        """
        POST the given URL (relative to the root of WSGI).
        """
        r = requests.put(self.base_url + url, json=json, headers=self._cors_headers(cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.json() if r.status_code != 204 else None
        finally:
            r.close()

    def delete(self, url, expected_status=204, cors=True):
        """
        DELETE the given URL (relative to the root of WSGI).
        """
        r = requests.delete(self.base_url + url, headers=self._cors_headers(cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.json() if r.status_code != 204 else None
        finally:
            r.close()


def check_response(r, expected_status=200):
    assert r.status_code == expected_status, "status=%d\n%s" % (r.status_code, r.text)
