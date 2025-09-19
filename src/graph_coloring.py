


from qiskit import QuantumCircuit 
import math
import utils
import quantum_algorithms
from qiskit.visualization import plot_histogram

# AES 

def graph_coloring_oracle_sat_formula(nodes, edges, chromaticSpace, use_extendedEdges = False):

    if use_extendedEdges:
        extendedEdges = utils.get_extended_edges(nodes, edges)
    else:
        extendedEdges = edges

    
    totalCircuitLength = (nodes * chromaticSpace) + nodes + (len(extendedEdges) * chromaticSpace) + 1
    numberOfEdges = len(extendedEdges)

    qubits = []
    start = 0
    for _ in range(nodes):
        end = start + chromaticSpace
        qubits.append(tuple(range(start, end)))  
        start = end

    def create_initial_quantum_circuit(numberOfEdges, chromaticSpace, nodes):
        initialQuantumCircuit = QuantumCircuit((nodes * chromaticSpace) + nodes + (numberOfEdges * chromaticSpace) + 1)
        return initialQuantumCircuit  

    initialCircuit = create_initial_quantum_circuit(numberOfEdges, chromaticSpace, nodes)

    # Add first color constraint
    ancillaPositions = []
    def generate_full_qubit_list(qubits):
        qubitsList = []
        for qubitSet in qubits:
            qubitList = list(qubitSet)
            qubitsList.append(qubitList)
        return qubitsList
    
    qubitsList = generate_full_qubit_list(qubits)
    ancillaQubitIndex = nodes * chromaticSpace

    for qubitGroup in qubitsList:
        for eachQubit in qubitGroup:
            initialCircuit.x(eachQubit)
        initialCircuit.mcx(list(qubitGroup), ancillaQubitIndex)  
        ancillaPositions.append(ancillaQubitIndex)
        for eachQubit in qubitGroup:
            initialCircuit.x(eachQubit)
        initialCircuit.x(ancillaQubitIndex)
        ancillaQubitIndex += 1

    # Add second color constraint  
    expandedEdges = []
    for eachEdge in extendedEdges:
        for i in range(chromaticSpace):
            expandedEdges.append((eachEdge[0] * chromaticSpace + i, eachEdge[1] * chromaticSpace + i))

    for eachExpandedEdge in expandedEdges:
        initialCircuit.ccx(eachExpandedEdge[0], eachExpandedEdge[1], ancillaQubitIndex)
        ancillaPositions.append(ancillaQubitIndex)
        initialCircuit.x(ancillaQubitIndex)
        ancillaQubitIndex += 1

    def create_middle_circuit(initialCircuit, ancillaPositions, ancillaQubitIndex):
        quantumSupportCircuit = QuantumCircuit(totalCircuitLength)
        quantumSupportCircuit.mcx(ancillaPositions, ancillaQubitIndex)
        return quantumSupportCircuit
    
    middleCircuit = create_middle_circuit(initialCircuit, ancillaPositions, ancillaQubitIndex)


    reversedCircuit = initialCircuit.reverse_ops()

    firstCircuitCombination = middleCircuit.compose(initialCircuit, range(0, totalCircuitLength), front=True)
    oracleCircuit = reversedCircuit.compose(firstCircuitCombination, range(0, totalCircuitLength), front=True)



    
    
    diffuserCircuit = quantum_algorithms.create_diffuser(nodes * chromaticSpace)

    oraclePlusDiffuser = oracleCircuit.compose(diffuserCircuit, range(0, (nodes * chromaticSpace)), front=False)

    return oraclePlusDiffuser





