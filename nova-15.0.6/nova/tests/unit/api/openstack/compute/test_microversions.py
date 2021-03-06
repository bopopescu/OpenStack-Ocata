# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from oslo_serialization import jsonutils

from nova.api.openstack import api_version_request as api_version
from nova import test
from nova.tests.unit.api.openstack import fakes


class LegacyMicroversionsTest(test.NoDBTestCase):

    header_name = 'X-OpenStack-Nova-API-Version'

    def _test_microversions(self, app, req, ret_code, ret_header=None):
        req.environ['CONTENT_TYPE'] = "application/json"

        res = req.get_response(app)
        self.assertEqual(ret_code, res.status_int)
        if ret_header:
            if 'nova' not in self.header_name.lower():
                ret_header = 'compute %s' % ret_header
            self.assertEqual(ret_header,
                             res.headers[self.header_name])
        return res

    def _make_header(self, req_header):
        if 'nova' in self.header_name.lower():
            headers = {self.header_name: req_header}
        else:
            headers = {self.header_name: 'compute %s' % req_header}
        return headers

    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_no_header(self, mock_namespace):
        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('val', resp_json['param'])

    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_return_header(self, mock_namespace):
        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('val', resp_json['param'])
        if 'nova' in self.header_name.lower():
            self.assertEqual("2.1", res.headers[self.header_name])
        else:
            self.assertEqual("compute 2.1", res.headers[self.header_name])
        self.assertIn(self.header_name, res.headers.getall('Vary'))

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_return_header_non_default(self, mock_namespace,
                                                        mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("2.3")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        req.headers = self._make_header('2.3')
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('val2', resp_json['param'])
        if 'nova' in self.header_name.lower():
            self.assertEqual("2.3", res.headers[self.header_name])
        else:
            self.assertEqual("compute 2.3", res.headers[self.header_name])
        self.assertIn(self.header_name, res.headers.getall('Vary'))

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_return_header_fault(self, mock_namespace,
                                                        mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.0")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        req.headers = self._make_header('3.0')
        res = req.get_response(app)
        self.assertEqual(400, res.status_int)
        if 'nova' in self.header_name.lower():
            self.assertEqual("3.0", res.headers[self.header_name])
        else:
            self.assertEqual("compute 3.0", res.headers[self.header_name])
        self.assertIn(self.header_name, res.headers.getall('Vary'))

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def _check_microversion_response(self, url, req_version, resp_param,
                                     mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest('2.3')

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank(url)
        req.headers = self._make_header(req_version)
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual(resp_param, resp_json['param'])

    def test_microversions_with_header(self):
        self._check_microversion_response('/v2/fake/microversions',
                                          '2.3', 'val2')

    def test_microversions_with_header_exact_match(self):
        self._check_microversion_response('/v2/fake/microversions',
                                          '2.2', 'val2')

    def test_microversions2_no_2_1_version(self):
        self._check_microversion_response('/v2/fake/microversions2',
                                          '2.3', 'controller2_val1')

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions2_later_version(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.1")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = self._make_header('3.0')
        res = req.get_response(app)
        self.assertEqual(202, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('controller2_val2', resp_json['param'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions2_version_too_high(self, mock_namespace,
                                             mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.5")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {self.header_name: '3.2'}
        res = req.get_response(app)
        self.assertEqual(404, res.status_int)

    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions2_version_too_low(self, mock_namespace):
        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {self.header_name: '2.1'}
        res = req.get_response(app)
        self.assertEqual(404, res.status_int)

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_global_version_too_high(self, mock_namespace,
                                                   mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.5")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = self._make_header('3.7')
        res = req.get_response(app)
        self.assertEqual(406, res.status_int)
        res_json = jsonutils.loads(res.body)
        self.assertEqual("Version 3.7 is not supported by the API. "
                         "Minimum is 2.1 and maximum is 3.5.",
                         res_json['computeFault']['message'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_schema(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.3")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions3')
        req.method = 'POST'
        req.headers = self._make_header('2.2')
        req.environ['CONTENT_TYPE'] = "application/json"
        req.body = jsonutils.dump_as_bytes({'dummy': {'val': 'foo'}})

        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('create_val1', resp_json['param'])
        if 'nova' in self.header_name.lower():
            self.assertEqual("2.2", res.headers[self.header_name])
        else:
            self.assertEqual("compute 2.2", res.headers[self.header_name])
        self.assertIn(self.header_name, res.headers.getall('Vary'))

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_schema_fail(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.3")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions3')
        req.method = 'POST'
        req.headers = {self.header_name: '2.2'}
        req.environ['CONTENT_TYPE'] = "application/json"
        req.body = jsonutils.dump_as_bytes({'dummy': {'invalid_param': 'foo'}})

        res = req.get_response(app)
        self.assertEqual(400, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertTrue(resp_json['badRequest']['message'].startswith(
            "Invalid input for field/attribute dummy."))

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_schema_out_of_version_check(self, mock_namespace,
                                                       mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.3")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions3/1')
        req.method = 'PUT'
        req.headers = self._make_header('2.2')
        req.body = jsonutils.dump_as_bytes({'dummy': {'inv_val': 'foo'}})
        req.environ['CONTENT_TYPE'] = "application/json"

        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('update_val1', resp_json['param'])
        if 'nova' in self.header_name.lower():
            self.assertEqual("2.2", res.headers[self.header_name])
        else:
            self.assertEqual("compute 2.2", res.headers[self.header_name])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_microversions_schema_second_version(self, mock_namespace,
                                                       mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.3")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions3/1')
        req.headers = self._make_header('2.10')
        req.environ['CONTENT_TYPE'] = "application/json"
        req.method = 'PUT'
        req.body = jsonutils.dump_as_bytes({'dummy': {'val2': 'foo'}})

        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('update_val1', resp_json['param'])
        if 'nova' in self.header_name.lower():
            self.assertEqual("2.10", res.headers[self.header_name])
        else:
            self.assertEqual("compute 2.10", res.headers[self.header_name])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def _test_microversions_inner_function(self, version, expected_resp,
                                           mock_namespace,
                                           mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("2.2")
        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions4')
        req.headers = self._make_header(version)
        req.environ['CONTENT_TYPE'] = "application/json"
        req.method = 'POST'

        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual(expected_resp, resp_json['param'])
        if 'nova' not in self.header_name.lower():
            version = 'compute %s' % version
        self.assertEqual(version, res.headers[self.header_name])

    def test_microversions_inner_function_v22(self):
        self._test_microversions_inner_function('2.2', 'controller4_val2')

    def test_microversions_inner_function_v21(self):
        self._test_microversions_inner_function('2.1', 'controller4_val1')

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def test_with_extends_decorator(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest('2.4')

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions5/item')
        req.headers = {'X-OpenStack-Nova-API-Version': '2.4'}
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)

        expected_res = {
            "extend_ctrlr2": "val_2",
            "extend_ctrlr1": "val_1",
            "base_param": "base_val"}

        resp_json = jsonutils.loads(res.body)
        for param in resp_json:
            self.assertIn(param, expected_res)
            self.assertEqual(expected_res[param], resp_json[param])
        self.assertEqual(3, len(resp_json))

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v21.test_extensions')
    def _test_microversions_actions(self, ret_code, ret_header, req_header,
                                    mock_namespace,
                                    mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("2.3")

        app = fakes.wsgi_app_v21()
        req = fakes.HTTPRequest.blank('/v2/fake/microversions3/1/action')
        if req_header:
            req.headers = self._make_header(req_header)
        req.method = 'POST'
        req.body = jsonutils.dump_as_bytes({'foo': None})

        res = self._test_microversions(app, req, ret_code,
                                       ret_header=ret_header)
        if ret_code == 202:
            resp_json = jsonutils.loads(res.body)
            self.assertEqual({'foo': 'bar'}, resp_json)

    def test_microversions_actions(self):
        self._test_microversions_actions(202, "2.1", "2.1")

    def test_microversions_actions_too_high(self):
        self._test_microversions_actions(404, "2.3", "2.3")

    def test_microversions_actions_no_header(self):
        self._test_microversions_actions(202, "2.1", None)


class MicroversionsTest(LegacyMicroversionsTest):

    header_name = 'OpenStack-API-Version'
