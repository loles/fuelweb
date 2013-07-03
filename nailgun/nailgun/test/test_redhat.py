#    Copyright 2013 Mirantis, Inc.
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

import json
from paste.fixture import TestApp

from nailgun.api.models import Release
from nailgun.settings import settings


from nailgun.test.base import BaseHandlers
from nailgun.test.base import reverse


class TestHandlers(BaseHandlers):
    def test_redhat_account_handler(self):
        resp = self.app.post(
            reverse('RedHatAccountHandler'),
            json.dumps({'license_type': 'rhsm',
                        'username': 'user',
                        'password': 'password',
                        'release_id': 1}),
            headers=self.default_headers)
        self.assertEquals(resp.status, 200)

    def test_redhat_account_invalid_data_handler(self):
        resp = self.app.post(
            reverse('RedHatAccountHandler'),
            json.dumps({'username': 'user',
                        'password': 'password'}),
            headers=self.default_headers,
            expect_errors=True)
        self.assertEquals(resp.status, 400)

    def test_redhat_account_validation_success(self):
        resp = self.app.post(
            reverse('RedHatAccountHandler'),
            json.dumps({'license_type': 'rhsm',
                        'username': 'rheltest',
                        'password': 'password',
                        'release_id': 1}),
            headers=self.default_headers)
        self.assertEquals(resp.status, 200)

    def test_redhat_account_validation_failure(self):
        resp = self.app.post(
            reverse('RedHatAccountHandler'),
            json.dumps({'license_type': 'rhsm',
                        'username': 'some_user',
                        'password': 'password',
                        'release_id': 1}),
            headers=self.default_headers,
            expect_errors=True)
        self.assertEquals(resp.status, 400)
