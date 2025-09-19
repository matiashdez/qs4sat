

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.providers.fake_provider import GenericBackendV2
from graph_coloring import *
import random
import math


def create_exponential_graph_coloring_search(
                                      oracle,
                                      check_oracle,
                                      n_qubits: int,
                                      top_k: int,
                                      growth: float = 8/7) -> list:
    """
    Quantum exponential search for graph coloring in a single function.
    Combines oracle creation, Grover exponential subroutine, and solution check.
    Returns a valid coloring assignment as a list.
    """
    # Create oracles
    

    m = 1
    while True:
        # Random repetition count
        j = random.randint(0, int(m) - 1)

        # Build exponential Grover circuit
        grover_qc = QuantumCircuit(oracle.num_qubits, n_qubits)
        grover_qc.x(-1)
        grover_qc.h(-1)
        for q in range(n_qubits):
            grover_qc.h(q)
        oracle_gate = oracle.to_gate()
        for _ in range(j):
            grover_qc.append(oracle_gate, list(range(oracle.num_qubits)))
        grover_qc.measure(list(range(n_qubits)), list(range(n_qubits)))

        # Execute
        backend = GenericBackendV2(num_qubits=oracle.num_qubits)
        pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
        transpiled_circuit = pm.run(grover_qc)

        job = backend.run(transpiled_circuit, shots=1024)
        counts = job.result().get_counts()

        # Top candidates
        candidates = sorted(counts, key=counts.get, reverse=True)[:top_k]
        for bitstr in candidates:
            assignment = list(map(int, bitstr))
            # Check solution via measurement oracle
            check_qc = QuantumCircuit(check_oracle.num_qubits, 1)
            for idx, bit in enumerate(assignment):
                if bit == 1:
                    check_qc.x(idx)
            
            check_qc.compose(check_oracle, inplace=True)
            check_qc.measure(check_oracle.num_qubits - 1, 0)

            pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
            transpiled_check = pm.run(check_qc)

            chk_job = backend.run(transpiled_check, shots=1024)
            chk_counts = chk_job.result().get_counts()
            if max(chk_counts, key=chk_counts.get) == '1':
                return assignment

      
        m = min(growth * m, math.sqrt(n_qubits))
        print(f"Solution not found. Increasing m to {m}")



def create_grover_search(oracle, m, n):
    


    GroverCircuit = QuantumCircuit(oracle.num_qubits, n)
    GroverCircuit.x(-1)
    GroverCircuit.h(-1)

    for qubit in range(n):
        GroverCircuit.h(qubit)
    

    numberOfRepetitions = math.ceil(math.pi/4 * math.sqrt(oracle.num_qubits/m))

    oracle_gate = oracle.to_gate()
    

    for _ in range(numberOfRepetitions):
        GroverCircuit.append(oracle_gate, range(oracle.num_qubits))
     
    GroverCircuit.measure(range(n), range(n))

    return GroverCircuit




def create_quantum_counting(oracle, n):

    
    t = math.ceil((n/2) + 3)
    CountingCircuit = QuantumCircuit((t + oracle.num_qubits), t)

    for qubit in range(t + n):
        CountingCircuit.h(qubit)
    
    CountingCircuit.x(-1)
    CountingCircuit.h(-1)
   
    oracle_gate = oracle.to_gate()

    for i in range(t):
        controlled_oracle = oracle_gate.control(1).repeat(2 ** i)
        CountingCircuit.append(controlled_oracle, [i] + list(range(t, t + oracle.num_qubits)))


    CountingCircuit.append(QFT(t).inverse(), range(t))
    CountingCircuit.measure(range(t), range(t))




    return CountingCircuit




def create_diffuser(n):
        diffuser = QuantumCircuit(n)
        
        for qubit in range(n):
            diffuser.h(qubit)
        
        for qubit in range(n):
            diffuser.x(qubit)
        
        diffuser.h(n-1)
        diffuser.mcx(list(range(n-1)), n-1)
        diffuser.h(n-1)
        
        for qubit in range(n):
            diffuser.x(qubit)
        
        for qubit in range(n):
            diffuser.h(qubit)
        
        return diffuser
