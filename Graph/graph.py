import networkx as nx

class Node:
    def __init__(self, target, variables, formula):
        self.target = target
        self.variables = variables
        self.formula = formula
        self.value = []
        self.program_str = ''
        self.program = []

    def change_to_time(self, time):
        for (index_x, f) in enumerate(self.formula):
            if f in self.variables:
                self.formula[index_x] = f + time
        self.target += time
        for (index, v) in enumerate(self.variables):
            self.variables[index] = v + time

    def to_dict(self):
        return {'target':self.target, 'variables':self.variables, 'formula':self.formula,'value':self.value,'program':self.program,'program_str':self.program_str}


class FormulaGraph:
    def __init__(self, nodes):
        self.graph = nx.DiGraph()
        self.node_dict = {}
        self.used_edge = set()
        for (index, n) in enumerate(nodes):
            d = dict(n.to_dict())
            self.graph.add_node(index)
            self.node_dict[index] = d
        #add edge
        for index1 in self.graph.nodes:
            for index2 in self.graph.nodes:
                if self.node_dict[index1]['target'] in self.node_dict[index2]['variables']:
                    self.graph.add_edge(index1, index2)


    def get_nodes_num(self):
        num = 0
        for key in self.node_dict.keys():
            target = self.node_dict[key]['target']
            if '*n-1' not in target:
                num += 1
        print("number of formulas：", num)
        return num

    def get_node_attr(self, index):
        return self.node_dict[index]

    def add_node(self, attr):
        index = self.graph.number_of_nodes()
        self.node_dict[index] = attr
        self.graph.add_node(index)
        for index2 in self.graph.nodes:
            if self.node_dict[index]['target'] in self.node_dict[index2]['variables']:
                self.graph.add_edge(index, index2)
        for index1 in self.graph.nodes:
            if self.node_dict[index1]['target'] in self.node_dict[index]['variables']:
                self.graph.add_edge(index1, index)

    def expension(self, max_length=12, max_variable=3):
        all_edges = list(self.graph.edges)
        for e in all_edges:
            if e in self.used_edge:
                continue
            index1 = e[0]
            index2 = e[1]
            self.used_edge.add(e)

            target = self.node_dict[index2]['target']
            if 'n-1' in target:
                continue
            variables1 = self.node_dict[index1]['variables']
            variables2 = self.node_dict[index2]['variables']
            variables = variables1 + variables2
            variables = list(set(variables))
            variables.remove(self.node_dict[index1]['target'])

            # 未合并
            formula = self.merge_formula(list(self.node_dict[index1]['formula']), list(self.node_dict[index2]['formula']), str(self.node_dict[index1]['target']))

            if len(variables) > max_variable or len(formula) > max_length:
                continue

            node = Node(target, variables, formula)
            self.add_node(node.to_dict())

    def merge_formula(self, formula1, formula2, target):
        num = int(len(formula1)/3)
        for (index,f) in enumerate(formula2):
            if f == target:
                formula2[index] = '#' + str(num-1)
            elif f[0] == '#':
                num_tmp = int(f[1:])
                formula2[index] = '#' + str(num + num_tmp)
        new_f = []
        for f in formula1:
            new_f.append(f)
        for f in formula2:
            new_f.append(f)
        return new_f

if __name__ == '__main__':
    def merge_formula(formula1, formula2, target):
        num = int(len(formula1)/3)
        for (index, f) in enumerate(formula2):
            if f == target:
                formula2[index] = '#' + str(num - 1)
            elif f[0] == '#':
                num_tmp = int(f[1:])
                formula2[index] = '#' + str(num + num_tmp)
        new_f = []
        for f in formula1:
            new_f.append(f)
        for f in formula2:
            new_f.append(f)
        return new_f
    d = ['add', 'a', 'basd', 'add', '#0', 'c']
    f2 = ['add', 'dasd', 'dasd', 'add', '#0', 'c']
    print(merge_formula(d, f2, 'dasd'))


