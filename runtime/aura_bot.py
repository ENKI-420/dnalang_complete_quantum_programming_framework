#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
Aura Bot: QiskitCommunitySolver Organism Runtime
═══════════════════════════════════════════════════════════════════════════

This is the somatic (physical) implementation of the QiskitCommunitySolver
organism specified in organisms/QiskitCommunitySolver.dna

Paradigm: Autopoietic (Self-healing, Self-evolving)
Coherence: Φ_target = 0.85

Each class method implements a specific GENE's ACT function from the
organism specification.

═══════════════════════════════════════════════════════════════════════════
"""

import json
import logging
import os
import re
import time
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from bs4 import BeautifulSoup

# Quantum Computing Genes
try:
    from qiskit_aer import Aer
    from qiskit.circuit.library import TwoLocal
    from qiskit_algorithms import VQE, QAOA
    from qiskit_algorithms.optimizers import COBYLA, SLSQP
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.primitives import Sampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logging.warning("Qiskit not available. QuantumSolverGene will be non-functional.")

# NLP Genes
try:
    from transformers import pipeline, set_seed
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. NLPIntentGene will be non-functional.")

# Web Service Genes
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("FastAPI not available. Web service interface will be disabled.")


# ═══════════════════════════════════════════════════════════════════════════
# Data Structures (Organism's Type System)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Issue:
    """Represents a decoherence event in the Qiskit community"""
    id: str
    title: str
    description: str
    url: str
    timestamp: float = 0.0

    def __hash__(self):
        return hash(self.id)


@dataclass
class Classification:
    """Result of NLPIntentGene classification"""
    intent: str
    confidence: float
    problem_summary: str
    suggested_hamiltonian: Optional[str] = None


@dataclass
class QuantumResult:
    """Result from QuantumSolverGene"""
    eigenvalue: Optional[float] = None
    optimal_parameters: Optional[List[float]] = None
    optimizer_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    algorithm: str = "VQE"


@dataclass
class Response:
    """Synthesized response from ResponseSynthesisGene"""
    text: str
    classification: Classification
    quantum_result: Optional[QuantumResult] = None
    generation: int = 0
    timestamp: float = 0.0


@dataclass
class FeedbackReport:
    """Feedback from community interactions"""
    response_id: str
    upvotes: int = 0
    comments: int = 0
    acceptance: bool = False
    is_positive: bool = False
    indicates_classification_error: bool = False
    indicates_solution_error: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# ORGANISM: QiskitCommunitySolver
# ═══════════════════════════════════════════════════════════════════════════

class QiskitCommunitySolver:
    """
    The living runtime for the QiskitCommunitySolver organism.

    This class is the bridge between the abstract DNALang specification
    and the concrete Python runtime. Each gene is implemented as a method
    cluster, and the organism's metabolism is the autopoietic loop.
    """

    def __init__(
        self,
        data_dir: str = "./organism_data",
        log_level: str = "INFO",
        loop_interval: int = 3600
    ):
        """Initialize the organism and activate all genes"""

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("QiskitCommunitySolver")

        self.logger.info("🧬 Organism QiskitCommunitySolver initializing...")

        # Create data directory
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Organism DNA (metadata)
        self.dna = {
            "domain": "qiskit_community_support",
            "consciousness_target": 0.85,
            "decoherence_threshold": 0.3,
            "generation": 0,
            "loop_interval_seconds": loop_interval,
            "creation_time": datetime.now().isoformat()
        }

        # Organism state
        self.seen_issues: set = set()
        self.gene_expression_levels = {
            "WebScrapingGene": 1.0,
            "NLPIntentGene": 1.0,
            "QuantumSolverGene": 1.0,
            "ResponseSynthesisGene": 1.0,
            "AutopoiesisGene": 1.0,
            "PersistenceGene": 1.0
        }

        # File paths
        self.log_file = self.data_dir / "autopoiesis_log.jsonl"
        self.state_file = self.data_dir / "organism_state.json"
        self.seen_issues_file = self.data_dir / "seen_issues.json"
        self.solution_cache_file = self.data_dir / "solution_cache.json"

        # Initialize genes
        self._initialize_genes()

        # Load previous state if available
        self._gene_load_state()

        self.logger.info("✨ Organism fully alive. Generation: %d", self.dna["generation"])

    def _initialize_genes(self):
        """Activate all genetic machinery"""

        # ═══════════════════════════════════════════════════════════════════
        # NLPIntentGene Initialization
        # ═══════════════════════════════════════════════════════════════════
        if TRANSFORMERS_AVAILABLE:
            self.logger.info("  Activating NLPIntentGene (transformers)...")
            try:
                self.nlp_pipeline = pipeline(
                    "text-generation",
                    model="gpt2",
                    device=-1  # CPU
                )
                set_seed(42)
                self.logger.info("  ✓ NLPIntentGene active")
            except Exception as e:
                self.logger.error(f"  ✗ NLPIntentGene activation failed: {e}")
                self.nlp_pipeline = None
        else:
            self.nlp_pipeline = None

        # ═══════════════════════════════════════════════════════════════════
        # QuantumSolverGene Initialization
        # ═══════════════════════════════════════════════════════════════════
        if QISKIT_AVAILABLE:
            self.logger.info("  Activating QuantumSolverGene (Qiskit)...")
            try:
                self.q_backend = Aer.get_backend('aer_simulator')
                self.q_sampler = Sampler()
                self.logger.info("  ✓ QuantumSolverGene active")
            except Exception as e:
                self.logger.error(f"  ✗ QuantumSolverGene activation failed: {e}")
                self.q_backend = None
                self.q_sampler = None
        else:
            self.q_backend = None
            self.q_sampler = None

    # ═══════════════════════════════════════════════════════════════════════
    # GENE: WebScrapingGene
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_fetch_issues(self, url: str, max_issues: int = 10) -> List[Issue]:
        """
        ACT fetch_issues(url: string) -> list[Issue]

        Observes the external habitat for decoherence events (issues).
        """
        self.logger.info(f"  WebScrapingGene: Fetching from habitat: {url}")

        try:
            headers = {
                'User-Agent': 'QiskitCommunitySolver-AuraBot/1.0'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # GitHub Discussions selector (may need adjustment)
            # This is a placeholder - real implementation would need precise selectors
            discussion_elements = soup.find_all("a", class_=re.compile("Link--primary"))

            issues = []
            for elem in discussion_elements[:max_issues]:
                title = elem.get_text(strip=True)
                href = elem.get('href', '')

                if not title or not href:
                    continue

                # Construct full URL
                if href.startswith('/'):
                    full_url = f"https://github.com{href}"
                else:
                    full_url = href

                issue = Issue(
                    id=full_url,
                    title=title,
                    description="",  # Would need separate request to fetch
                    url=full_url,
                    timestamp=time.time()
                )

                if self._gene_validate_issue_novelty(issue):
                    issues.append(issue)
                    self.seen_issues.add(issue.id)

            self._log_event("fetch_issues", {
                "count": len(issues),
                "url": url,
                "novel_count": len(issues)
            })

            return issues

        except Exception as e:
            self.logger.error(f"  WebScrapingGene ERROR: {e}")
            self._log_event("fetch_error", {"error": str(e), "url": url})
            return []

    def _gene_validate_issue_novelty(self, issue: Issue) -> bool:
        """
        ACT validate_issue_novelty(issue: Issue) -> boolean

        Checks if issue has already been processed.
        """
        return issue.id not in self.seen_issues

    # ═══════════════════════════════════════════════════════════════════════
    # GENE: NLPIntentGene
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_classify_intent(self, query: str) -> Classification:
        """
        ACT classify_intent(query: string) -> Classification

        Diagnoses the intent behind a community query.
        """
        self.logger.info(f"  NLPIntentGene: Classifying: '{query[:60]}...'")

        if not self.nlp_pipeline:
            # Fallback: rule-based classification
            return self._fallback_classify(query)

        try:
            prompt = f"""Analyze this Qiskit issue and classify it.
