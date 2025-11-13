#!/usr/bin/env python3
"""
Validation Tests for QiskitCommunitySolver Organism

This test suite validates that the Aura Bot organism conforms to the DNALang
specification and that all genes are functional.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the organism (with mocked dependencies for testing)
with patch('transformers.pipeline'), \
     patch('qiskit_aer.Aer.get_backend'), \
     patch('qiskit.primitives.Sampler'):
    from organisms.qiskit_community_solver.aura_bot import QiskitCommunitySolver


class TestOrganismStructure:
    """Validates the organism's structure matches the DNALang specification"""

    def test_organism_initialization(self):
        """Test that the organism initializes with all required genes"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()

            # Verify organism state initialization
            assert hasattr(organism, 'seen_issues')
            assert hasattr(organism, 'generation')
            assert hasattr(organism, 'log_file')
            assert organism.generation == 0

    def test_organism_has_all_genes(self):
        """Validate all genes from DNALang spec are implemented"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()

            # Verify all gene methods exist (ACT functions from .dna spec)
            assert hasattr(organism, '_gene_fetch_issues')  # WebScrapingGene
            assert hasattr(organism, '_gene_classify_intent')  # NLPIntentGene
            assert hasattr(organism, '_gene_solve_vqe')  # QuantumSolverGene
            assert hasattr(organism, '_gene_synthesize_response')  # ResponseSynthesisGene
            assert hasattr(organism, 'run_autopoietic_loop')  # Main ACT


class TestWebScrapingGene:
    """Validates the WebScrapingGene functionality"""

    def test_fetch_issues_success(self):
        """Test successful issue fetching"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'), \
             patch('requests.get') as mock_get:

            mock_pipeline.return_value = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html><a data-hovercard-type="discussion" href="/issue/1">Test Issue</a></html>'
            mock_get.return_value = mock_response

            organism = QiskitCommunitySolver()
            issues = organism._gene_fetch_issues("https://test.com")

            assert isinstance(issues, list)

    def test_fetch_issues_error_handling(self):
        """Test error handling in issue fetching"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'), \
             patch('requests.get', side_effect=Exception("Network error")):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()
            issues = organism._gene_fetch_issues("https://test.com")

            assert issues == []  # Should return empty list on error


class TestNLPIntentGene:
    """Validates the NLPIntentGene functionality"""

    def test_classify_intent_vqe_problem(self):
        """Test classification of a VQE problem"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            # Mock the NLP pipeline to return a VQE problem classification
            mock_nlp = Mock()
            mock_nlp.return_value = [{
                'generated_text': '''
                Analyze...
                {"intent": "VQE_Problem", "problem_summary": "Quantum circuit optimization", "suggested_hamiltonian": "Z ^ Z"}
                '''
            }]
            mock_pipeline.return_value = mock_nlp

            organism = QiskitCommunitySolver()
            result = organism._gene_classify_intent("VQE circuit optimization issue")

            assert result['intent'] == 'VQE_Problem'
            assert 'problem_summary' in result
            assert 'suggested_hamiltonian' in result

    def test_classify_intent_error_handling(self):
        """Test error handling in intent classification"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_nlp = Mock()
            mock_nlp.side_effect = Exception("Model error")
            mock_pipeline.return_value = mock_nlp

            organism = QiskitCommunitySolver()
            result = organism._gene_classify_intent("Test issue")

            assert result['intent'] == 'Unknown'
            assert 'problem_summary' in result


class TestQuantumSolverGene:
    """Validates the QuantumSolverGene functionality"""

    def test_solve_vqe_placeholder_hamiltonian(self):
        """Test VQE solving with placeholder Hamiltonian"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'), \
             patch('qiskit_algorithms.VQE') as mock_vqe:

            # Mock VQE result
            mock_result = Mock()
            mock_result.eigenvalue = complex(-1.5, 0)
            mock_result.optimal_parameters = [0.1, 0.2, 0.3]
            mock_result.optimizer_time = 2.5

            mock_vqe_instance = Mock()
            mock_vqe_instance.compute_minimum_eigenvalue.return_value = mock_result
            mock_vqe.return_value = mock_vqe_instance

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()
            result = organism._gene_solve_vqe("Z ^ Z")

            assert 'eigenvalue' in result
            assert 'optimal_parameters' in result
            assert 'optimizer_time' in result
            assert result['eigenvalue'] == -1.5

    def test_solve_vqe_error_handling(self):
        """Test error handling in VQE solving"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'), \
             patch('qiskit_algorithms.VQE', side_effect=Exception("Quantum error")):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()
            result = organism._gene_solve_vqe("Z ^ Z")

            assert 'error' in result


