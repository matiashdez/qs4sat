#%%

import cmath
from termcolor import colored
import math


# Function to get extended edges in a graph

def get_extended_edges(nodes, edges):
    def get_neighbors(nodes, edges):
        neighbors = [[] for _ in range(nodes)]
        for edge in edges:
            node1, node2 = edge
            neighbors[node1].append(node2)
            neighbors[node2].append(node1)  
        return neighbors
    
    neighborsList = get_neighbors(nodes, edges)

    def convert_list(listed):
        result = []
        for i in range(len(listed)):
            neighbors = []
            for eachNeighbor in listed[i]:
                neighbors.extend(listed[eachNeighbor])
            neighbors = list(set(neighbors) - set([i]))
            result.append(neighbors)
        return result

    neighborsFromNeighbors = convert_list(neighborsList)

    def add_links(adjacencyList, linksList):
        transformedList = convert_list(adjacencyList)
        for node, neighbors in enumerate(transformedList):
            for eachNeighbor in neighbors:
                if (node, eachNeighbor) not in linksList and (eachNeighbor, node) not in linksList:
                    linksList.append((node, eachNeighbor))
        return linksList

    return add_links(neighborsList, edges)



def print_state(statevector, num_cols=0, print_0_prob=False, precision=6):
    ''' Prints the statevector (calculated as 'qiskit.quantum_info.Statevector(qc)' ) showing the kets and their probabilities
        The user can select whether states with 0 probability are to be shown, the number of columns to organize the output,
        and the number of decimal places for the probabilities.
        Numbers in blue have phase 0 and in yellow phase PI.
    '''
    num_cols = statevector.num_qubits // 2 if num_cols == 0 else num_cols
    for pos, val in enumerate(statevector.data):
        prob = abs(val) ** 2
        phase = cmath.phase(val)
        txt = f"|{pos:0{statevector.num_qubits}b}\u232A: {prob:.{precision}f}"  
        fin = '\n' if (pos + 1) % num_cols == 0 else '\t'
        if math.isclose(prob, 0, abs_tol=1e-6):
            if print_0_prob:
                print(colored(txt, 'white'), end=fin)
        elif math.isclose(phase, 0, abs_tol=1e-6):
            print(colored(txt, 'blue', attrs=["bold"]), end=fin)
        elif math.isclose(phase, math.pi, abs_tol=1e-6) or math.isclose(phase, -math.pi, abs_tol=1e-6):
            print(colored(txt, 'yellow', attrs=["bold"]), end=fin)
        else:
            print(colored(txt + f"({phase})", 'red', attrs=["bold"]), end=fin)

# %%
