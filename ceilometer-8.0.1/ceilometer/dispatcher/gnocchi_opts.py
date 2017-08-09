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


dispatcher_opts = [
    cfg.BoolOpt('filter_service_activity',
                default=True,
                help='Filter out samples generated by Gnocchi '
                'service activity'),
    cfg.StrOpt('filter_project',
               default='gnocchi',
               help='Gnocchi project used to filter out samples '
               'generated by Gnocchi service activity'),
    cfg.StrOpt('archive_policy',
               help='The archive policy to use when the dispatcher '
               'create a new metric.'),
    cfg.StrOpt('resources_definition_file',
               default='gnocchi_resources.yaml',
               help=('The Yaml file that defines mapping between samples '
                     'and gnocchi resources/metrics')),
]
