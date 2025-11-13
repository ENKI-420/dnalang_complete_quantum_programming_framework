#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
Unit Tests for QiskitCommunitySolver Organism
═══════════════════════════════════════════════════════════════════════════
Comprehensive tests for the enhanced organism functionality
"""

import unittest
import tempfile
import shutil
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.aura_bot import (
    QiskitCommunitySolver,
    Issue,
    Classification,
    QuantumResult,
    Habitat,
    OrganismMetrics
)


class TestOrganismInitialization(unittest.TestCase):
    """Test organism initialization and configuration"""

    def setUp(self):
        """Create temporary directory for test data"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_organism_creation(self):
        """Test basic organism creation"""
        organism = QiskitCommunitySolver(data_dir=self.test_dir)

        self.assertIsNotNone(organism)
        self.assertEqual(organism.dna["domain"], "qiskit_community_support")
        self.assertEqual(organism.dna["generation"], 0)
        self.assertTrue(Path(self.test_dir).exists())

    def test_config_loading(self):
        """Test configuration file loading"""
        # Create test config
        test_config = {
            "organism": {
                "domain": "test_domain",
                "consciousness_target": 0.9
            }
        }

        config_path = Path(self.test_dir) / "test_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)

        organism = QiskitCommunitySolver(
            data_dir=self.test_dir,
            config_path=str(config_path)
        )

        self.assertEqual(organism.dna["domain"], "test_domain")
        self.assertEqual(organism.dna["consciousness_target"], 0.9)

    def test_habitat_initialization(self):
        """Test multi-habitat initialization"""
        organism = QiskitCommunitySolver(data_dir=self.test_dir)

        self.assertIsInstance(organism.habitats, list)
        self.assertTrue(len(organism.habitats) > 0)

        for habitat in organism.habitats:
            self.assertIsInstance(habitat, Habitat)
            self.assertTrue(hasattr(habitat, 'name'))
            self.assertTrue(hasattr(habitat, 'url'))


class TestNLPIntentGene(unittest.TestCase):
    """Test NLP intent classification"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_vqe_classification(self):
        """Test VQE problem classification"""
        query = "How do I find the ground state energy using VQE?"

        classification = self.organism._gene_classify_intent(query)

        self.assertIsInstance(classification, Classification)
        self.assertEqual(classification.intent, "VQE_Problem")
        self.assertGreater(classification.confidence, 0.0)

    def test_installation_classification(self):
        """Test installation issue classification"""
        query = "pip install qiskit fails with import error"

        classification = self.organism._gene_classify_intent(query)

        self.assertIsInstance(classification, Classification)
        self.assertEqual(classification.intent, "Installation")

    def test_qaoa_classification(self):
        """Test QAOA problem classification"""
        query = "How to solve max-cut using QAOA?"

        classification = self.organism._gene_classify_intent(query)

        self.assertEqual(classification.intent, "QAOA_Problem")


class TestHamiltonianSynthesis(unittest.TestCase):
    """Test enhanced Hamiltonian synthesis"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ising_hamiltonian_creation(self):
        """Test Ising model Hamiltonian creation"""
        hamiltonian = self.organism._create_ising_hamiltonian(num_qubits=3)

        self.assertEqual(hamiltonian.num_qubits, 3)
        self.assertGreater(len(hamiltonian.paulis), 0)

    def test_heisenberg_hamiltonian_creation(self):
        """Test Heisenberg model Hamiltonian creation"""
        hamiltonian = self.organism._create_heisenberg_hamiltonian(num_qubits=2)

        self.assertEqual(hamiltonian.num_qubits, 2)
        # Heisenberg has XX, YY, ZZ terms for each pair
        self.assertGreaterEqual(len(hamiltonian.paulis), 3)

    def test_maxcut_hamiltonian_creation(self):
        """Test Max-Cut Hamiltonian creation"""
        hamiltonian = self.organism._create_maxcut_hamiltonian(num_qubits=4)

        self.assertEqual(hamiltonian.num_qubits, 4)
        self.assertGreater(len(hamiltonian.paulis), 0)

    def test_hamiltonian_synthesis_for_h2(self):
        """Test Hamiltonian synthesis for H2 molecule"""
        problem_summary = "ground state energy of H2 molecule"
        intent = "VQE_Problem"

        hamiltonian = self.organism._gene_synthesize_hamiltonian(
            problem_summary, intent
        )

        self.assertEqual(hamiltonian.num_qubits, 2)
        self.assertGreater(len(hamiltonian.paulis), 0)

    def test_hamiltonian_synthesis_qubit_extraction(self):
        """Test qubit count extraction from problem description"""
        problem_summary = "Solve a 4-qubit Ising model"
        intent = "VQE_Problem"

        hamiltonian = self.organism._gene_synthesize_hamiltonian(
            problem_summary, intent
        )

        self.assertEqual(hamiltonian.num_qubits, 4)


