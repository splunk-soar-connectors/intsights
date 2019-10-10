import requests

# Phantom imports
import phantom.app as phantom
from phantom.app import BaseConnector
from phantom.app import ActionResult


class IntSightsConnector(BaseConnector):
    # IntSights endpoints
    INTSIGHTS_BASE_URL = 'https://api.intsights.com/public/v1'
    INTSIGHTS_SEARCH_IOC_URL = INTSIGHTS_BASE_URL + '/iocs/ioc-by-value'
    INTSIGHTS_GET_API_VERSION_URL = INTSIGHTS_BASE_URL + '/api/version'
    INTSIGHTS_GET_SOURCES_URL = INTSIGHTS_BASE_URL + '/iocs/sources'
    INTSIGHTS_GET_ALERTS_LIST_URL = INTSIGHTS_BASE_URL + '/data/alerts/alerts-list'
    INTSIGHTS_GET_COMPLETE_ALERT_URL = INTSIGHTS_BASE_URL + '/data/alerts/get-complete-alert/{alert_id}'
    INTSIGHTS_CLOSE_ALERT_URL = INTSIGHTS_BASE_URL + '/data/alerts/close-alert/{alert_id}'
    INTSIGHTS_ALERT_TAKEDOWN_URL = INTSIGHTS_BASE_URL + '/data/alerts/takedown-request/{alert_id}'
    INTSIGHTS_INVESTIGATION_LINK_URL = 'https://dashboard.intsights.com/#/tip/investigation/?q={ioc}'

    # Supported actions
    ACTION_ID_TEST_ASSET_CONNECTIVITY = 'test_asset_connectivity'
    ACTION_ID_HUNT_FILE = 'hunt_file'
    ACTION_ID_HUNT_DOMAIN = 'hunt_domain'
    ACTION_ID_HUNT_IP = 'hunt_ip'
    ACTION_ID_HUNT_URL = 'hunt_url'
    ACTION_ID_ON_POLL = 'on_poll'
    ACTION_ID_CLOSE_ALERT = 'close_alert'
    ACTION_ID_TAKEDOWN_REQUEST = 'takedown_request'

    # Messages
    INTSIGHTS_CONNECTION_SUCCESSFUL = 'Connection successful'
    INTSIGHTS_ERROR_NO_CONTENT = 'No data was returned from IntSights'
    INTSIGHTS_ERROR_CONNECTION = 'Error getting data from IntSights'
    INTSIGHTS_ERROR_AUTH = 'Authentication error'
    INTSIGHTS_ERROR_INIT_SOURCES = 'Failed to initiate sources map'
    INTSIGHTS_ERROR_CLOSE_ALERT = 'Failed to close alert ID {alert_id}'
    INTSIGHTS_ERROR_TAKEDOWN_ALERT = 'Failed to takedown alert ID {alert_id}'
    PHANTOM_ERROR_SAVE_CONTAINER = 'An error occured while creating container for IntSights alert ID {alert_id}'

    def __init__(self):

        super(IntSightsConnector, self).__init__()
        self._session = None
        self._sources = None

    def initialize(self):

        config = self.get_config()

        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'application/json',
                'X-App-Name': 'Phantom_1.0',
            }
        )
        session.auth = requests.auth.HTTPBasicAuth(
            config['account_id'],
            config['api_key'],
        )

        self._session = session

        return phantom.APP_SUCCESS

    def finalize(self):
        self._session = None

        return phantom.APP_SUCCESS

    def _test_asset_connectivity(self):
        try:
            response = self._session.get(self.INTSIGHTS_GET_API_VERSION_URL)
            if response.status_code == 401:
                return self.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_AUTH)

            response.raise_for_status()
        except requests.HTTPError as e:
            return self.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION, e)

        return self.set_status_save_progress(phantom.APP_SUCCESS, self.INTSIGHTS_CONNECTION_SUCCESSFUL)

    def _init_sources(self):
        try:
            sources_map = self._session.get(self.INTSIGHTS_GET_SOURCES_URL).json()
            self._sources = {
                value['_id']: value['Name']
                for category in sources_map.values()
                for value in category
            }
        except Exception:
            self.save_progress(self.INTSIGHTS_ERROR_INIT_SOURCES)

    def _search_ioc(self, value, action_result):

        self.save_progress('Searching for IOC value: ' + value)

        try:
            response = self._session.get(self.INTSIGHTS_SEARCH_IOC_URL, params={'iocValue': value})
            if response.status_code == 204:
                return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_NO_CONTENT), None
            response.raise_for_status()
        except requests.HTTPError as e:
            return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION, e), None

        ioc_data = response.json()
        ioc_data['InvestigationLink'] = self.INTSIGHTS_INVESTIGATION_LINK_URL.format(ioc=value)

        source_name = ''
        if self._sources:
            source_name = self._sources[ioc_data['SourceID']]
        ioc_data['SourceName'] = source_name

        return True, ioc_data

    def _hunt_file(self, param):

        self._init_sources()
        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['hash']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'File information retrieved')
        action_result.add_data(results)

        return action_result.get_status()

    def _hunt_domain(self, param):

        self._init_sources()
        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['domain']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'Domain information retrieved')
        action_result.add_data(results)

        return action_result.get_status()

    def _hunt_ip(self, param):

        self._init_sources()
        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['ip']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'IP information retrieved')
        action_result.add_data(results)

        return action_result.get_status()

    def _hunt_url(self, param):

        self._init_sources()
        action_result = ActionResult()
        self.add_action_result(action_result)

        value = param['url']

        ok, results = self._search_ioc(value, action_result)
        if not ok:
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, 'URL information retrieved')
        action_result.add_data(results)

        return action_result.get_status()

    def _get_artifact(self, alert):
        cef = {
            'Subtype': alert['Details']['SubType'],
        }

        assets = [ asset['Value'] for asset in alert['Assets'] ]
        if assets:
            cef['Assets'] = assets

        tags = [ tag['Name'] for tag in alert['Details']['Tags'] ]
        if tags:
            cef['Tags'] = tags

        source_date = alert['Details']['Source'].get('Date', '')
        if source_date:
            cef['Source Date'] = source_date

        artifact = {
            'label': 'IntSights Alert',
            'name': alert['Details']['Title'],
            'description': alert['Details']['Description'],
            'type': alert['Details']['Type'],
            'severity': alert['Details']['Severity'],
            'start_time': alert['FoundDate'],
            'source_data_identifier': alert['_id'],
            'data': alert,
            'cef': cef,
        }

        return artifact

    def _get_alert_ids(self, param, action_result):
        try:
            params = {
                'foundDateFrom': param['start_time'],
                'foundDateTo': param['end_time'],
            }
            response = self._session.get(self.INTSIGHTS_GET_ALERTS_LIST_URL, params=params)
            if response.status_code == 204:
                action_result.set_status(phantom.APP_SUCCESS)
                return []

            response.raise_for_status()
            alert_ids = response.json()
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION, e)
            return []

        return alert_ids

    def _on_poll(self, param):
        action_result = ActionResult()

        alert_ids = self._get_alert_ids(param, action_result)

        try:
            for alert_id in alert_ids:
                alert = self._session.get(self.INTSIGHTS_GET_COMPLETE_ALERT_URL.format(alert_id=alert_id)).json()
                artifact = self._get_artifact(alert)
                container = {
                    'name': '{title} - {id}'.format(title=alert['Details']['Title'], id=alert_id),
                    'description': 'Unresolved IntSights Alert',
                    'severity': alert['Details']['Severity'],
                    'source_data_identifier': alert_id,
                    'artifacts': [ artifact ],
                }

                status, msg, container_id_ = self.save_container(container)

                if phantom.is_fail(status):
                    self.save_progress(self.PHANTOM_ERROR_SAVE_CONTAINER.format(alert_id=alert_id))
                    self.debug_print('Failed to save container', dump_object=container)

            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, 'Failed to get data', e)

        self.add_action_result(action_result)
        return action_result.get_status()

    def _get_closure_json(self, param):
        closure_json = dict()

        closure_json['Reason'] = param['reason']

        free_text = param.get('free_text')
        if free_text:
            closure_json['FreeText'] = free_text

        is_hidden = param.get('is_hidden')
        if is_hidden:
            closure_json['IsHidden'] = is_hidden

        alert_rate = param.get('rate')
        if alert_rate:
            closure_json['Rate'] = alert_rate

        return closure_json

    def _close_alert(self, param):
        action_result = ActionResult()

        alert_id = param['alert_id']
        closure_json = self._get_closure_json(param)

        try:
            response = self._session.patch(self.INTSIGHTS_CLOSE_ALERT_URL.format(alert_id=alert_id), json=closure_json)
            if response.status_code in [400, 403, 500]:
               raise Exception(response.text)
            response.raise_for_status()
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CLOSE_ALERT.format(alert_id=alert_id), e)

        self.add_action_result(action_result)
        return action_result.get_status()

    def _takedown_request(self, param):
        action_result = ActionResult()
        alert_id = param['alert_id']

        try:
            response = self._session.patch(self.INTSIGHTS_ALERT_TAKEDOWN_URL.format(alert_id=alert_id))
            if response.status_code in [400, 403, 500]:
               raise Exception(response.text)
            response.raise_for_status()
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_TAKEDOWN_ALERT.format(alert_id=alert_id), e)

        self.add_action_result(action_result)
        return action_result.get_status()

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
        elif action_id == self.ACTION_ID_CLOSE_ALERT:
            ret_val = self._close_alert(param)
        elif action_id == self.ACTION_ID_TAKEDOWN_REQUEST:
            ret_val = self._takedown_request(param)
        else:
            raise ValueError('Action {} is not supported'.format(action_id))

        return ret_val


if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) < 2:
        print('No test json specified as input')
        exit(1)

    with open(sys.argv[1]) as f:

        in_json = f.read()
        in_json = json.loads(in_json)

        print(json.dumps(in_json, indent=4))

        connector = IntSightsConnector()
        connector.print_progress_message = True

        ret_val = connector._handle_action(json.dumps(in_json), None)

        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)