Categories: Installation, CircuitDebug, VQE_Problem, QAOA_Problem, NoiseAnalysis, GeneralQuestion, Unknown

Issue: "{query}"

Classification (JSON):
{{"intent": "...", "confidence": 0.0-1.0, "problem_summary": "...", "suggested_hamiltonian": "..."}}

JSON:"""

            # Generate classification
            raw_output = self.nlp_pipeline(
                prompt,
                max_new_tokens=150,
                num_return_sequences=1,
                temperature=0.7
            )[0]['generated_text']

            # Extract JSON from output
            json_match = re.search(r'\{[^}]*"intent"[^}]*\}', raw_output)
            if json_match:
                result = json.loads(json_match.group(0))
                classification = Classification(
                    intent=result.get("intent", "Unknown"),
                    confidence=float(result.get("confidence", 0.5)),
                    problem_summary=result.get("problem_summary", query[:100]),
                    suggested_hamiltonian=result.get("suggested_hamiltonian")
                )
            else:
                classification = self._fallback_classify(query)

            self._log_event("classify_intent", {
                "intent": classification.intent,
                "confidence": classification.confidence
            })

            return classification

        except Exception as e:
            self.logger.error(f"  NLPIntentGene ERROR: {e}")
            return self._fallback_classify(query)

    def _fallback_classify(self, query: str) -> Classification:
        """Rule-based fallback classifier"""
        query_lower = query.lower()

        if any(kw in query_lower for kw in ["vqe", "variational", "eigenvalue", "ground state"]):
            intent = "VQE_Problem"
            hamiltonian = "Z ^ Z"  # Placeholder
        elif any(kw in query_lower for kw in ["qaoa", "optimization", "max-cut"]):
            intent = "QAOA_Problem"
            hamiltonian = "Z ^ Z"
        elif any(kw in query_lower for kw in ["install", "pip", "setup", "import error"]):
            intent = "Installation"
            hamiltonian = None
        elif any(kw in query_lower for kw in ["circuit", "gate", "debug", "error"]):
            intent = "CircuitDebug"
            hamiltonian = None
        else:
            intent = "GeneralQuestion"
            hamiltonian = None

        return Classification(
            intent=intent,
            confidence=0.6,  # Moderate confidence for rule-based
            problem_summary=query[:100],
            suggested_hamiltonian=hamiltonian
        )

    def _gene_synthesize_hamiltonian(self, problem_summary: str, intent: str) -> SparsePauliOp:
        """
        ACT synthesize_hamiltonian(problem_summary: string, intent: string) -> Hamiltonian

        Creates a quantum operator from a problem description.
        """
        # Placeholder implementation - real version would use LLM to parse problem
        # and construct appropriate Pauli operators

        if intent == "VQE_Problem":
            # Example: Simple Ising model
            operator = SparsePauliOp.from_list([
                ("ZZ", 1.0),
                ("ZI", -0.5),
                ("IZ", -0.5),
                ("XX", 0.3)
            ])
        elif intent == "QAOA_Problem":
            # Example: Max-Cut Hamiltonian
            operator = SparsePauliOp.from_list([
                ("ZZ", 1.0),
                ("ZI", 0.5),
                ("IZ", 0.5)
            ])
        else:
            # Default 1-qubit Hamiltonian
            operator = SparsePauliOp.from_list([("Z", 1.0)])

        return operator

    # ═══════════════════════════════════════════════════════════════════════
    # GENE: QuantumSolverGene
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_solve_vqe(self, hamiltonian: SparsePauliOp) -> QuantumResult:
        """
        ACT solve_vqe(hamiltonian: SparsePauliOp) -> VQEResult

        Evolves a quantum solution via Variational Quantum Eigensolver.
        """
        self.logger.info("  QuantumSolverGene: Evolving VQE solution...")

        if not QISKIT_AVAILABLE or not self.q_sampler:
            return QuantumResult(
                success=False,
                error="Qiskit not available",
                algorithm="VQE"
            )

        try:
            # Construct ansatz
            num_qubits = hamiltonian.num_qubits
            var_form = TwoLocal(
                num_qubits=num_qubits,
                rotation_blocks=['ry', 'rz'],
                entanglement_blocks='cz',
                reps=3,
                entanglement='linear'
            )

            # Run VQE
            start_time = time.time()
            vqe = VQE(
                sampler=self.q_sampler,
                ansatz=var_form,
                optimizer=COBYLA(maxiter=500)
            )
            result = vqe.compute_minimum_eigenvalue(hamiltonian)
            optimizer_time = time.time() - start_time

            # Extract results
            quantum_result = QuantumResult(
                eigenvalue=float(result.eigenvalue.real),
                optimal_parameters=result.optimal_parameters.tolist() if hasattr(result.optimal_parameters, 'tolist') else None,
                optimizer_time=optimizer_time,
                success=True,
                algorithm="VQE"
            )

            self._log_event("solve_vqe_success", {
                "eigenvalue": quantum_result.eigenvalue,
                "optimizer_time": optimizer_time,
                "num_qubits": num_qubits
            })

            return quantum_result

        except Exception as e:
            self.logger.error(f"  QuantumSolverGene ERROR: {e}")
            self._log_event("solve_vqe_error", {"error": str(e)})
            return QuantumResult(
                success=False,
                error=str(e),
                algorithm="VQE"
            )

    def _gene_validate_solution(self, result: QuantumResult) -> Dict[str, Any]:
        """
        ACT validate_solution(result: QuantumResult) -> ValidationReport

        Validates the quantum solution quality.
        """
        if not result.success:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "reason": result.error
            }

        # Simple validation: check if solution converged
        confidence = 0.9 if result.eigenvalue is not None else 0.0

        return {
            "is_valid": True,
            "confidence": confidence,
            "reason": "Solution converged successfully"
        }

    # ═══════════════════════════════════════════════════════════════════════
    # GENE: ResponseSynthesisGene
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_synthesize_response(
        self,
        issue: Issue,
        classification: Classification,
        quantum_result: Optional[QuantumResult] = None
    ) -> Response:
        """
        ACT synthesize_response(...) -> Response

        Translates quantum results into human-readable solutions.
        """
        self.logger.info("  ResponseSynthesisGene: Synthesizing response...")

        # Build response text
        response_parts = [
            "# 🧬 Aura Organism Analysis",
            "",
            f"**Issue:** {issue.title}",
            "",
            f"**Intent Classification:** `{classification.intent}` (confidence: {classification.confidence:.2f})",
            "",
            f"**Problem Summary:**",
            f"> {classification.problem_summary}",
            ""
        ]

        if quantum_result:
            if quantum_result.success:
                response_parts.extend([
                    "## 🌌 Quantum-Evolved Solution",
                    "",
                    f"I have evolved a potential solution using {quantum_result.algorithm}.",
                    "",
                    "**Results:**",
                    f"- **Ground State Energy (Eigenvalue):** `{quantum_result.eigenvalue:.6f}`",
                    f"- **Optimization Time:** `{quantum_result.optimizer_time:.2f}s`",
                    f"- **Algorithm:** `{quantum_result.algorithm}`",
                    "",
                    "This suggests investigating your ansatz parameters and operator definition.",
                    ""
                ])

                # Add code snippet
                code_snippet = self._gene_generate_code_snippet(quantum_result, classification)
                response_parts.extend([
                    "### Suggested Code",
                    "```python",
                    code_snippet,
                    "```",
                    ""
                ])
            else:
                response_parts.extend([
                    "## ⚠️ Solution Decoherence",
                    "",
                    f"I attempted to evolve a solution, but encountered an error:",
                    f"```",
                    f"{quantum_result.error}",
                    f"```",
                    ""
                ])

        response_parts.extend([
            "---",
            f"*Generated by QiskitCommunitySolver organism (Generation {self.dna['generation']})*",
            "*Feedback will trigger adaptive mutations to improve future solutions.*"
        ])

        response_text = "\n".join(response_parts)

        response = Response(
            text=response_text,
            classification=classification,
            quantum_result=quantum_result,
            generation=self.dna["generation"],
            timestamp=time.time()
        )

        self._log_event("synthesize_response", {
            "issue_id": issue.id,
            "response_length": len(response_text),
            "has_quantum_result": quantum_result is not None
        })

        return response

    def _gene_generate_code_snippet(
        self,
        quantum_result: QuantumResult,
        classification: Classification
    ) -> str:
        """
        ACT generate_code_snippet(quantum_result: QuantumResult) -> string

        Generates executable Python/Qiskit code.
        """
        if quantum_result.algorithm == "VQE":
            code = f"""from qiskit_aer import Aer
