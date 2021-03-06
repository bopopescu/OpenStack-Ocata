#
# Copyright 2015 b<>com
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


# Audit Template
AUDIT_TEMPLATE_FIELDS = [
    'uuid', 'created_at', 'updated_at', 'deleted_at',
    'description', 'name', 'goal_name', 'strategy_name', 'scope']

AUDIT_TEMPLATE_FIELD_LABELS = [
    'UUID', 'Created At', 'Updated At', 'Deleted At',
    'Description', 'Name', 'Goal', 'Strategy', 'Audit Scope']

AUDIT_TEMPLATE_SHORT_LIST_FIELDS = [
    'uuid', 'name', 'goal_name', 'strategy_name']

AUDIT_TEMPLATE_SHORT_LIST_FIELD_LABELS = ['UUID', 'Name', 'Goal', 'Strategy']

# Audit
AUDIT_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at',
                'state', 'audit_type', 'parameters', 'interval', 'goal_name',
                'strategy_name', 'scope', 'auto_trigger']

AUDIT_FIELD_LABELS = ['UUID', 'Created At', 'Updated At', 'Deleted At',
                      'State', 'Audit Type', 'Parameters', 'Interval', 'Goal',
                      'Strategy', 'Audit Scope', 'Auto Trigger']

AUDIT_SHORT_LIST_FIELDS = ['uuid', 'audit_type',
                           'state', 'goal_name', 'strategy_name',
                           'auto_trigger']

AUDIT_SHORT_LIST_FIELD_LABELS = ['UUID', 'Audit Type', 'State', 'Goal',
                                 'Strategy', 'Auto Trigger']

# Action Plan
ACTION_PLAN_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at',
                      'audit_uuid', 'strategy_name', 'state',
                      'efficacy_indicators', 'global_efficacy']

ACTION_PLAN_FIELD_LABELS = ['UUID', 'Created At', 'Updated At', 'Deleted At',
                            'Audit', 'Strategy', 'State',
                            'Efficacy indicators', 'Global efficacy']

ACTION_PLAN_SHORT_LIST_FIELDS = ['uuid', 'audit_uuid', 'state',
                                 'updated_at', 'global_efficacy']

ACTION_PLAN_SHORT_LIST_FIELD_LABELS = ['UUID', 'Audit', 'State',
                                       'Updated At', 'Global efficacy']

# Action
ACTION_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at', 'parents',
                 'state', 'action_plan_uuid', 'action_type',
                 'input_parameters']

ACTION_FIELD_LABELS = ['UUID', 'Created At', 'Updated At', 'Deleted At',
                       'Parents', 'State', 'Action Plan', 'Action',
                       'Parameters']

ACTION_SHORT_LIST_FIELDS = ['uuid', 'parents',
                            'state', 'action_plan_uuid', 'action_type']

ACTION_SHORT_LIST_FIELD_LABELS = ['UUID', 'Parents', 'State',
                                  'Action Plan', 'Action']
# Goals

GOAL_FIELDS = ['uuid', 'name', 'display_name', 'efficacy_specification']

GOAL_FIELD_LABELS = ['UUID', 'Name', 'Display name', 'Efficacy specification']

GOAL_SHORT_LIST_FIELDS = ['uuid', 'name', 'display_name']

GOAL_SHORT_LIST_FIELD_LABELS = ['UUID', 'Name', 'Display name']

# Strategies

STRATEGY_FIELDS = ['uuid', 'name', 'display_name', 'goal_name',
                   'parameters_spec']

STRATEGY_FIELD_LABELS = ['UUID', 'Name', 'Display name', 'Goal',
                         'Parameters spec']

STRATEGY_SHORT_LIST_FIELDS = ['uuid', 'name', 'display_name', 'goal_name']

STRATEGY_SHORT_LIST_FIELD_LABELS = ['UUID', 'Name', 'Display name', 'Goal']

# Metric Collector
METRIC_COLLECTOR_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at',
                           'endpoint', 'category']

METRIC_COLLECTOR_FIELD_LABELS = ['UUID', 'Created At', 'Updated At',
                                 'Deleted At', 'Endpoint URL',
                                 'Metric Category']

METRIC_COLLECTOR_SHORT_LIST_FIELDS = ['uuid', 'endpoint', 'category']

METRIC_COLLECTOR_SHORT_LIST_FIELD_LABELS = ['UUID', 'Endpoint URL',
                                            'Metric Category']
# Scoring Engines
SCORING_ENGINE_FIELDS = ['uuid', 'name', 'description', 'metainfo']
SCORING_ENGINE_FIELD_LABELS = ['UUID', 'Name', 'Description', 'Metainfo']

SCORING_ENGINE_SHORT_LIST_FIELDS = ['uuid', 'name', 'description']
SCORING_ENGINE_SHORT_LIST_FIELD_LABELS = ['UUID', 'Name', 'Description']

# Services
SERVICE_FIELDS = ['id', 'name', 'host', 'status', 'last_seen_up']
SERVICE_FIELD_LABELS = ['ID', 'Name', 'Host', 'Status', 'Last seen up']
SERVICE_SHORT_LIST_FIELDS = ['id', 'name', 'host', 'status']
SERVICE_SHORT_LIST_FIELD_LABELS = ['ID', 'Name', 'Host', 'Status']
