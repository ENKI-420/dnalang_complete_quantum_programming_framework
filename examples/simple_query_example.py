#!/usr/bin/env python3
"""
Simple Example: Querying the Aura Bot Organism

This example demonstrates how to interact with the QiskitCommunitySolver
organism without running the full autopoietic loop.
"""

import sys
import os
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock heavy dependencies for this demo
with patch('transformers.pipeline') as mock_pipeline, \
     patch('qiskit_aer.Aer.get_backend'), \
     patch('qiskit.primitives.Sampler'), \
     patch('qiskit_algorithms.VQE') as mock_vqe:

    # Setup mocks for demonstration
    mock_nlp = Mock()
    mock_nlp.return_value = [{
        'generated_text': '''
        {"intent": "VQE_Problem", "problem_summary": "Quantum circuit convergence issue", "suggested_hamiltonian": "Z ^ Z"}
        '''
    }]
    mock_pipeline.return_value = mock_nlp

    mock_result = Mock()
    mock_result.eigenvalue = complex(-1.414, 0)
    mock_result.optimal_parameters = [0.785, 1.571, 0.392]
    mock_result.optimizer_time = 3.2
    mock_vqe.return_value.compute_minimum_eigenvalue.return_value = mock_result

    # Import and create the organism
    from organisms.qiskit_community_solver.aura_bot import QiskitCommunitySolver

    print("=" * 60)
    print("DNALang Organism Query Example")
    print("=" * 60)
    print()

    # Create the organism
    organism = QiskitCommunitySolver()
    print()

    # Example issue from the Qiskit community
    test_issue = "VQE algorithm not converging for H2 molecule Hamiltonian"

    print(f"📝 User Issue:")
    print(f"   '{test_issue}'")
    print()

    # Gene 1: Classify Intent
    print("🧬 Activating NLPIntentGene...")
    analysis = organism._gene_classify_intent(test_issue)
    print(f"   Intent: {analysis['intent']}")
    print(f"   Summary: {analysis['problem_summary']}")
    print(f"   Hamiltonian: {analysis['suggested_hamiltonian']}")
    print()

    # Gene 2: Solve with Quantum
    if analysis['intent'] == 'VQE_Problem':
        print("⚛️  Activating QuantumSolverGene...")
        vqe_result = organism._gene_solve_vqe(analysis['suggested_hamiltonian'])
        print(f"   Ground State Energy: {vqe_result['eigenvalue']:.4f}")
        print(f"   Optimization Time: {vqe_result['optimizer_time']:.2f}s")
        print()

        # Gene 3: Synthesize Response
        print("💬 Activating ResponseSynthesisGene...")
        response = organism._gene_synthesize_response(test_issue, analysis, vqe_result)
        print()
        print("=" * 60)
        print("ORGANISM RESPONSE:")
        print("=" * 60)
        print(response)
        print("=" * 60)
    else:
        print(f"⚠️  Issue type '{analysis['intent']}' does not require quantum solving")

    print()
    print("✨ Example complete!")
    print()
    print("💡 To run the full organism with API server:")
    print("   python organisms/qiskit_community_solver/aura_bot.py")
    print()