def graph_coloring_oracle_counters_OH(nodes, colors, edges, use_extendedEdges = False):

    degree_count = {i: 0 for i in range(nodes)}


    for edge in edges:
        degree_count[edge[0]] += 1
        degree_count[edge[1]] += 1

    
    max_degree = max(degree_count.values())

    if use_extendedEdges:
        extendedEdges = utils.get_extended_edges(nodes, edges)
    else:
        extendedEdges = edges



    circuitLength = (nodes * colors) + max(math.floor(math.log2(nodes)), math.floor(math.log2(max_degree))) + 3
    qcaux = QuantumCircuit(circuitLength, 1)
    qcaux2 = QuantumCircuit(circuitLength, 1)
    qc = QuantumCircuit(circuitLength, 1)

    for qubit in range(nodes * colors):
        qc.h(qubit)

    sum1 = (nodes * colors) 
    sum2 = (nodes * colors) + 1
    sum3 = (nodes * colors) + 2

    control_qubit = (nodes * colors)  
    start_qubit = sum2 + 1 
    last_target_qubits = [] 

    qc.barrier()

    for node in range(nodes):
        node_adjusted = node + 1
        node_qubit = node * colors  
        qc.cx(node_qubit, control_qubit)

        for color in range(1, colors):
            qc.ccx(node_qubit + color, control_qubit, sum2)
            qc.cx(node_qubit + color, control_qubit)

        qc.barrier()

        qc.x(sum2)
    

        level = 0
        current_qubits = [sum1, sum2]
      
        if node_adjusted == 1:
            target_qubit = start_qubit
            qc.ccx(sum1, sum2, target_qubit)
            last_target_qubits = [target_qubit]
          
        else:
      
            while (1 << level) <= node_adjusted:
                if level > 0:
                    current_qubits.append(start_qubit + level - 1)

                target_qubit = start_qubit + level

   
                if len(current_qubits) == 2:
                    qcaux.ccx(current_qubits[0], current_qubits[1], target_qubit)
                else:
                    qcaux.mcx(current_qubits, target_qubit)

                level += 1
            qcaux_inverse = qcaux.inverse()
            qc = qc.compose(qcaux_inverse)
            qcaux.data = []
          

            if node_adjusted == nodes:

                current_qubits = [qubit + 1 for qubit in current_qubits]
                last_target_qubits = current_qubits[-(level):] 

        
        if node_adjusted == nodes:
            
            for i, bit in enumerate(reversed(f"{nodes:b}".zfill(len(last_target_qubits)))):
                if bit == '0':
                    qc.x(last_target_qubits[i])

            

        qc.x(sum2)
        qc.barrier()

        
        for color in range(colors - 1, 0, -1):
            qc.cx(node_qubit + color, control_qubit)
            qc.ccx(node_qubit + color, control_qubit, sum2)

        
        
        qc.cx(node_qubit, control_qubit)
        qc.barrier()

    
    qc.mcx(last_target_qubits, sum1)
    for qubit in range(sum3, circuitLength):
        qc.x(qubit)

    
    
    
    qc.barrier()
    primera_comparacion = True  



    for edge in extendedEdges:
        node_a, node_b = edge
        for color in range(colors):
            node_a_qubit = node_a * colors + color
            node_b_qubit = node_b * colors + color
            current_qubits = [node_a_qubit, node_b_qubit, sum2]

       
            current_qubits = list(set(current_qubits))

            if primera_comparacion:
                qc.ccx(node_a_qubit, node_b_qubit, sum2)
                primera_comparacion = False
            else:
               
                num_qubits = math.ceil(math.log2(max_degree + 2))  
                levels_qubits = []

                for level in range(num_qubits):
                    target_qubit = start_qubit + level

                    levels_qubits = list(set(levels_qubits))
                    
                    control_qubits = list(range(sum2+1, target_qubit))

                    if level == 0:
                        qcaux2.mcx(current_qubits, target_qubit)
                    else:

                        qcaux2.mcx(current_qubits + levels_qubits + control_qubits, target_qubit)
                        
                
                qcaux2_inverse = qcaux2.inverse()
                qc = qc.compose(qcaux2_inverse)
                qc.ccx(node_a_qubit, node_b_qubit, sum2)
                qcaux2.data = []
                levels_qubits.append(target_qubit)

            qc.barrier()
            

    for qubit in range(sum2, target_qubit+1):
        qc.x(qubit)
    qc.mcp(math.pi, list(range(sum1, (target_qubit))),  target_qubit)
    
    
    

    
    

    return qc



