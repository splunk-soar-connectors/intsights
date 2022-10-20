# File: intsights_connector.py
#
# Copyright (c) 2019-2022 IntSights Cyber Intelligence Ltd.
#
# This unpublished material is proprietary to IntSights.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of IntSights.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

from urllib.parse import unquote

# Phantom imports
import phantom.app as phantom
import requests
from phantom.app import BaseConnector


class IntSightsConnector(BaseConnector):
    """
    Represent a connector module that implements the actions that are provided by the app.

    IntSightsConnector is a class that is derived from the BaseConnector class.
    """

    # IntSights endpoints
    INTSIGHTS_BASE_URL = 'https://api.ti.insight.rapid7.com/public/v1'
    INTSIGHTS_BASE_URL_V3 = 'https://api.ti.insight.rapid7.com/public/v3'
    INTSIGHTS_SEARCH_IOC_URL = INTSIGHTS_BASE_URL_V3 + '/iocs/ioc-by-value'
    INTSIGHTS_GET_API_VERSION_URL = INTSIGHTS_BASE_URL + '/api/version'
    INTSIGHTS_GET_SOURCES_URL = INTSIGHTS_BASE_URL + '/iocs/sources'
    INTSIGHTS_GET_ALERTS_LIST_URL = INTSIGHTS_BASE_URL + '/data/alerts/alerts-list'
    INTSIGHTS_GET_COMPLETE_ALERT_URL = INTSIGHTS_BASE_URL + '/data/alerts/get-complete-alert/{alert_id}'
    INTSIGHTS_CLOSE_ALERT_URL = INTSIGHTS_BASE_URL + '/data/alerts/close-alert/{alert_id}'
    INTSIGHTS_ALERT_TAKEDOWN_URL = INTSIGHTS_BASE_URL + '/data/alerts/takedown-request/{alert_id}'
    INTSIGHTS_INVESTIGATION_LINK_URL = 'https://dashboard.ti.insight.rapid7.com/#/tip/investigation/?q={ioc}'

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
    INTSIGHTS_CONNECTION_SUCCESSFUL = 'Test Connectivity passed'
    INTSIGHTS_ERROR_NO_CONTENT = 'No data was returned from IntSights'
    INTSIGHTS_ERROR_CONNECTION = 'Error getting data from IntSights. {error}'
    INTSIGHTS_ERROR_AUTH = 'Authentication error'
    INTSIGHTS_ERROR_INIT_SOURCES = 'Failed to initiate sources map. {error}'
    INTSIGHTS_ERROR_CLOSE_ALERT = 'Failed to close alert ID {alert_id}'
    INTSIGHTS_ERROR_TAKEDOWN_ALERT = 'Failed to takedown alert ID {alert_id}'
    PHANTOM_ERROR_SAVE_CONTAINER = 'An error occurred while creating container for IntSights alert ID {alert_id}'
    PHANTOM_ERROR_SAVE_ARTIFACT = 'An error occurred while creating artifact for IntSights alert ID {alert_id}'
    INTSIGHTS_ERR_UNABLE_TO_PARSE_JSON_RESPONSE = "Unable to parse response as JSON. {error}"
    INTSIGHTS_ERR_INVALID_RESPONSE = "Invalid response received from the server while fetching the list of alert ids"

    # Constants relating to 'get_error_message_from_exception'
    ERR_MSG_UNAVAILABLE = "Error message unavailable. Please check the asset configuration and|or action parameters."

    # Constants relating to 'validate_integer'
    INTSIGHTS_VALID_INT_MSG = "Please provide a valid integer value in the '{param}' parameter"
    INTSIGHTS_NON_NEG_NON_ZERO_INT_MSG = "Please provide a valid non-zero positive integer value in '{param}' parameter"
    INTSIGHTS_NON_NEG_INT_MSG = "Please provide a valid non-negative integer value in the '{param}' parameter"

    def __init__(self):
        """Initialize global variables."""
        super(IntSightsConnector, self).__init__()
        self._session = None
        self._sources = None

    def _get_error_message_from_exception(self, e):
        """
        Get appropriate error message from the exception.

        :param e: Exception object
        :return: error message
        """
        error_code = None
        error_msg = self.ERR_MSG_UNAVAILABLE

        try:
            if hasattr(e, "args"):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_msg = e.args[1]
                elif len(e.args) == 1:
                    error_msg = e.args[0]
        except Exception:
            pass

        if not error_code:
            error_text = "Error Message: {}".format(error_msg)
        else:
            error_text = "Error Code: {}. Error Message: {}".format(error_code, error_msg)

        return error_text

    def _validate_integer(self, action_result, parameter, key, allow_zero=False):
        """
        Validate an integer.

        :param action_result: Action result or BaseConnector object
        :param parameter: input parameter
        :param key: input parameter message key
        :allow_zero: whether zero should be considered as valid value or not
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS, integer value of the parameter or None in case of failure
        """
        if parameter is not None:
            try:
                if not float(parameter).is_integer():
                    return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_VALID_INT_MSG.format(param=key)), None

                parameter = int(parameter)
            except Exception:
                return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_VALID_INT_MSG.format(param=key)), None

            if parameter < 0:
                return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_NON_NEG_INT_MSG.format(param=key)), None
            if not allow_zero and parameter == 0:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    self.INTSIGHTS_NON_NEG_NON_ZERO_INT_MSG.format(param=key)
                ), None

        return phantom.APP_SUCCESS, parameter

    def initialize(self):
        """Initialize the global variables with its value and validate it."""
        config = self.get_config()

        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'application/json',
                'X-App-Name': 'Phantom_1.0',
            }
        )

        account_id = config['account_id'].encode("utf8")
        session.auth = requests.auth.HTTPBasicAuth(
            account_id,
            config['api_key'],
        )

        self._session = session

        return phantom.APP_SUCCESS

    def finalize(self):
        """Perform some final operations or clean up operations."""
        self._session = None

        return phantom.APP_SUCCESS

    def _test_asset_connectivity(self):
        self.debug_print('Starting connectivity test')

        action_result = self.add_action_result(phantom.ActionResult())

        try:
            response = self._session.get(self.INTSIGHTS_GET_API_VERSION_URL)
            if response.status_code == 401:
                return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_AUTH)

            response.raise_for_status()
        except requests.HTTPError as e:
            error_msg = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION.format(error=error_msg))
        except Exception as e:
            self.error_print('Something went wrong')
            return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION.format(error=e))

        self.save_progress(self.INTSIGHTS_CONNECTION_SUCCESSFUL)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _init_sources(self, action_result):
        try:
            sources_map = self._session.get(self.INTSIGHTS_GET_SOURCES_URL).json()
            self._sources = {
                value['_id']: value['Name']
                for category in sources_map.values()
                for value in category
            }
            return phantom.APP_SUCCESS
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            self.save_progress(self.INTSIGHTS_ERROR_INIT_SOURCES.format(error=error_msg))
            return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_INIT_SOURCES.format(error=error_msg))

    def _search_ioc(self, value, action_result):

        self.save_progress('Searching for IOC value: ' + value)

        try:
            response = self._session.get(self.INTSIGHTS_SEARCH_IOC_URL, params={'iocValue': value})
            if response.status_code == 204:
                return action_result.set_status(phantom.APP_SUCCESS, self.INTSIGHTS_ERROR_NO_CONTENT), None
            response.raise_for_status()
        except requests.HTTPError as e:
            error_msg = unquote(self._get_error_message_from_exception(e))
            return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION.format(error=error_msg)), None

        try:
            ioc_data = response.json()
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            return action_result.set_status(
                phantom.APP_ERROR,
                self.INTSIGHTS_ERR_UNABLE_TO_PARSE_JSON_RESPONSE.format(error=error_msg)
            ), None

        ioc_data['InvestigationLink'] = self.INTSIGHTS_INVESTIGATION_LINK_URL.format(ioc=value)

        source_name = ''
        if self._sources:
            source_name = self._sources.get(ioc_data.get('SourceID', ""))
        ioc_data['SourceName'] = source_name

        return phantom.APP_SUCCESS, ioc_data

    def _hunt_file(self, param):

        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        ret_val = self._init_sources(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        value = param['hash']

        ret_val, results = self._search_ioc(value, action_result)
        if phantom.is_fail(ret_val) or not results:
            return action_result.get_status()

        action_result.add_data(results)
        return action_result.set_status(phantom.APP_SUCCESS, 'File information retrieved')

    def _hunt_domain(self, param):

        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        ret_val = self._init_sources(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        value = param['domain']

        ret_val, results = self._search_ioc(value, action_result)
        if phantom.is_fail(ret_val) or not results:
            return action_result.get_status()

        action_result.add_data(results)
        return action_result.set_status(phantom.APP_SUCCESS, 'Domain information retrieved')

    def _hunt_ip(self, param):

        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        ret_val = self._init_sources(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        value = param['ip']

        ret_val, results = self._search_ioc(value, action_result)
        if phantom.is_fail(ret_val) or not results:
            return action_result.get_status()

        action_result.add_data(results)
        return action_result.set_status(phantom.APP_SUCCESS, 'IP information retrieved')

    def _hunt_url(self, param):

        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        ret_val = self._init_sources(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        value = param['url']

        ret_val, results = self._search_ioc(value, action_result)
        if phantom.is_fail(ret_val) or not results:
            return action_result.get_status()

        action_result.add_data(results)
        return action_result.set_status(phantom.APP_SUCCESS, 'URL information retrieved')

    def _get_artifact(self, alert):
        cef = {
            'Subtype': alert.get('Details', {}).get('SubType'),
        }

        assets = [asset.get('Value') for asset in alert.get('Assets')]
        if assets:
            cef['Assets'] = assets

        tags = [tag.get('Name') for tag in alert.get('Details', {}).get('Tags')]
        if tags:
            cef['Tags'] = tags

        source_date = alert.get('Details', {}).get('Source', {}).get('Date', '')
        if source_date:
            cef['Source Date'] = source_date

        artifact = {
            'label': 'IntSights Alert',
            'name': alert.get('Details', {}).get('Title'),
            'description': alert.get('Details', {}).get('Description'),
            'type': alert.get('Details', {}).get('Type'),
            'severity': alert.get('Details', {}).get('Severity'),
            'start_time': alert.get('FoundDate'),
            'source_data_identifier': alert.get('_id'),
            'data': alert,
            'cef': cef,
        }

        return artifact

    def _get_alert_ids(self, param, action_result):
        try:
            # start time is considered as last 10 days
            start_time = param['end_time'] - (432000000 * 2)
            params = {
                'foundDateFrom': start_time,
                'foundDateTo': param['end_time'],
            }
            response = self._session.get(self.INTSIGHTS_GET_ALERTS_LIST_URL, params=params)
            if response.status_code == 204:
                return action_result.set_status(phantom.APP_SUCCESS), []

            response.raise_for_status()
            try:
                alert_ids = response.json()
                if not isinstance(alert_ids, list):
                    self.debug_print("{}. Alert IDs: {}".format(self.INTSIGHTS_ERR_INVALID_RESPONSE, alert_ids))
                    return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERR_INVALID_RESPONSE), []
            except Exception as e:
                error_msg = self._get_error_message_from_exception(e)
                return action_result.set_status(
                    phantom.APP_ERROR,
                    self.INTSIGHTS_ERR_UNABLE_TO_PARSE_JSON_RESPONSE.format(error=error_msg)
                ), []

        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CONNECTION.format(error=error_msg)), []

        return phantom.APP_SUCCESS, alert_ids

    def _on_poll(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        ret_val, alert_ids = self._get_alert_ids(param, action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        max_results = param.get("container_count", len(alert_ids))

        if max_results < len(alert_ids):
            alert_ids = alert_ids[:max_results]

        try:
            for alert_id in alert_ids:
                alert = self._session.get(self.INTSIGHTS_GET_COMPLETE_ALERT_URL.format(alert_id=alert_id)).json()
                artifact = self._get_artifact(alert)
                container = {
                    'name': '{title} - {id}'.format(title=alert.get('Details', {}).get('Title'), id=alert_id),
                    'description': 'Unresolved IntSights Alert',
                    'severity': alert.get('Details', {}).get('Severity'),
                    'source_data_identifier': alert_id,
                }

                status, msg, container_id_ = self.save_container(container)

                if phantom.is_fail(status):
                    self.save_progress(self.PHANTOM_ERROR_SAVE_CONTAINER.format(alert_id=alert_id))
                    self.debug_print('Failed to save container', dump_object=container)
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        self.PHANTOM_ERROR_SAVE_CONTAINER.format(alert_id=alert_id)
                    )

                artifact['container_id'] = container_id_
                status, message, _ = self.save_artifacts([artifact])

                if phantom.is_fail(status):
                    self.save_progress(self.PHANTOM_ERROR_SAVE_ARTIFACT.format(alert_id=alert_id))
                    self.debug_print('Failed to save artifact', dump_object=artifact)
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        self.PHANTOM_ERROR_SAVE_ARTIFACT.format(alert_id=alert_id)
                    )

            return action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, 'Failed to get data {}'.format(error_msg))

    def _get_closure_json(self, param, action_result):
        closure_json = dict()

        closure_json['Reason'] = param['reason']

        free_text = param.get('free_text')
        if free_text:
            closure_json['FreeText'] = free_text

        is_hidden = param.get('is_hidden')
        if is_hidden:
            closure_json['IsHidden'] = is_hidden

        alert_rate = param.get('rate')

        if alert_rate is not None:

            # Integer validation for 'rate' parameter
            ret_val, alert_rate = self._validate_integer(action_result, alert_rate, 'rate', True)
            if phantom.is_fail(ret_val):
                return action_result.get_status(), {}

            closure_json['Rate'] = alert_rate

        return phantom.APP_SUCCESS, closure_json

    def _close_alert(self, param):
        self.debug_print('Starting close alert')

        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        alert_id = param['alert_id']
        ret_val, closure_json = self._get_closure_json(param, action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        try:
            response = self._session.patch(self.INTSIGHTS_CLOSE_ALERT_URL.format(alert_id=alert_id), json=closure_json)
            if response.status_code in [400, 403, 500]:
                return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_CLOSE_ALERT.format(alert_id=alert_id))
            response.raise_for_status()
            return action_result.set_status(phantom.APP_SUCCESS, "Successfully closed the alert")
        except Exception as e:
            self.error_print('Something went wrong')
            error_msg = unquote(self._get_error_message_from_exception(e))
            msg = "{}. {}".format(self.INTSIGHTS_ERROR_TAKEDOWN_ALERT.format(alert_id=alert_id), error_msg)
            return action_result.set_status(phantom.APP_ERROR, msg)

    def _takedown_request(self, param):
        self.debug_print('Starting takedown request')
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        alert_id = param['alert_id']

        try:
            response = self._session.patch(self.INTSIGHTS_ALERT_TAKEDOWN_URL.format(alert_id=alert_id))
            if response.status_code in [400, 403, 500]:
                return action_result.set_status(phantom.APP_ERROR, self.INTSIGHTS_ERROR_TAKEDOWN_ALERT.format(alert_id=alert_id))
            response.raise_for_status()
            return action_result.set_status(phantom.APP_SUCCESS, "Takedown request successfully executed")
        except Exception as e:
            self.error_print('Something went wrong')
            error_msg = unquote(self._get_error_message_from_exception(e))
            msg = "{}. {}".format(self.INTSIGHTS_ERROR_TAKEDOWN_ALERT.format(alert_id=alert_id), error_msg)
            return action_result.set_status(phantom.APP_ERROR, msg)

    def handle_action(self, param):
        """Get current action identifier and call member function of its own to handle the action."""
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
        sys.exit(1)

    with open(sys.argv[1]) as f:

        in_json = f.read()
        in_json = json.loads(in_json)

        print(json.dumps(in_json, indent=4))

        connector = IntSightsConnector()
        connector.print_progress_message = True

        ret_val = connector._handle_action(json.dumps(in_json), None)

        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)
