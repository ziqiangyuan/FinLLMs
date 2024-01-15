import json
from Graph.graph import *
import copy


def get_funs(input_path='data/funciton.json',
             t_num=5,
             output_path='data/all_function.json',
             max_dsl_program_step=4,
             max_variable_number=5):
    init_nodes = []
    time_nodes = []
    init_variable_list = []
    time_variable_list = []
    with open(input_path, encoding='utf-8') as input_file:
        input_data = json.load(input_file)
    for target in input_data.keys():
        fs = input_data[target]
        for f in fs:
            if 'text' in f and len(f['text']) != 0:
                node = Node(target, f['variable'], f['formula'])
                init_variable_list += f['variable']
                init_nodes.append(node)
    variable_list = list(set(init_variable_list))
    print('Number of initial formulas：', len(init_nodes))
    print('Number of initial variables：', len(variable_list))
    for node in init_nodes:
        node1 = Node(str(node.target), list(node.variables), list(node.formula))
        node2 = Node(str(node.target), list(node.variables), list(node.formula))
        node1.change_to_time('*n')
        node2.change_to_time('*n-1')
        time_nodes.append(node1)
        time_nodes.append(node2)
        time_variable_list += node1.variables
        time_variable_list += node2.variables
        time_variable_list.append(node1.target)
        time_variable_list.append(node2.target)
    time_variable_list = list(set(time_variable_list))
    for v in init_variable_list:
        # change
        target = 'increase_of_' + v
        formula = ['subtract', v + '*n', v + '*n-1']
        variables = [v + '*n', v + '*n-1']
        node1 = Node(target, variables, formula)
        time_nodes.append(node1)
        time_variable_list.append(target)
        # change rate
        target = 'change_rate_of_' + v
        formula = ['subtract', v + '*n', v + '*n-1', 'divide', '#0', v + '*n-1']
        variables = [v + '*n', v + '*n-1']
        node2 = Node(target, variables, formula)
        time_nodes.append(node2)
        time_variable_list.append(target)
    num = 0
    for node in time_nodes:
        if '*n' not in node.target:
            num += 1
        elif '*n-1' not in node.target:
            num += 1


    G = FormulaGraph(time_nodes)
    #for index in G.graph.nodes:
    #    print(G.get_node_attr(index))

    print("Number of initial edges", len(G.graph.edges))
    print("Number of initial Nodes", len(G.graph.nodes))
    G.get_nodes_num()
    for i in range(t_num):
        G.expension(max_length=max_dsl_program_step*3, max_variable=max_variable_number)
        print('step: ' + str(i+1)+" edges:", len(G.graph.edges))
        G.get_nodes_num()
        print('step: ' + str(i+1)+" nodes:", len(G.graph.nodes))
    fun_list = []
    for index in G.graph.nodes:
        fun_list.append(G.node_dict[index])
    write(fun_list, output_path)
    return fun_list

def write(fun, path):
    with open(path, "w", encoding='utf-8') as f:
        json.dump(fun, f)




