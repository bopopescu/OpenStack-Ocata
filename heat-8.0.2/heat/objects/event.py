# Copyright 2014 Intel Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Event object."""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from heat.common import identifier
from heat.db.sqlalchemy import api as db_api
from heat.objects import base as heat_base
from heat.objects import resource_properties_data as rpd


class Event(
        heat_base.HeatObject,
        base.VersionedObjectDictCompat,
):
    fields = {
        'id': fields.IntegerField(),
        'stack_id': fields.StringField(),
        'uuid': fields.StringField(),
        'resource_action': fields.StringField(nullable=True),
        'resource_status': fields.StringField(nullable=True),
        'resource_name': fields.StringField(nullable=True),
        'physical_resource_id': fields.StringField(nullable=True),
        'resource_status_reason': fields.StringField(nullable=True),
        'resource_type': fields.StringField(nullable=True),
        'rsrc_prop_data': fields.ObjectField(
            rpd.ResourcePropertiesData),
        'created_at': fields.DateTimeField(read_only=True),
        'updated_at': fields.DateTimeField(nullable=True),
    }

    @staticmethod
    def _from_db_object(context, event, db_event):
        for field in event.fields:
                event[field] = db_event[field]
        if db_event['rsrc_prop_data']:
            event['rsrc_prop_data'] = \
                rpd.ResourcePropertiesData._from_db_object(
                    rpd.ResourcePropertiesData(context), context,
                    db_event['rsrc_prop_data'])
            event._resource_properties = event['rsrc_prop_data'].data
        else:
            event._resource_properties = db_event['resource_properties'] or {}
        event._context = context
        event.obj_reset_changes()
        return event

    @property
    def resource_properties(self):
        return self._resource_properties

    @classmethod
    def get_by_id(cls, context, event_id):
        db_event = db_api.event_get(context, event_id)
        return cls._from_db_object(context, cls(context), db_event)

    @classmethod
    def get_all(cls, context):
        return [cls._from_db_object(context, cls(), db_event)
                for db_event in db_api.event_get_all(context)]

    @classmethod
    def get_all_by_tenant(cls, context, **kwargs):
        return [cls._from_db_object(context, cls(), db_event)
                for db_event in db_api.event_get_all_by_tenant(context,
                                                               **kwargs)]

    @classmethod
    def get_all_by_stack(cls, context, stack_id, **kwargs):
        return [cls._from_db_object(context, cls(), db_event)
                for db_event in db_api.event_get_all_by_stack(context,
                                                              stack_id,
                                                              **kwargs)]

    @classmethod
    def count_all_by_stack(cls, context, stack_id):
        return db_api.event_count_all_by_stack(context, stack_id)

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(context, cls(),
                                   db_api.event_create(context, values))

    def identifier(self, stack_identifier):
        """Return a unique identifier for the event."""

        res_id = identifier.ResourceIdentifier(
            resource_name=self.resource_name, **stack_identifier)

        return identifier.EventIdentifier(event_id=str(self.uuid), **res_id)
