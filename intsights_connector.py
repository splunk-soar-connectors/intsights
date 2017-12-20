# Phantom imports
import phantom.app as phantom
from phantom.app import BaseConnector
from phantom.app import ActionResult

import requests


class IntsightsConnector(BaseConnector):
    # Intsights endpoints
    SERVER = 'https://dashboard.intsights.com'
    LOGIN = SERVER + '/login'
    LOGOUT = SERVER + '/logout'
    SEARCH_IOC = SERVER + '/iocs/search'
    ALERTS = SERVER + '/alerts'

    # Supported actions
    ACTION_ID_TEST_ASSET_CONNECTIVITY = 'test_asset_connectivity'
    ACTION_ID_HUNT_FILE = 'hunt_file'
    ACTION_ID_HUNT_DOMAIN = 'hunt_domain'
    ACTION_ID_HUNT_IP = 'hunt_ip'
    ACTION_ID_HUNT_URL = 'hunt_url'
    ACTION_ID_ON_POLL = 'on_poll'

    def __init__(self):

        super(IntsightsConnector, self).__init__()
        self._session = None
        self._data = {}

    def initialize(self):

        config = self.get_config()

        s = requests.Session()
        s.headers.update({'Accept': 'application/json'})

        self._session = s
        self._data = {'Email': config['email'], 'Password': config['password'], 'Type': ''}

        self._login()

        return phantom.APP_SUCCESS

    def finalize(self):

        self._logout()

        self._session = None
        self._data = None

        return phantom.APP_SUCCESS

    def _login(self):

        self._data['Type'] = 'pass'

        r = self._session.post(self.LOGIN, data=self._data)
        r.raise_for_status()

        self._data['Type'] = ''

        return r

    def _logout(self):

        self._data['Type'] = 'pass'

        r = self._session.post(self.LOGOUT, data=self._data)
        r.raise_for_status()

        self._data['Type'] = ''

        return r

    def _test_asset_connectivity(self):

        return self.set_status_save_progress(phantom.APP_SUCCESS, 'Connection successful')

    def _search_ioc(self, value, action_result):

        self.save_progress('Searching for IOC value: ' + value)

        try:
            r = self._session.get(self.SEARCH_IOC, params={'Value': value})
            r.raise_for_status()
        except requests.HTTPError as e:
            return action_result.set_status(phantom.APP_ERROR, 'IOC search failed', e), None

        r_json = r.json()
        if len(r_json['Data']) == 0:
            r_json['Data'] = [{'Value': value}]

        return True, r_json

    def _hunt_file(self, param):

        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['hash']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'File information retrieved')
        action_result.update_data(results['Data'])

        return action_result.get_status()

    def _hunt_domain(self, param):

        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['domain']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'Domain information retrieved')
        action_result.update_data(results['Data'])

        return action_result.get_status()

    def _hunt_ip(self, param):

        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['ip']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'IP information retrieved')
        action_result.update_data(results['Data'])

        return action_result.get_status()

    def _hunt_url(self, param):

        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['url'].split('://')[1]

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'URL information retrieved')
        action_result.update_data(results['Data'])

        return action_result.get_status()

    def _on_poll(self, param):

        raise NotImplementedError

    def handle_action(self, param):

        ret_val = phantom.APP_ERROR

        action_id = self.get_action_identifier()

        if action_id == self.ACTION_ID_TEST_ASSET_CONNECTIVITY:
            ret_val = self._test_asset_connectivity()
        elif action_id == self.ACTION_ID_HUNT_FILE:
            ret_val = self._hunt_file(param)
        elif action_id == self.ACTION_ID_HUNT_DOMAIN:
            ret_val = self._hunt_domain(param)
        elif action_id == self.ACTION_ID_HUNT_IP:
            ret_val = self._hunt_ip(param)
        elif action_id == self.ACTION_ID_HUNT_URL:
            ret_val = self._hunt_url(param)
        elif action_id == self.ACTION_ID_ON_POLL:
            ret_val = self._on_poll(param)
        else:
            raise ValueError('Action {} is not supported'.format(action_id))

        return ret_val


if __name__ == '__main__':
    import json
    import sys
    # import wingdbstub

    if len(sys.argv) < 2:
        print 'No test json specified as input'
        exit(1)

    with open(sys.argv[1]) as f:

        in_json = f.read()
        in_json = json.loads(in_json)

        print json.dumps(in_json, indent=4)

        connector = IntsightsConnector()
        connector.print_progress_message = True

        ret_val = connector._handle_action(json.dumps(in_json), None)

        print json.dumps(json.loads(ret_val), indent=4)

    exit(0)