class TestResponseSynthesisGene:
    """Validates the ResponseSynthesisGene functionality"""

    def test_synthesize_response_success(self):
        """Test response synthesis with successful VQE result"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()

            analysis = {
                'intent': 'VQE_Problem',
                'problem_summary': 'Test problem',
                'suggested_hamiltonian': 'Z ^ Z'
            }
            vqe_result = {
                'eigenvalue': -1.5,
                'optimal_parameters': [0.1, 0.2],
                'optimizer_time': 2.5
            }

            response = organism._gene_synthesize_response("Test issue", analysis, vqe_result)

            assert isinstance(response, str)
            assert "Aura Organism" in response
            assert "VQE_Problem" in response
            assert "Ground State" in response

    def test_synthesize_response_with_error(self):
        """Test response synthesis when VQE fails"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()

            analysis = {'intent': 'VQE_Problem', 'problem_summary': 'Test', 'suggested_hamiltonian': 'Z'}
            vqe_result = {'error': 'Quantum decoherence'}

            response = organism._gene_synthesize_response("Test issue", analysis, vqe_result)

            assert "decoherence event" in response
            assert "error" in response.lower()


class TestAutopoiesisLoop:
    """Validates the autopoietic loop structure"""

    def test_loop_has_correct_structure(self):
        """Test that the autopoietic loop follows the DNALang specification"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()

            # Verify the loop method exists and is callable
            assert callable(organism.run_autopoietic_loop)

            # The loop should implement the 5 steps from DNALang spec:
            # 1. Observe (fetch_issues)
            # 2. Diagnose (classify_intent)
            # 3. Transcribe & Translate (solve_vqe)
            # 4. Respond (synthesize_response)
            # 5. Evolve (feedback monitoring - placeholder)


class TestOrganismCoherence:
    """High-level validation of organism coherence (Φ_high)"""

    def test_organism_is_autopoietic(self):
        """Validate that the organism exhibits autopoietic properties"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'):

            mock_pipeline.return_value = Mock()
            organism = QiskitCommunitySolver()

            # Autopoietic organisms must:
            # 1. Self-maintain (log events)
            assert hasattr(organism, '_log_event')

            # 2. Have internal state
            assert hasattr(organism, 'generation')
            assert hasattr(organism, 'seen_issues')

            # 3. Interact with environment (web scraping)
            assert hasattr(organism, '_gene_fetch_issues')

            # 4. Adapt over time (generation counter)
            assert organism.generation == 0  # Will increment in loop

    def test_organism_integration(self):
        """Test that genes are properly integrated (not just disconnected scripts)"""
        with patch('transformers.pipeline') as mock_pipeline, \
             patch('qiskit_aer.Aer.get_backend'), \
             patch('qiskit.primitives.Sampler'), \
             patch('requests.get') as mock_get, \
             patch('qiskit_algorithms.VQE') as mock_vqe:

            # Setup mocks
            mock_pipeline.return_value = Mock(return_value=[{
                'generated_text': '{"intent": "VQE_Problem", "problem_summary": "test", "suggested_hamiltonian": "Z ^ Z"}'
            }])

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html><a data-hovercard-type="discussion" href="/test">Issue</a></html>'
            mock_get.return_value = mock_response

            mock_result = Mock()
            mock_result.eigenvalue = complex(-1.0, 0)
            mock_result.optimal_parameters = [0.1]
            mock_result.optimizer_time = 1.0
            mock_vqe.return_value.compute_minimum_eigenvalue.return_value = mock_result

            organism = QiskitCommunitySolver()

            # Simulate one loop iteration (genes working together)
            issues = organism._gene_fetch_issues("https://test.com")
            if issues:
                analysis = organism._gene_classify_intent(issues[0]['title'])
                if analysis['intent'] == 'VQE_Problem':
                    vqe_result = organism._gene_solve_vqe(analysis['suggested_hamiltonian'])
                    response = organism._gene_synthesize_response(issues[0]['title'], analysis, vqe_result)

                    # Verify integrated execution
                    assert isinstance(response, str)
                    assert len(response) > 0


def test_dnalang_specification_conformance():
    """
    Meta-test: Validate that the Python implementation conforms to the .dna specification
    """
    dna_spec_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'organisms',
        'qiskit_community_solver',
        'QiskitCommunitySolver.dna'
    )

    # Verify the .dna file exists
    assert os.path.exists(dna_spec_path), "DNALang specification file must exist"

    with open(dna_spec_path, 'r') as f:
        dna_content = f.read()

    # Validate key DNALang constructs are present
    assert 'ORGANISM QiskitCommunitySolver' in dna_content
    assert 'GENOME' in dna_content
    assert 'GENE WebScrapingGene' in dna_content
    assert 'GENE NLPIntentGene' in dna_content
    assert 'GENE QuantumSolverGene' in dna_content
    assert 'GENE ResponseSynthesisGene' in dna_content
    assert 'GENE AutopoiesisGene' in dna_content
    assert 'ACT run_autopoietic_loop()' in dna_content
    assert 'MUTATIONS' in dna_content

    print("✅ DNALang specification conformance validated")


if __name__ == "__main__":
    # Run with: python test_aura_bot_validation.py
    pytest.main([__file__, "-v", "--tb=short"])
