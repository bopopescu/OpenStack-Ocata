# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import mock

from magnum.api.controllers.v1 import quota as api_quota
from magnum.tests import base
from magnum.tests.unit.api import base as api_base
from magnum.tests.unit.api import utils as apiutils
from magnum.tests.unit.objects import utils as obj_utils


class TestQuotaObject(base.TestCase):
    def test_quota_init(self):
        quota_dict = apiutils.quota_post_data()
        del quota_dict['hard_limit']
        quota = api_quota.Quota(**quota_dict)
        self.assertEqual(1, quota.hard_limit)


class TestQuota(api_base.FunctionalTest):
    _quota_attrs = ("project_id", "resource", "hard_limit")

    def setUp(self):
        super(TestQuota, self).setUp()

    def test_empty(self):
        response = self.get_json('/quotas')
        self.assertEqual([], response['quotas'])

    def test_one(self):
        quota = obj_utils.create_test_quota(self.context)
        response = self.get_json('/quotas')
        self.assertEqual(quota.project_id, response['quotas'][0]["project_id"])
        self._verify_attrs(self._quota_attrs, response['quotas'][0])

    def test_get_one(self):
        quota = obj_utils.create_test_quota(self.context)
        response = self.get_json('/quotas/%s/%s' % (quota['project_id'],
                                                    quota['resource']))
        self.assertEqual(quota.project_id, response['project_id'])
        self.assertEqual(quota.resource, response['resource'])

    def test_get_one_not_found(self):
        response = self.get_json(
            '/quotas/fake_project/invalid_res',
            expect_errors=True)
        self.assertEqual(404, response.status_int)
        self.assertEqual('application/json', response.content_type)
        self.assertTrue(response.json['errors'])

    def test_get_one_not_authorized(self):
        obj_utils.create_test_quota(self.context)
        response = self.get_json(
            '/quotas/invalid_proj/invalid_res',
            expect_errors=True)
        self.assertEqual(403, response.status_int)
        self.assertEqual('application/json', response.content_type)
        self.assertTrue(response.json['errors'])

    @mock.patch("magnum.common.policy.enforce")
    @mock.patch("magnum.common.context.make_context")
    def test_get_all_admin_all_tenants(self, mock_context, mock_policy):
        mock_context.return_value = self.context
        quota_list = []
        for i in range(4):
            quota = obj_utils.create_test_quota(self.context,
                                                project_id="proj-id-"+str(i))
            quota_list.append(quota)

        self.context.is_admin = True
        response = self.get_json('/quotas?all_tenants=True')
        self.assertEqual(4, len(response['quotas']))
        expected = [r.project_id for r in quota_list]
        res_proj_ids = [r['project_id'] for r in response['quotas']]
        self.assertEqual(sorted(expected), sorted(res_proj_ids))

    @mock.patch("magnum.common.policy.enforce")
    @mock.patch("magnum.common.context.make_context")
    def test_get_all_admin_not_all_tenants(self, mock_context, mock_policy):
        mock_context.return_value = self.context
        quota_list = []
        for i in range(4):
            quota = obj_utils.create_test_quota(self.context,
                                                project_id="proj-id-"+str(i))
            quota_list.append(quota)

        self.context.is_admin = True
        self.context.project_id = 'proj-id-1'
        response = self.get_json('/quotas')
        self.assertEqual(1, len(response['quotas']))
        self.assertEqual('proj-id-1', response['quotas'][0]['project_id'])

    @mock.patch("magnum.common.policy.enforce")
    @mock.patch("magnum.common.context.make_context")
    def test_get_all_with_pagination_limit(self, mock_context,
                                           mock_policy):
        mock_context.return_value = self.context
        quota_list = []
        for i in range(4):
            quota = obj_utils.create_test_quota(self.context,
                                                project_id="proj-id-"+str(i))
            quota_list.append(quota)

        self.context.is_admin = True
        response = self.get_json('/quotas?limit=2&all_tenants=True')
        self.assertEqual(2, len(response['quotas']))
        expected = [r.project_id for r in quota_list[:2]]
        res_proj_ids = [r['project_id'] for r in response['quotas']]
        self.assertEqual(sorted(expected), sorted(res_proj_ids))
        self.assertTrue('http://localhost/v1/quotas?' in response['next'])
        self.assertTrue('sort_key=id' in response['next'])
        self.assertTrue('sort_dir=asc' in response['next'])
        self.assertTrue('limit=2' in response['next'])
        self.assertTrue('marker=%s' % quota_list[1].id in response['next'])

    @mock.patch("magnum.common.policy.enforce")
    @mock.patch("magnum.common.context.make_context")
    def test_get_all_admin_all_with_pagination_marker(self, mock_context,
                                                      mock_policy):
        mock_context.return_value = self.context
        quota_list = []
        for i in range(4):
            quota = obj_utils.create_test_quota(self.context,
                                                project_id="proj-id-"+str(i))
            quota_list.append(quota)

        self.context.is_admin = True
        response = self.get_json('/quotas?limit=3&marker=%s&all_tenants=True'
                                 % quota_list[2].id)
        self.assertEqual(1, len(response['quotas']))
        self.assertEqual(quota_list[-1].project_id,
                         response['quotas'][0]['project_id'])

    def test_get_all_non_admin(self):
        quota_list = []
        for i in range(4):
            quota = obj_utils.create_test_quota(self.context,
                                                project_id="proj-id-"+str(i))
            quota_list.append(quota)

        headers = {'X-Project-Id': 'proj-id-2'}
        response = self.get_json('/quotas', headers=headers)
        self.assertEqual(1, len(response['quotas']))
        self.assertEqual('proj-id-2', response['quotas'][0]['project_id'])

    def test_create_quota(self):
        quota_dict = apiutils.quota_post_data()
        response = self.post_json('/quotas', quota_dict)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(201, response.status_int)
        self.assertEqual(quota_dict['project_id'], response.json['project_id'])

    def test_create_quota_invalid_resource(self):
        quota_dict = apiutils.quota_post_data()
        quota_dict['resource'] = 'invalid-res'
        response = self.post_json('/quotas', quota_dict, expect_errors=True)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(400, response.status_int)
        self.assertTrue(response.json['errors'])

    def test_create_quota_invalid_hard_limit(self):
        quota_dict = apiutils.quota_post_data()
        quota_dict['hard_limit'] = -10
        response = self.post_json('/quotas', quota_dict, expect_errors=True)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(400, response.status_int)
        self.assertTrue(response.json['errors'])

    def test_create_quota_no_project_id(self):
        quota_dict = apiutils.quota_post_data()
        del quota_dict['project_id']
        response = self.post_json('/quotas', quota_dict, expect_errors=True)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(400, response.status_int)
        self.assertTrue(response.json['errors'])

    def test_patch_quota(self):
        quota_dict = apiutils.quota_post_data(hard_limit=5)
        response = self.post_json('/quotas', quota_dict)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(201, response.status_int)
        self.assertEqual(quota_dict['project_id'], response.json['project_id'])
        self.assertEqual(5, response.json['hard_limit'])

        quota_dict['hard_limit'] = 20
        response = self.patch_json('/quotas', quota_dict)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(202, response.status_int)
        self.assertEqual(20, response.json['hard_limit'])

    def test_patch_quota_not_found(self):
        quota_dict = apiutils.quota_post_data()
        response = self.post_json('/quotas', quota_dict)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(201, response.status_int)

        # update quota with non-existing project id
        update_dict = {'project_id': 'not-found',
                       'hard_limit': 20,
                       'resource': 'Cluster'}
        response = self.patch_json('/quotas', update_dict, expect_errors=True)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(404, response.status_int)
        self.assertTrue(response.json['errors'])

    def test_delete_quota(self):
        quota_dict = apiutils.quota_post_data()
        response = self.post_json('/quotas', quota_dict)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(201, response.status_int)

        project_id = quota_dict['project_id']
        resource = quota_dict['resource']
        # delete quota
        self.delete('/quotas/%s/%s' % (project_id, resource))

        # now check that quota does not exist
        response = self.get_json(
            '/quotas/%s/%s' % (project_id, resource),
            expect_errors=True)
        self.assertEqual(404, response.status_int)
        self.assertEqual('application/json', response.content_type)
        self.assertTrue(response.json['errors'])
