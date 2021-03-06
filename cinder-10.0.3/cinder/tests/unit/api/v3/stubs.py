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

import datetime
import iso8601

from cinder.message import defined_messages
from cinder.tests.unit import fake_constants as fake


FAKE_UUID = fake.OBJECT_ID


def stub_message(id, **kwargs):
    message = {
        'id': id,
        'event_id': defined_messages.EventIds.UNABLE_TO_ALLOCATE,
        'message_level': "ERROR",
        'request_id': FAKE_UUID,
        'updated_at': datetime.datetime(1900, 1, 1, 1, 1, 1,
                                        tzinfo=iso8601.iso8601.Utc()),
        'created_at': datetime.datetime(1900, 1, 1, 1, 1, 1,
                                        tzinfo=iso8601.iso8601.Utc()),
        'expires_at': datetime.datetime(1900, 1, 1, 1, 1, 1,
                                        tzinfo=iso8601.iso8601.Utc()),
    }

    message.update(kwargs)
    return message


def stub_message_get(self, context, message_id):
    return stub_message(message_id)
