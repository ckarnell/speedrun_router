import json
import pprint
import sys

class DependencyTable():
    def __init__(self, table_path=None):
        # Optionally open an existing table if given a path to a json file
        if table_path:
            self.table_path = table_path
            with open (table_path) as table_file:
                self.dep_dict = json.load(table_file)
        else:
            self.table_path = 'dependency_table.json'
            self.nodes = []
            # dep_dict will look like {node1: {dependency1: time1, dependency2: time2...}, node2:...}
            self.dep_dict = {}

    def addNode(self, node_name):
        if node_name:
            str_node = str(node_name)
            if str_node not in self.dep_dict:
                self.dep_dict[str_node] = {}
                self.nodes.append(str_node)

    def addEdge(self, start_node, end_node, time=None):
        str_start, str_end = str(start_node), str(end_node)
        if str_start not in self.nodes:
            self.addNode(str_start)
        if str_end not in self.nodes:
            self.addNode(str_end)
        # Default to the max int to help with Dijkstra's algorithm
        if time:
            self.dep_dict[str_start][str_end] = time
        else:
            self.dep_dict[str_start][str_end] = sys.maxint

    def setMinEdgeTime(self, start_node, end_node, time):
        str_start, str_end = str(start_node), str(end_node)
        if any(node not in self.nodes for node in [str_start, str_end]):
            self.addEdge(str_start, str_end)
        self.dep_dict[str_start][str_end] = time

    def saveTable(self, alternate_filename=None):
        if alternate_filename:
            with open(alternate_filename, 'wb') as json_table:
                json.dump(self.dep_dict, json_table, indent=4)
        else:
            with open(self.filename, 'wb') as json_table:
                json.dump(self.dep_dict, json_table, indent=4)

    def printTable(self):
        pprint(self.dep_dict)

    def printNodes(self):
        pprint(self.nodes)

if __name__ == '__main__':
    debug = True # Set to True to run tests

    if debug:
        import unittest
        class TestDependencyTable(unittest.TestCase):
            def setUp(self):
                self.dep_table = DependencyTable()

            def test_add_node(self):
                inputs = ('test', 5)
                expected = ({'test': {}}, {'test': {}, '5': {}})
                result = ()
                for i in inputs:
                    self.dep_table.addNode(i)
                    result = result + (dict(self.dep_table.dep_dict),)
                self.assertTrue(all(expected[i] == result[i] for i in range(len(expected))))

            def test_add_edge_neither_node_exist(self):
                self.dep_table.addEdge('hi', 'hey')
                self.assertTrue(self.dep_table.dep_dict == {'hi': {'hey': sys.maxint}, 'hey': {}})


        unittest.main()