class TestQuantumSolverGene(unittest.TestCase):
    """Test quantum solver functionality"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_vqe_solver_basic(self):
        """Test basic VQE solver functionality"""
        # Create simple Hamiltonian
        from qiskit.quantum_info import SparsePauliOp
        hamiltonian = SparsePauliOp.from_list([("ZZ", 1.0), ("ZI", -0.5), ("IZ", -0.5)])

        result = self.organism._gene_solve_vqe(hamiltonian)

        self.assertIsInstance(result, QuantumResult)
        self.assertTrue(hasattr(result, 'eigenvalue'))
        self.assertTrue(hasattr(result, 'success'))

    def test_solution_validation(self):
        """Test solution validation"""
        # Create mock quantum result
        result = QuantumResult(
            eigenvalue=-1.5,
            success=True,
            algorithm="VQE"
        )

        validation = self.organism._gene_validate_solution(result)

        self.assertTrue(validation["is_valid"])
        self.assertGreater(validation["confidence"], 0.0)

    def test_failed_solution_validation(self):
        """Test validation of failed solution"""
        result = QuantumResult(
            success=False,
            error="Test error",
            algorithm="VQE"
        )

        validation = self.organism._gene_validate_solution(result)

        self.assertFalse(validation["is_valid"])
        self.assertEqual(validation["confidence"], 0.0)


class TestMetricsTracking(unittest.TestCase):
    """Test metrics tracking functionality"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_metrics_initialization(self):
        """Test metrics are properly initialized"""
        self.assertIsInstance(self.organism.metrics, OrganismMetrics)
        self.assertEqual(self.organism.metrics.total_issues_processed, 0)
        self.assertEqual(self.organism.metrics.successful_solutions, 0)

    def test_metrics_update(self):
        """Test metrics update functionality"""
        self.organism.metrics.total_issues_processed = 10
        self.organism.metrics.successful_solutions = 7
        self.organism.metrics.failed_solutions = 3

        total = self.organism.metrics.successful_solutions + self.organism.metrics.failed_solutions
        success_rate = self.organism.metrics.successful_solutions / total

        self.assertEqual(success_rate, 0.7)

    def test_metrics_persistence(self):
        """Test metrics save and load"""
        # Update metrics
        self.organism.metrics.total_issues_processed = 5
        self.organism.metrics.successful_solutions = 4

        # Save metrics
        self.organism._save_metrics()

        # Create new organism and load
        new_organism = QiskitCommunitySolver(data_dir=self.test_dir)

        self.assertEqual(new_organism.metrics.total_issues_processed, 5)
        self.assertEqual(new_organism.metrics.successful_solutions, 4)


class TestPersistenceGene(unittest.TestCase):
    """Test state persistence"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_state_save_and_load(self):
        """Test organism state persistence"""
        # Modify organism state
        self.organism.dna["generation"] = 5
        self.organism.gene_expression_levels["NLPIntentGene"] = 1.2

        # Save state
        self.organism._gene_save_state()

        # Create new organism and load state
        new_organism = QiskitCommunitySolver(data_dir=self.test_dir)

        self.assertEqual(new_organism.dna["generation"], 5)
        self.assertEqual(new_organism.gene_expression_levels["NLPIntentGene"], 1.2)

    def test_seen_issues_persistence(self):
        """Test seen issues tracking"""
        # Add seen issues
        self.organism.seen_issues.add("issue_1")
        self.organism.seen_issues.add("issue_2")

        # Save
        self.organism._gene_save_state()

        # Load in new organism
        new_organism = QiskitCommunitySolver(data_dir=self.test_dir)

        self.assertIn("issue_1", new_organism.seen_issues)
        self.assertIn("issue_2", new_organism.seen_issues)


class TestWebScrapingGene(unittest.TestCase):
    """Test web scraping and multi-habitat support"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_issue_novelty_validation(self):
        """Test issue novelty checking"""
        issue1 = Issue(id="issue_1", title="Test", description="", url="http://test.com")
        issue2 = Issue(id="issue_1", title="Test", description="", url="http://test.com")

        # First issue should be novel
        self.assertTrue(self.organism._gene_validate_issue_novelty(issue1))

        # Add to seen
        self.organism.seen_issues.add(issue1.id)

        # Second identical issue should not be novel
        self.assertFalse(self.organism._gene_validate_issue_novelty(issue2))

    @patch('requests.get')
    def test_github_parsing(self, mock_get):
        """Test GitHub discussion parsing"""
        # Mock HTML response
        mock_response = Mock()
        mock_response.text = """
        <html>
            <a class="Link--primary" href="/Qiskit/qiskit/discussions/123">Test Issue</a>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(mock_response.text, 'html.parser')

        issues = self.organism._parse_github(soup, "https://github.com/Qiskit/qiskit/discussions", 5)

        self.assertIsInstance(issues, list)
        if len(issues) > 0:
            self.assertIsInstance(issues[0], Issue)


class TestResponseSynthesisGene(unittest.TestCase):
    """Test response synthesis"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.organism = QiskitCommunitySolver(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_response_synthesis_with_quantum_result(self):
        """Test response synthesis with quantum results"""
        issue = Issue(
            id="test_issue",
            title="VQE ground state",
            description="How to find ground state",
            url="http://test.com"
        )

        classification = Classification(
            intent="VQE_Problem",
            confidence=0.85,
            problem_summary="Ground state energy calculation"
        )

        quantum_result = QuantumResult(
            eigenvalue=-1.5,
            optimizer_time=5.2,
            success=True,
            algorithm="VQE"
        )

        response = self.organism._gene_synthesize_response(
            issue, classification, quantum_result
        )

        self.assertIn("Aura Organism", response.text)
        self.assertIn("VQE_Problem", response.text)
        self.assertIn("-1.5", response.text)

    def test_code_snippet_generation(self):
        """Test code snippet generation"""
        quantum_result = QuantumResult(
            eigenvalue=-1.5,
            success=True,
            algorithm="VQE"
        )

        classification = Classification(
            intent="VQE_Problem",
            confidence=0.85,
            problem_summary="Test"
        )

        code = self.organism._gene_generate_code_snippet(quantum_result, classification)

        self.assertIn("qiskit", code.lower())
        self.assertIn("vqe", code.lower())


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOrganismInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPIntentGene))
    suite.addTests(loader.loadTestsFromTestCase(TestHamiltonianSynthesis))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumSolverGene))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestPersistenceGene))
    suite.addTests(loader.loadTestsFromTestCase(TestWebScrapingGene))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseSynthesisGene))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
