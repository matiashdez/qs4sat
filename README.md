
# QS4SAT: A Qiskit Library for Applying Quantum Search Algorithms and Constructing Quantum Oracles for SAT-Based Problems

This repository provides quantum algorithm implementations for solving the **graph coloring problem**, leveraging Grover Search, Quantum Counting, and Quantum Exponential Search (QES). It includes custom oracle circuits and search strategies using Qiskit.

## 📂 Main Files

### `quantum_algorithms.py`

This module implements **quantum algorithms** for exploring the solution space:

- `create_exponential_graph_coloring_search(...)`: Performs Quantum Exponential Search (QES) to find a valid coloring assignment.
- `create_grover_search(...)`: Classic **Grover’s Search** using a given oracle.
- `create_quantum_counting(...)`: Constructs a circuit for **Quantum Counting**, estimating the number of valid solutions.
- `create_diffuser(n)`: Builds the standard diffuser (inversion about the mean) used in Grover-based circuits.


### `graph_coloring.py`

This file contains **three different oracles** for encoding the graph coloring problem into quantum circuits:

- `graph_coloring_oracle_sat_formula(...)`: Uses a SAT-style formulation to ensure that each node gets exactly one color and that no two adjacent nodes share the same color.
- `graph_coloring_oracle_counters_OH(...)`: Implements an oracle based on binary counters and multicontrolled logic gates.
- `graph_coloring_oracle_counters_bin(...)`: A more efficient version in terms of qubit usage, especially when the number of colors is a power of 2.


### `utils.py`

Utility functions:

- `get_extended_edges(...)`: Returns the extended set of edges including second-order neighbors.
- `print_state(...)`: Nicely formats and displays quantum state vectors with probabilities and phases using colors.

## 📓 Test Notebooks

The repository includes three Jupyter notebooks that demonstrate how to use the implemented circuits and algorithms:

- **`Quantum_Counting.ipynb`** – Demonstrates quantum counting on a graph coloring oracle.
- **`Grover_Search.ipynb`** – Applies Grover's algorithm to find valid colorings.
- **`QES.ipynb`** – Demonstrates the complete **Quantum Exponential Search** workflow.

## 🚀 Requirements

- Python 3.8+
- [Qiskit](https://qiskit.org/)
- (Optional) `termcolor` for colored state vector printing

Install dependencies:

```bash
pip install qiskit termcolor
```

## ⚠️ Notes

- The graph oracles are designed for undirected graphs.
- Modular structure allows for reuse in other quantum optimization problems.



## 📌 Authors & License

**UPCT - Universidad Politécnica de Cartagena**  
Experimental project for academic purposes. Free to use with attribution.

