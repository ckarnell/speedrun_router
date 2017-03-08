import json
import pprint

class DependencyTable():
    def __init__(self, table_path=None):
        if table_path:
            self.table_path = table_path
            with open (table_path) as table_file:
                self.dep_dict = json.load(table_file)
        else:
            self.table_path = 'dependency_table.txt'
            self.dep_dict = {}

    def addNode(self, node_name):
        if node_name:
            str_node = str(node_name)
            if str_node not in self.dep_dict:
                self.dep_dict[str_node] = []

    def addEdge(self, start_node, end_node):
        str_start, str_end = str(start_node), str(end_node)
        self.addNode(str_start)
        self.addNode(str_end)
        self.dep_dict[str_start].append(str_end)

    def saveTable(self, alternate_filename=None):
        if alternate_filename:
            with open(alternate_filename, 'wb') as json_table:
                json.dump(self.dep_dict, json_table, indent=4)
        else:
            with open(self.filename, 'wb') as json_table:
                json.dump(self.dep_dict, json_table, indent=4)

    def printTable(self):
        print self.dep_dict

if __name__ == '__main__':
    debug = True # Set to True to run tests

    if debug:
        import unittest
        class TestDependencyTable(unittest.TestCase):
            def setUp(self):
                self.dep_table = DependencyTable()

            def test_add_node(self):
                inputs = ('test', 5)
                expected = ({'test': []}, {'test': [], '5': []})
                result = ()
                for i in inputs:
                    self.dep_table.addNode(i)
                    result = result + (dict(self.dep_table.dep_dict),)
                self.assertTrue(all(expected[i] == result[i] for i in range(len(expected))))

            def test_add_edge_neither_node_exist(self):
                self.dep_table.addEdge('hi', 'hey')
                self.assertTrue(self.dep_table.dep_dict == {'hi': ['hey'], 'hey': []})


        unittest.main()