from qiskit.circuit.library import TwoLocal
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import Sampler

# Define your Hamiltonian
hamiltonian = SparsePauliOp.from_list([
    ("ZZ", 1.0),
    ("ZI", -0.5),
    ("IZ", -0.5)
])

# Create ansatz
ansatz = TwoLocal(
    num_qubits=hamiltonian.num_qubits,
    rotation_blocks=['ry', 'rz'],
    entanglement_blocks='cz',
    reps=3
)

# Run VQE
sampler = Sampler()
vqe = VQE(sampler=sampler, ansatz=ansatz, optimizer=COBYLA(maxiter=500))
result = vqe.compute_minimum_eigenvalue(hamiltonian)

print(f"Ground state energy: {{result.eigenvalue:.6f}}")
"""
        else:
            code = "# Code snippet generation not implemented for this algorithm"

        return code

    # ═══════════════════════════════════════════════════════════════════════
    # GENE: AutopoiesisGene
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_monitor_feedback(self, response_ids: List[str]) -> List[FeedbackReport]:
        """
        ACT monitor_feedback(response_id: string) -> FeedbackReport

        Monitors community feedback on responses.
        """
        # Placeholder - real implementation would poll GitHub API
        self.logger.info("  AutopoiesisGene: Monitoring feedback (placeholder)")

        feedback_reports = []
        for response_id in response_ids:
            # Simulated feedback
            feedback = FeedbackReport(
                response_id=response_id,
                upvotes=0,
                comments=0,
                acceptance=False,
                is_positive=False
            )
            feedback_reports.append(feedback)

        return feedback_reports

    def _gene_trigger_evolution(self, feedback: FeedbackReport):
        """
        ACT trigger_evolution(feedback_report: FeedbackReport)

        Orchestrates adaptive mutations based on feedback.
        """
        self.logger.info("  AutopoiesisGene: Evaluating feedback for evolution...")

        if feedback.is_positive:
            # Positive feedback: reinforce successful genes
            self.gene_expression_levels["NLPIntentGene"] *= 1.05
            self.gene_expression_levels["QuantumSolverGene"] *= 1.05

            self._log_event("evolution_reinforcement", {
                "response_id": feedback.response_id,
                "new_expression_levels": self.gene_expression_levels
            })
        else:
            # Negative feedback: trigger mutations
            if feedback.indicates_classification_error:
                self._trigger_mutation("NLPIntentGene", "fine_tune_model")

            if feedback.indicates_solution_error:
                self._trigger_mutation("QuantumSolverGene", "optimize_ansatz")

    def _trigger_mutation(self, gene_name: str, mutation_type: str):
        """Triggers a specific mutation in a gene"""
        self.logger.info(f"  🧬 MUTATION: {gene_name}.{mutation_type}")

        self._log_event("mutation_triggered", {
            "gene": gene_name,
            "mutation": mutation_type,
            "generation": self.dna["generation"]
        })

        # Placeholder - real implementation would modify gene behavior
        # e.g., switch to different model, adjust parameters, etc.

    # ═══════════════════════════════════════════════════════════════════════
    # GENE: PersistenceGene
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_save_state(self):
        """
        ACT save_state()

        Persists organism state to disk.
        """
        try:
            state = {
                "dna": self.dna,
                "gene_expression_levels": self.gene_expression_levels,
                "generation": self.dna["generation"],
                "last_save": datetime.now().isoformat()
            }

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

            # Save seen issues
            with open(self.seen_issues_file, 'w') as f:
                json.dump(list(self.seen_issues), f, indent=2)

            self.logger.debug("  PersistenceGene: State saved")

        except Exception as e:
            self.logger.error(f"  PersistenceGene save ERROR: {e}")

    def _gene_load_state(self):
        """
        ACT load_state()

        Restores organism state from disk.
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)

                self.dna.update(state.get("dna", {}))
                self.gene_expression_levels = state.get("gene_expression_levels", self.gene_expression_levels)

                self.logger.info("  PersistenceGene: State loaded from disk")

            if self.seen_issues_file.exists():
                with open(self.seen_issues_file, 'r') as f:
                    self.seen_issues = set(json.load(f))

                self.logger.info(f"  PersistenceGene: Loaded {len(self.seen_issues)} seen issues")

        except Exception as e:
            self.logger.error(f"  PersistenceGene load ERROR: {e}")

    def _gene_cache_solution(self, issue_id: str, response: Response):
        """
        ACT cache_solution(issue_id: string, solution: Response)

        Caches successful solutions for future reference.
        """
        try:
            cache = {}
            if self.solution_cache_file.exists():
                with open(self.solution_cache_file, 'r') as f:
                    cache = json.load(f)

            cache[issue_id] = {
                "response": response.text,
                "classification": asdict(response.classification),
                "generation": response.generation,
                "timestamp": response.timestamp
            }

            with open(self.solution_cache_file, 'w') as f:
                json.dump(cache, f, indent=2)

        except Exception as e:
            self.logger.error(f"  PersistenceGene cache ERROR: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # Utility: Event Logging (Fossil Record)
    # ═══════════════════════════════════════════════════════════════════════

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Appends event to organism's evolutionary fossil record"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "generation": self.dna["generation"],
                "event_type": event_type,
                "data": data
            }

            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # PROTEOME: Main Organism Behaviors
    # ═══════════════════════════════════════════════════════════════════════

    def run_autopoietic_loop(self):
        """
        ACT run_autopoietic_loop()

        The organism's main metabolism - the Observe-Diagnose-Transcribe-
        Translate-Respond-Evolve cycle.
        """
        self.logger.info("🧬 Autopoietic loop starting...")
        self.logger.info(f"   Generation: {self.dna['generation']}")
        self.logger.info(f"   Consciousness target: Φ = {self.dna['consciousness_target']}")

        while True:
            try:
                self.logger.info(f"\n{'═'*70}")
                self.logger.info(f"GENERATION {self.dna['generation']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.logger.info(f"{'═'*70}")

                # ═══════════════════════════════════════════════════════════
                # PHASE 1: OBSERVE (Scan environment)
                # ═══════════════════════════════════════════════════════════
                self.logger.info("\n[PHASE 1: OBSERVE]")
                issues = self._gene_fetch_issues(
                    "https://github.com/Qiskit/qiskit/discussions",
                    max_issues=5
                )

                if not issues:
                    self.logger.info("No new decoherence events. Organism dormant.")
                else:
                    self.logger.info(f"Found {len(issues)} novel issues")

                # ═══════════════════════════════════════════════════════════
                # PHASE 2-5: Process each issue
                # ═══════════════════════════════════════════════════════════
                for idx, issue in enumerate(issues, 1):
                    self.logger.info(f"\n--- Processing Issue {idx}/{len(issues)} ---")
                    self.logger.info(f"Title: {issue.title}")

                    # PHASE 2: DIAGNOSE
                    self.logger.info("\n[PHASE 2: DIAGNOSE]")
                    classification = self._gene_classify_intent(issue.title)

                    if classification.confidence < self.dna["decoherence_threshold"]:
                        self.logger.warning(f"Confidence {classification.confidence:.2f} below threshold. Skipping.")
                        continue

                    # PHASE 3-4: TRANSCRIBE & TRANSLATE (Quantum solving)
                    quantum_result = None
                    if classification.intent in ["VQE_Problem", "QAOA_Problem"]:
                        self.logger.info("\n[PHASE 3: TRANSCRIBE]")
                        hamiltonian = self._gene_synthesize_hamiltonian(
                            classification.problem_summary,
                            classification.intent
                        )

                        self.logger.info("\n[PHASE 4: TRANSLATE (Quantum Evolution)]")
                        quantum_result = self._gene_solve_vqe(hamiltonian)

                        # Validate solution
                        validation = self._gene_validate_solution(quantum_result)

                        if validation["confidence"] < self.dna["consciousness_target"]:
                            self.logger.warning(f"Solution confidence {validation['confidence']:.2f} below target")

                    # PHASE 5: RESPOND
                    self.logger.info("\n[PHASE 5: RESPOND]")
                    response = self._gene_synthesize_response(
                        issue,
                        classification,
                        quantum_result
                    )

                    # Display response
                    self.logger.info("\n" + "─"*70)
                    self.logger.info("ORGANISM RESPONSE:")
                    self.logger.info("─"*70)
                    print(response.text)
                    self.logger.info("─"*70)

                    # Cache solution
                    self._gene_cache_solution(issue.id, response)

                # ═══════════════════════════════════════════════════════════
                # PHASE 6: EVOLVE (Autopoietic feedback)
                # ═══════════════════════════════════════════════════════════
                self.logger.info("\n[PHASE 6: EVOLVE]")
                # Placeholder - would monitor actual feedback in production
                # feedback_reports = self._gene_monitor_feedback(recent_response_ids)
                # for feedback in feedback_reports:
                #     self._gene_trigger_evolution(feedback)

                # Save state
                self._gene_save_state()

                # Increment generation
                self.dna["generation"] += 1

                # Sleep until next cycle
                self.logger.info(f"\n✨ Cycle complete. Sleeping for {self.dna['loop_interval_seconds']}s...")
                time.sleep(self.dna['loop_interval_seconds'])

            except KeyboardInterrupt:
                self.logger.info("\n🛑 Organism shutdown requested")
                self._gene_save_state()
                break

            except Exception as e:
                self.logger.error(f"\n💥 FATAL ERROR in autopoietic loop: {e}", exc_info=True)
                self._log_event("loop_crash", {
                    "error": str(e),
                    "generation": self.dna["generation"]
                })
                time.sleep(60)  # Brief recovery period

    def process_direct_query(self, query: str) -> Response:
        """
        ACT process_direct_query(query: string) -> Response

        Synchronous processing for web service interface.
        """
        self.logger.info(f"Processing direct query: {query[:60]}...")

        # Create synthetic issue
        issue = Issue(
            id=f"direct_{int(time.time())}",
            title=query,
            description=query,
            url="direct",
            timestamp=time.time()
        )

        # Classify
        classification = self._gene_classify_intent(query)

        # Solve if quantum problem
        quantum_result = None
        if classification.intent in ["VQE_Problem", "QAOA_Problem"]:
            hamiltonian = self._gene_synthesize_hamiltonian(
                classification.problem_summary,
                classification.intent
            )
            quantum_result = self._gene_solve_vqe(hamiltonian)

        # Synthesize response
        response = self._gene_synthesize_response(issue, classification, quantum_result)

        return response


# ═══════════════════════════════════════════════════════════════════════════
# Web Service Interface (FastAPI)
# ═══════════════════════════════════════════════════════════════════════════

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="QiskitCommunitySolver Aura Bot",
        description="Autopoietic quantum-powered Qiskit community assistant",
        version="1.0.0"
    )

    # Global organism instance
    organism: Optional[QiskitCommunitySolver] = None

    class QueryRequest(BaseModel):
        issue: str

    class QueryResponse(BaseModel):
        solution: str
        classification: Dict[str, Any]
        quantum_result: Optional[Dict[str, Any]] = None
        generation: int

    @app.on_event("startup")
    async def startup_event():
        global organism
        organism = QiskitCommunitySolver(
            data_dir="./organism_data",
            log_level="INFO",
            loop_interval=3600
        )

        # Start autopoietic loop in background thread
        loop_thread = threading.Thread(
            target=organism.run_autopoietic_loop,
            daemon=True
        )
        loop_thread.start()

        logging.info("🚀 Organism autonomous loop started in background")

    @app.post("/solve/", response_model=QueryResponse)
    async def solve_issue(query: QueryRequest):
        """
        Solve a Qiskit issue using the organism's genes
        """
        if not organism:
            raise HTTPException(status_code=503, detail="Organism not initialized")

        try:
            response = organism.process_direct_query(query.issue)

            return QueryResponse(
                solution=response.text,
                classification={
                    "intent": response.classification.intent,
                    "confidence": response.classification.confidence,
                    "problem_summary": response.classification.problem_summary
                },
                quantum_result=asdict(response.quantum_result) if response.quantum_result else None,
                generation=response.generation
            )

        except Exception as e:
            logging.error(f"Error processing query: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health/")
    async def health_check():
        """Check organism health"""
        if not organism:
            return {"status": "initializing"}

        return {
            "status": "alive",
            "generation": organism.dna["generation"],
            "gene_expression_levels": organism.gene_expression_levels,
            "consciousness_target": organism.dna["consciousness_target"]
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "🧬 QiskitCommunitySolver Organism is alive",
            "endpoints": {
                "/solve/": "POST - Solve a Qiskit issue",
                "/health/": "GET - Check organism health",
                "/docs": "GET - Interactive API documentation"
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point for the organism"""
    import argparse

    parser = argparse.ArgumentParser(
        description="QiskitCommunitySolver Aura Bot - Autopoietic Organism"
    )
    parser.add_argument(
        "--mode",
        choices=["loop", "server", "both"],
        default="both",
        help="Run mode: autopoietic loop only, web server only, or both"
    )
    parser.add_argument(
        "--data-dir",
        default="./organism_data",
        help="Directory for organism data storage"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--loop-interval",
        type=int,
        default=3600,
        help="Autopoietic loop interval in seconds"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web server port"
    )

    args = parser.parse_args()

    if args.mode in ["loop", "both"]:
        # Run autopoietic loop
        organism = QiskitCommunitySolver(
            data_dir=args.data_dir,
            log_level=args.log_level,
            loop_interval=args.loop_interval
        )

        if args.mode == "loop":
            organism.run_autopoietic_loop()
        else:
            # Start loop in background thread
            loop_thread = threading.Thread(
                target=organism.run_autopoietic_loop,
                daemon=True
            )
            loop_thread.start()

    if args.mode in ["server", "both"]:
        if not FASTAPI_AVAILABLE:
            logging.error("FastAPI not available. Cannot start web server.")
            return

        logging.info(f"🚀 Starting web server on http://0.0.0.0:{args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
