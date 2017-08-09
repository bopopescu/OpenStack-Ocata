# Copyright 2016 - Alcatel-Lucent
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

import abc
from collections import namedtuple
import six

Mapping = \
    namedtuple('Mapping', ['subgraph_element', 'graph_element', 'is_vertex'])


@six.add_metaclass(abc.ABCMeta)
class GraphAlgorithm(object):

    def __init__(self, graph):
        """Create a new GraphAlgorithm

        :param graph: graph instance
        :type graph: driver.Graph
        """
        self.graph = graph

    @abc.abstractmethod
    def graph_query_vertices(self,
                             query_dict=None,
                             root_id=None,
                             depth=None,
                             direction=None,
                             edge_query_dict=None):
        """Create a sub graph of all the matching vertices and their edges

        BFS traversal over the graph starting from root, each vertex is
        checked according to the query. A matching vertex will be added to the
        resulting sub graph and traversal will continue to its neighbors
        :rtype: driver.Graph
        """
        pass

    @abc.abstractmethod
    def sub_graph_matching(self, sub_graph, known_mappings, validate=False):
        """Search for occurrences of of a template graph in the graph

        In sub-graph matching algorithms complexity is high in the general case
        Here it is considerably mitigated  as we have an anchor in the graph.
        TODO(ihefetz)  document this

        :type known_mappings: list
        :type sub_graph: driver.Graph
        :type validate: bool
        :rtype: list of dict
        """
        pass

    @abc.abstractmethod
    def subgraph(self, entities):
        """Return the subgraph induced on nodes in entities.

        The induced subgraph of the graph contains the nodes in entities and
        the edges between those nodes.

        :type entities: list
        :rtype: NXGraph
        """
        pass

    @staticmethod
    def connected_component_subgraphs(subgraph):
        """Generate connected components as subgraphs.

        :type subgraph: NetworkX graph.
        :rtype: list of NXGraphs
        """
        pass

    def all_simple_paths(self, source, target):
        """Generate all simple paths in the graph G from source to target.

        A simple path is a path with no repeated nodes.

        :type source: Starting node for path
        :type target: Ending node for path
        :rtype: lists of simple paths
        """
        pass

    @abc.abstractmethod
    def create_graph_from_matching_vertices(self,
                                            vertex_attr_filter=None,
                                            query_dict=None,
                                            edge_attr_filter=None):
        """Generate graph using the query

        Finds all the vertices in the graph matching the query, and returns
        a subgraph consisted from the vertices

        :type vertex_attr_filter: dictionary
        :type query_dict: dictionary
        :type edge_attr_filter: dictionary
        :rtype: NXGraph
        """
        pass