def graph_coloring_oracle_counters_bin(nodes, colors, edges, use_extendedEdges=False):
    degree_count = {i: 0 for i in range(nodes)}

 
    for edge in edges:
        degree_count[edge[0]] += 1
        degree_count[edge[1]] += 1

    
    max_degree = max(degree_count.values())

    if use_extendedEdges:
        extendedEdges = utils.get_extended_edges(nodes, edges)
    else:
        extendedEdges = edges


    if colors == 0:
        return ("Not possible to color the graph with 0 colors")
    elif (colors & (colors - 1)) == 0:
        restriction = False
    else:
        restriction = True

    qubitsPerNode = math.ceil(math.log2(colors))
    totalInputQubits = nodes * qubitsPerNode
    sum1 = totalInputQubits 
    sum2 = totalInputQubits + 1
    start_qubit = sum1

    

    if restriction:
        qc = QuantumCircuit(totalInputQubits + max(math.floor(math.log2(nodes)), math.floor(math.log2(max_degree))) + 2, 1)
    elif max_degree == 1:
        qc = QuantumCircuit(totalInputQubits + 2, 1)
    else:
        qc = QuantumCircuit(totalInputQubits + math.floor(math.log2(max_degree - 1)) + 2)
    

  
    for i in range(totalInputQubits):
        qc.h(i)

    primera_comparacion = True
    qcaux2 = QuantumCircuit(qc.num_qubits)

    qubits_afectados = []
    
    for edge in edges:
        node_a, node_b = edge
        

        node_a_qubits = list(range(node_a * qubitsPerNode, (node_a + 1) * qubitsPerNode))
        node_b_qubits = list(range(node_b * qubitsPerNode, (node_b + 1) * qubitsPerNode))
        

        qubits_afectados.append((node_a_qubits, node_b_qubits))

    

    

    primera_primera_comparacion = True
    nodos_qubits = []
    

    for node in range(nodes):
        node_qubits = list(range(node * qubitsPerNode, (node + 1) * qubitsPerNode))
        nodos_qubits.append(node_qubits)
    
   
    if colors > 0 and (colors & (colors - 1)) == 0:
        nothing = 0
    else:
        colores_a_quitar = (2**qubitsPerNode) - colors
        
        
        for i in range(colores_a_quitar+1):
            num_qubits = math.ceil(math.log2(max_degree))
            if primera_primera_comparacion:
                list1 = list(range(0, qubitsPerNode))
                qc.mcx(list1, sum1)
                primera_primera_comparacion = False
               
                
            else:
          
                levels_qubits = []
                
      

                
               
                for node_qubits in nodos_qubits[1:]:  
                    
                    
                    for bit_position, qubit in enumerate(node_qubits):
                        adjusted_color = (colors -1) + i 
                        if (adjusted_color >> bit_position) & 1 == 0:  
                            qcaux2.x(qubit)  
                
                    for level in range(num_qubits):
                        target_qubit = sum2 + level
                        
                        if level == 0:
                            aux_current_qubits = node_qubits + [sum1] + list(range((totalInputQubits+1), target_qubit))
                            qcaux2.mcx(aux_current_qubits, target_qubit)
                        else: 
                            aux_current_qubits = node_qubits + [sum1] + [sum2]
                            qcaux2.mcx(aux_current_qubits, target_qubit)
                            
                    
                    
                    levels_qubits.append(target_qubit)

                    qcaux2_inverse = qcaux2.inverse()
                    qc = qc.compose(qcaux2_inverse) 
                    qc.mcx(node_qubits, sum1)
                    qcaux2.data = []
                    qc.barrier()

        
        
       
        for i in range(num_qubits+1):
            qc.x(sum1 + i)

        
        
        qc.mcx(list(range(sum1, sum1 + num_qubits+1)), sum1 + num_qubits+1)

        for i in range(num_qubits+1):
            qc.x(sum1 + i)

                

        qc.barrier()

   
    primera_comparacion = True


    for pareja_afectada in qubits_afectados:
        node_a_qubits, node_b_qubits = pareja_afectada
        current_qubits = sum(pareja_afectada, [])


        if primera_comparacion:

            for i in pareja_afectada:
                qc.x(i)
            qc.mcx(current_qubits, sum1)
            for i in pareja_afectada:
                qc.x(i)

            qc.barrier()
            
            for i in range(colors-1):

                for node_qubits in pareja_afectada:  
                    for bit_position, qubit in enumerate(node_qubits):
                       
                        adjusted_color = i + 1  
                        if (adjusted_color >> bit_position) & 1 == 0:
                            qc.x(qubit)  

                if nodes == 2:
                    num_qubits = 1
                else:
                    num_qubits = math.ceil(math.log2(max_degree)) 

                levels_qubits = []
                for level in range(num_qubits):
                    target_qubit = sum2 + level
                    
                    if level == 0:  
                        aux_current_qubits = current_qubits + list(range(totalInputQubits, target_qubit))
                        qcaux2.mcx(aux_current_qubits, target_qubit)
                    else:  
                        aux_current_qubits = current_qubits + levels_qubits
                       
                        aux_current_qubits.append(sum1)
                        qcaux2.mcx(aux_current_qubits, target_qubit)
                    
                 
                    levels_qubits.append(target_qubit)
                
            
                qcaux2_inverse = qcaux2.inverse()
                qc = qc.compose(qcaux2_inverse)    
                qc.mcx(current_qubits, sum1)
              
                for node_qubits in pareja_afectada:  
                    for bit_position, qubit in enumerate(node_qubits):
     
                        adjusted_color = i + 1 
                        if (adjusted_color >> bit_position) & 1 == 0: 
                            qc.x(qubit)


                qcaux2.data = []
                levels_qubits.append(target_qubit)
                qc.barrier()
                               
            qc.barrier()
            primera_comparacion = False
        
        else:
            
            for i in range(colors):                
                num_qubits = math.ceil(math.log2(max_degree)) if nodes > 2 else 1
                levels_qubits = [] 

                for node_qubits in pareja_afectada: 
                    for bit_position, qubit in enumerate(node_qubits):
                     
                        adjusted_color = i  
                        if (adjusted_color >> bit_position) & 1 == 0:  
                            qc.x(qubit)   

                for level in range(num_qubits):
                    target_qubit = sum2 + level
                    
                    if level == 0: 
                        aux_current_qubits = current_qubits + list(range(totalInputQubits, target_qubit))
                        qcaux2.mcx(aux_current_qubits, target_qubit)
                    else:  
                        aux_current_qubits = current_qubits + levels_qubits
            
                        aux_current_qubits.append(sum1)
                        qcaux2.mcx(aux_current_qubits, target_qubit)
                 
                    levels_qubits.append(target_qubit)
                
   
                final_aux_qubits = current_qubits + levels_qubits
                
                
               
                qcaux2_inverse = qcaux2.inverse()
                qc = qc.compose(qcaux2_inverse) 
                qc.mcx(current_qubits, sum1) 

                for node_qubits in pareja_afectada: 
                    for bit_position, qubit in enumerate(node_qubits):
                    
                        adjusted_color = i 
                        if (adjusted_color >> bit_position) & 1 == 0: 
                            qc.x(qubit)  
                qcaux2.data = []
                
                
                qc.barrier()




    z_gate_qubits = list(range(sum1, qc.num_qubits - 1))
    z_gate_qubits_2 = list(range(sum1, qc.num_qubits))

    if colors > 0 and (colors & (colors - 1)) == 0:
        
        for qubit in z_gate_qubits_2:
            qc.x(qubit)

    else:
     
        for qubit in z_gate_qubits:
            qc.x(qubit)

    qc.mcp(math.pi, z_gate_qubits, -1)

    return qc