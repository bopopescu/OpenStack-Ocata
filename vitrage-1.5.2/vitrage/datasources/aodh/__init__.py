# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from vitrage.common.constants import UpdateMethod

AODH_DATASOURCE = 'aodh'

OPTS = [
    cfg.StrOpt('transformer',
               default='vitrage.datasources.aodh.'
                       'transformer.AodhTransformer',
               help='Aodh transformer class path',
               required=True),
    cfg.StrOpt('driver',
               default='vitrage.datasources.aodh.driver.AodhDriver',
               help='Aodh driver class path',
               required=True),
    cfg.StrOpt('update_method',
               default=UpdateMethod.PUSH,
               help='None: updates only via Vitrage periodic snapshots.'
                    'Pull: updates every [changes_interval] seconds.'
                    'Push: updates by getting notifications from the'
                    ' datasource itself.',
               required=True),
    cfg.IntOpt('changes_interval',
               default=20,
               min=20,
               help='interval between checking changes in aodh data source'),
]
