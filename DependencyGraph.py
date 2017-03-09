import json
import pprint
import sys

class DependencyGraph():
    def __init__(self, graph_path=None):
        # Optionally open an existing graph if given a path to a json file
        if graph_path:
            self.graph_path = graph_path
            with open (graph_path) as graph_file:
                self.dep_dict = json.load(graph_file)
        else:
            self.graph_path = 'dependency_graph.json'
            # dep_dict will look like {node1: {dependency1: time1, dependency2: time2...}, node2:...}
            self.dep_dict = {}
            self.nodes = self.dep_dict.keys()
        self.origin_node = None
        self.terminal_node = None

    def addNode(self, node_name):
        str_node = str(node_name)
        assert str_node, 'Node name must be non-empty'

        if str_node not in self.dep_dict:
            self.dep_dict[str_node] = {}
            self.nodes.append(str_node)
        else:
            raise Exception('Node {} already exists in the graph'.format(str_node))

    def removeNode(self, node_name):
        node_name = str(node_name)
        if node_name in self.nodes:
            nodes = list(self.nodes)
            nodes.remove(node_name)
            for node in nodes:
                if node_name in self.dep_dict[node].keys():
                    raise Exception('There are nodes in the graph that depend on {}'.format(node_name))
            # If no nodes depend on the node to be removed, remove it
            self.nodes.remove(node_name)
            del self.dep_dict[node_name]
        else:
            raise Exception('{} is not a node in the graph'.format(node_name))

    def cycleCheck(self, current_node, target_node, visited_nodes=None):
        '''
        Raises an error if the current node or any of it's dependents depend
        on the target node, indicating a cycle. Otherwise passes silently
        '''
        if visited_nodes:
            visited_nodes.append(current_node)
        else:
            visited_nodes = [current_node]
        for node in self.dep_dict[current_node].keys():
            if node == target_node:
                raise Exception('Target node would cause a dependency cycle if added')
            elif node not in visited_nodes:
                self.cycleCheck(node, target_node, visited_nodes)

    def addDependence(self, dependent_node, dependency_node, time=None):
        if all(node in self.dep_dict.keys() for node in [dependent_node, dependency_node]):
            # Throw an error if this would cause a cycle
            self.cycleCheck(dependency_node, dependent_node)
            self.dep_dict[dependent_node][dependency_node] = time
        else:
            # If one or both nodes aren't in the graph yet, it can't 
            # create a cycle to add the edge between them
            if dependent_node not in self.nodes:
                self.addNode(dependent_node)
            if dependency_node not in self.nodes:
                self.addNode(dependency_node)
            self.dep_dict[dependent_node][dependency_node] = time

    def setEdgeTime(self, dependent_node, dependency_node, time):
        str_start, str_end = str(dependent_node), str(dependency_node)
        if any(node not in self.nodes for node in [str_start, str_end]):
            self.addDependence(str_start, str_end)
        self.dep_dict[str_start][str_end] = time

    def clearNodeDependencies(self, node_name):
        node_name = str(node_name)
        if node_name in self.nodes:
            self.dep_dict[node_name] = {}
        else:
            raise Exception('{} is not a node in the graph'.format(node_name))

    def setOriginNode(self, origin_node):
        origin_node = str(origin_node)
        if origin_node in self.nodes:
            self.origin_node = origin_node
        else:
            raise Exception('{} is not a node in the graph'.format(node_name))

    def setTerminalNode(self, terminal_node):
        terminal_node = str(terminal_node)
        if terminal_node in self.nodes:
            self.terminal_node = terminal_node
        else:
            raise Exception('{} is not a node in the graph'.format(node_name))

    def saveGraph(self, alternate_filename=None):
        if alternate_filename:
            with open(alternate_filename, 'wb') as json_graph:
                json.dump(self.dep_dict, json_graph, indent=4)
        else:
            with open(self.filename, 'wb') as json_graph:
                json.dump(self.dep_dict, json_graph, indent=4)

    def printGraph(self):
        pprint(self.dep_dict)

    def printNodes(self):
        pprint(self.nodes)

    def minimizeGraph(self, origin_node=None, terminal_node=None):
        if origin_node:
            self.setOriginNode(origin_node)
        if terminal_node:
            self.setTerminalNode(terminal_node)
        if self.origin_node is None or self.terminal_node is None:
            raise Exception('Both origin and terminal nodes must be set')

if __name__ == '__main__':
    debug = True # Set to True to run tests

    if debug:
        import unittest
        class TestDependencyGraph(unittest.TestCase):
            def setUp(self):
                self.dep_graph = DependencyGraph()

            def test_add_node(self):
                inputs = ('test', 5)
                expected = ({'test': {}}, {'test': {}, '5': {}})
                result = ()
                for i in inputs:
                    self.dep_graph.addNode(i)
                    result = result + (dict(self.dep_graph.dep_dict),)
                self.assertTrue(all(expected[i] == result[i] for i in range(len(expected))))

            def test_add_dependence_neither_node_exists(self):
                self.dep_graph.addDependence('hi', 'hey')
                self.assertTrue(self.dep_graph.dep_dict == {'hi': {'hey': None}, 'hey': {}})

            def test_add_dependence_bot_nodes_exist(self):
                self.dep_graph.dep_dict = {'GameStart': {}, 'PokeyEscape': {'GetSword': 4}, 'GetSword': {'GameStart': 5}, 'WESS': {'GetSword': 10}}
                self.dep_graph.addDependence('WESS', 'PokeyEscape')
                self.assertTrue(self.dep_graph.dep_dict['WESS'] == {'GetSword': 10, 'PokeyEscape': None})

            def test_remove_empty_node(self):
                self.dep_graph.dep_dict = {'test': {}, '5': {}}
                self.dep_graph.nodes = ['test', '5']
                self.dep_graph.removeNode('test')
                results = [dict(self.dep_graph.dep_dict)]
                self.dep_graph.removeNode('5')
                results.append(dict(self.dep_graph.dep_dict))
                expected = [{'5': {}}, {}]
                self.assertTrue(all(results[i] == expected[i] for i in range(len(results))))

            def test_add_dependence_with_time(self):
                self.dep_graph.dep_dict = {'test': {}, '5': {}}
                self.dep_graph.nodes = ['test', '5']
                self.dep_graph.addDependence('test', '5', 6.15)
                self.assertTrue(self.dep_graph.dep_dict == {'test': {'5': 6.15}, '5': {}})

            def test_cycle_check(self):
                self.dep_graph.dep_dict = {'PokeyEscape': {'GetSword': 4}, 'GetSword': {'GameStart': 5}, 'GameStart': {}}
                try:
                    self.dep_graph.cycleCheck('PokeyEscape', 'GameStart')
                except Exception as e:
                    self.assertTrue(str(e) == 'Target node would cause a dependency cycle if added')
                else:
                    raise Exception, 'Failed to find cycle'

        unittest.main()