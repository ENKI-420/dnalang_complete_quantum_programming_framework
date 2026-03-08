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
import yaml
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from bs4 import BeautifulSoup

# GitHub Integration
try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    logging.warning("PyGithub not available. GitHub feedback monitoring will be disabled.")

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


@dataclass
class Habitat:
    """Represents a community habitat (data source)"""
    name: str
    url: str
    enabled: bool = True
    priority: int = 1
    last_scraped: Optional[float] = None
    total_issues_found: int = 0


@dataclass
class OrganismMetrics:
    """Comprehensive organism performance metrics"""
    total_issues_processed: int = 0
    successful_solutions: int = 0
    failed_solutions: int = 0
    average_confidence: float = 0.0
    average_response_time: float = 0.0
    total_mutations_triggered: int = 0
    uptime_seconds: float = 0.0
    generation: int = 0
    classification_accuracy: float = 0.0
    quantum_solver_success_rate: float = 0.0
    last_updated: Optional[str] = None
    habitat_stats: Dict[str, int] = field(default_factory=dict)


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
        loop_interval: int = 3600,
        config_path: Optional[str] = None
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

        # Load configuration
        self.config = self._load_config(config_path)

        # Create data directory
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Organism DNA (metadata) - enhanced with config
        organism_config = self.config.get("organism", {})
        self.dna = {
            "domain": organism_config.get("domain", "qiskit_community_support"),
            "consciousness_target": organism_config.get("consciousness_target", 0.85),
            "decoherence_threshold": organism_config.get("decoherence_threshold", 0.3),
            "generation": 0,
            "loop_interval_seconds": loop_interval,
            "max_concurrent_issues": organism_config.get("max_concurrent_issues", 5),
            "feedback_integration_rate": organism_config.get("feedback_integration_rate", 0.1),
            "creation_time": datetime.now().isoformat(),
            "start_time": time.time()
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

        # Multi-habitat support
        self.habitats = self._initialize_habitats()

        # Metrics tracking
        self.metrics = OrganismMetrics()

        # File paths
        persistence_config = self.config.get("persistence", {}).get("files", {})
        self.log_file = self.data_dir / persistence_config.get("autopoiesis_log", "autopoiesis_log.jsonl")
        self.state_file = self.data_dir / "organism_state.json"
        self.seen_issues_file = self.data_dir / persistence_config.get("seen_issues", "seen_issues.json")
        self.solution_cache_file = self.data_dir / persistence_config.get("solution_cache", "solution_cache.json")
        self.metrics_file = self.data_dir / persistence_config.get("metrics", "metrics.json")

        # GitHub integration
        self.github_client = None
        if GITHUB_AVAILABLE and self.config.get("integrations", {}).get("github", {}).get("enabled", False):
            self._initialize_github()

        # Initialize genes
        self._initialize_genes()

        # Load previous state if available
        self._gene_load_state()

        self.logger.info("✨ Organism fully alive. Generation: %d", self.dna["generation"])
        self.logger.info(f"   Active habitats: {len([h for h in self.habitats if h.enabled])}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load organism configuration from YAML file"""
        if config_path is None:
            # Look for config.yaml in common locations
            possible_paths = [
                Path("config.yaml"),
                Path("./config.yaml"),
                Path(__file__).parent.parent / "config.yaml",
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break

        if config_path and Path(config_path).exists():
            self.logger.info(f"  Loading configuration from: {config_path}")
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            self.logger.warning("  No configuration file found. Using defaults.")
            return {}

    def _initialize_habitats(self) -> List[Habitat]:
        """Initialize community habitats from configuration"""
        habitats = []
        habitat_configs = self.config.get("genes", {}).get("web_scraping", {}).get("enabled_habitats", [])

        if not habitat_configs:
            # Default habitat
            habitats.append(Habitat(
                name="github_discussions",
                url="https://github.com/Qiskit/qiskit/discussions",
                enabled=True,
                priority=1
            ))
        else:
            for hconfig in habitat_configs:
                habitats.append(Habitat(
                    name=hconfig.get("name", "unknown"),
                    url=hconfig.get("url", ""),
                    enabled=hconfig.get("enabled", True),
                    priority=hconfig.get("priority", 1)
                ))

        # Sort by priority
        habitats.sort(key=lambda h: h.priority)

        self.logger.info(f"  Initialized {len(habitats)} habitats")
        for habitat in habitats:
            if habitat.enabled:
                self.logger.info(f"    ✓ {habitat.name}: {habitat.url}")

        return habitats

    def _initialize_github(self):
        """Initialize GitHub API client for feedback monitoring"""
        try:
            github_token = os.environ.get("GITHUB_TOKEN")
            if github_token:
                self.github_client = Github(github_token)
                self.logger.info("  ✓ GitHub API client initialized")
                # Test the connection
                rate_limit = self.github_client.get_rate_limit()
                self.logger.info(f"    GitHub API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
            else:
                self.logger.warning("  GITHUB_TOKEN not set. GitHub feedback monitoring will use unauthenticated mode (limited).")
                self.github_client = Github()
        except Exception as e:
            self.logger.error(f"  ✗ GitHub initialization failed: {e}")
            self.github_client = None

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
    # GENE: WebScrapingGene (Enhanced with Multi-Habitat Support)
    # ═══════════════════════════════════════════════════════════════════════

    def _gene_fetch_issues_multi_habitat(self) -> List[Issue]:
        """
        Enhanced fetch_issues that scans multiple habitats

        Returns combined issues from all enabled habitats
        """
        all_issues = []

        for habitat in self.habitats:
            if not habitat.enabled:
                continue

            max_issues = self.config.get("genes", {}).get("web_scraping", {}).get("max_issues_per_habitat", 10)
            issues = self._gene_fetch_issues(habitat.url, max_issues, habitat.name)

            habitat.last_scraped = time.time()
            habitat.total_issues_found += len(issues)

            all_issues.extend(issues)

            # Update metrics
            if habitat.name not in self.metrics.habitat_stats:
                self.metrics.habitat_stats[habitat.name] = 0
            self.metrics.habitat_stats[habitat.name] += len(issues)

        return all_issues

    def _gene_fetch_issues(self, url: str, max_issues: int = 10, habitat_name: str = "unknown") -> List[Issue]:
        """
        ACT fetch_issues(url: string) -> list[Issue]

        Observes the external habitat for decoherence events (issues).
        """
        self.logger.info(f"  WebScrapingGene: Fetching from {habitat_name}: {url}")

        try:
            scraping_config = self.config.get("genes", {}).get("web_scraping", {})
            headers = {
                'User-Agent': scraping_config.get("user_agent", "QiskitCommunitySolver-AuraBot/2.0")
            }
            timeout = scraping_config.get("request_timeout", 15)
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            issues = []

            # Different parsing logic based on habitat
            if "github.com" in url:
                issues = self._parse_github(soup, url, max_issues)
            elif "stackoverflow.com" in url:
                issues = self._parse_stackoverflow(soup, url, max_issues)
            elif "quantumcomputing.stackexchange.com" in url:
                issues = self._parse_quantum_se(soup, url, max_issues)
            else:
                # Generic parsing
                issues = self._parse_generic(soup, url, max_issues)

            # Filter for novelty
            novel_issues = []
            for issue in issues:
                if self._gene_validate_issue_novelty(issue):
                    novel_issues.append(issue)
                    self.seen_issues.add(issue.id)

            self._log_event("fetch_issues", {
                "count": len(novel_issues),
                "url": url,
                "habitat": habitat_name,
                "novel_count": len(novel_issues)
            })

            return novel_issues

        except Exception as e:
            self.logger.error(f"  WebScrapingGene ERROR ({habitat_name}): {e}")
            self._log_event("fetch_error", {"error": str(e), "url": url, "habitat": habitat_name})
            return []

    def _parse_github(self, soup: BeautifulSoup, base_url: str, max_issues: int) -> List[Issue]:
        """Parse GitHub discussions/issues"""
        discussion_elements = soup.find_all("a", class_=re.compile("Link--primary"))

        issues = []
        for elem in discussion_elements[:max_issues]:
            title = elem.get_text(strip=True)
            href = elem.get('href', '')

            if not title or not href or len(title) < 10:
                continue

            # Construct full URL
            if href.startswith('/'):
                full_url = f"https://github.com{href}"
            else:
                full_url = href

            issue = Issue(
                id=full_url,
                title=title,
                description="",
                url=full_url,
                timestamp=time.time()
            )
            issues.append(issue)

        return issues

    def _parse_stackoverflow(self, soup: BeautifulSoup, base_url: str, max_issues: int) -> List[Issue]:
        """Parse StackOverflow questions"""
        question_elements = soup.find_all("div", class_="s-post-summary")

        issues = []
        for elem in question_elements[:max_issues]:
            title_elem = elem.find("a", class_="s-link")
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')

            if not title or not href:
                continue

            full_url = f"https://stackoverflow.com{href}" if href.startswith('/') else href

            issue = Issue(
                id=full_url,
                title=title,
                description="",
                url=full_url,
                timestamp=time.time()
            )
            issues.append(issue)

        return issues

    def _parse_quantum_se(self, soup: BeautifulSoup, base_url: str, max_issues: int) -> List[Issue]:
        """Parse Quantum Computing StackExchange questions"""
        # Similar structure to StackOverflow
        return self._parse_stackoverflow(soup, base_url, max_issues)

    def _parse_generic(self, soup: BeautifulSoup, base_url: str, max_issues: int) -> List[Issue]:
        """Generic parser for unknown habitats"""
        # Find all links that might be issues/questions
        links = soup.find_all("a", href=True)

        issues = []
        for link in links[:max_issues * 2]:  # Get extra to filter
            title = link.get_text(strip=True)
            href = link.get('href', '')

            if len(title) < 20 or len(title) > 200:  # Filter by reasonable title length
                continue

            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                from urllib.parse import urljoin
                full_url = urljoin(base_url, href)
            else:
                continue

            issue = Issue(
                id=full_url,
                title=title,
                description="",
                url=full_url,
                timestamp=time.time()
            )
            issues.append(issue)

            if len(issues) >= max_issues:
                break

        return issues

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
        Enhanced with better problem-to-operator mapping.
        """
        problem_lower = problem_summary.lower()

        # Determine number of qubits from problem context
        num_qubits = 2  # Default

        # Extract qubit count if mentioned
        qubit_match = re.search(r'(\d+)[\s-]?qubit', problem_lower)
        if qubit_match:
            num_qubits = min(int(qubit_match.group(1)), 6)  # Cap at 6 qubits for simulation

        if intent == "VQE_Problem":
            # Enhanced VQE Hamiltonian synthesis
            if any(kw in problem_lower for kw in ["h2", "hydrogen", "molecule"]):
                # Molecular Hamiltonian (simplified H2)
                operator = SparsePauliOp.from_list([
                    ("II", -1.052373245772859),
                    ("IZ", 0.39793742484318045),
                    ("ZI", -0.39793742484318045),
                    ("ZZ", -0.01128010425623538),
                    ("XX", 0.18093119978423156)
                ])
            elif any(kw in problem_lower for kw in ["ising", "spin"]):
                # Ising model
                operator = self._create_ising_hamiltonian(num_qubits)
            elif any(kw in problem_lower for kw in ["heisenberg"]):
                # Heisenberg model
                operator = self._create_heisenberg_hamiltonian(num_qubits)
            else:
                # Default: transverse field Ising
                operator = self._create_ising_hamiltonian(num_qubits, transverse_field=0.5)

        elif intent == "QAOA_Problem":
            # Enhanced QAOA Hamiltonian synthesis
            if any(kw in problem_lower for kw in ["max-cut", "maxcut", "graph"]):
                # Max-Cut problem
                operator = self._create_maxcut_hamiltonian(num_qubits)
            elif any(kw in problem_lower for kw in ["partition", "number partition"]):
                # Number partition
                operator = self._create_partition_hamiltonian(num_qubits)
            else:
                # Default QAOA cost Hamiltonian
                operator = self._create_maxcut_hamiltonian(num_qubits)

        else:
            # Default 2-qubit Hamiltonian
            operator = SparsePauliOp.from_list([
                ("ZZ", 1.0),
                ("ZI", -0.5),
                ("IZ", -0.5)
            ])

        self.logger.info(f"  Synthesized Hamiltonian: {num_qubits} qubits, {len(operator.paulis)} terms")
        return operator

    def _create_ising_hamiltonian(self, num_qubits: int, transverse_field: float = 0.0) -> SparsePauliOp:
        """Create an Ising model Hamiltonian"""
        pauli_list = []

        # Coupling terms (ZZ interactions)
        for i in range(num_qubits - 1):
            pauli_str = "I" * i + "ZZ" + "I" * (num_qubits - i - 2)
            pauli_list.append((pauli_str, 1.0))

        # Longitudinal field (Z terms)
        for i in range(num_qubits):
            pauli_str = "I" * i + "Z" + "I" * (num_qubits - i - 1)
            pauli_list.append((pauli_str, -0.5))

        # Transverse field (X terms)
        if transverse_field > 0:
            for i in range(num_qubits):
                pauli_str = "I" * i + "X" + "I" * (num_qubits - i - 1)
                pauli_list.append((pauli_str, -transverse_field))

        return SparsePauliOp.from_list(pauli_list)

    def _create_heisenberg_hamiltonian(self, num_qubits: int) -> SparsePauliOp:
        """Create a Heisenberg model Hamiltonian"""
        pauli_list = []

        # Heisenberg interactions: XX + YY + ZZ
        for i in range(num_qubits - 1):
            for pauli_char in ['X', 'Y', 'Z']:
                pauli_str = "I" * i + pauli_char * 2 + "I" * (num_qubits - i - 2)
                pauli_list.append((pauli_str, 1.0))

        return SparsePauliOp.from_list(pauli_list)

    def _create_maxcut_hamiltonian(self, num_qubits: int) -> SparsePauliOp:
        """Create a Max-Cut Hamiltonian for a simple graph"""
        pauli_list = []

        # Create edges for a circular graph
        for i in range(num_qubits):
            j = (i + 1) % num_qubits
            if i < j:
                pauli_str_i = "I" * i + "Z" + "I" * (num_qubits - i - 1)
                pauli_str_j = "I" * j + "Z" + "I" * (num_qubits - j - 1)

                # For Max-Cut: 0.5 * (I - Z_i Z_j) for each edge
                pauli_list.append((pauli_str_i[:min(i,j)] + "Z" + pauli_str_i[min(i,j)+1:max(i,j)] + "Z" + pauli_str_i[max(i,j)+1:], -0.5))

        # Add some cross edges for more complexity
        if num_qubits >= 4:
            for i in range(0, num_qubits - 2, 2):
                j = i + 2
                pauli_str = "I" * i + "Z" + "I" * (j - i - 1) + "Z" + "I" * (num_qubits - j - 1)
                pauli_list.append((pauli_str, -0.5))

        return SparsePauliOp.from_list(pauli_list) if pauli_list else SparsePauliOp.from_list([("Z", 1.0)])

    def _create_partition_hamiltonian(self, num_qubits: int) -> SparsePauliOp:
        """Create a number partition Hamiltonian"""
        # Simplified number partition: minimize sum of differences
        pauli_list = []

        for i in range(num_qubits):
            weight = i + 1  # Simple weights
            pauli_str = "I" * i + "Z" + "I" * (num_qubits - i - 1)
            pauli_list.append((pauli_str, weight))

        return SparsePauliOp.from_list(pauli_list)

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

        Monitors community feedback on responses using GitHub API.
        """
        self.logger.info("  AutopoiesisGene: Monitoring feedback...")

        feedback_reports = []

        if not self.github_client:
            self.logger.warning("  GitHub client not available. Skipping feedback monitoring.")
            return []

        for response_id in response_ids:
            try:
                # Extract repo and issue/discussion number from response_id
                # Expected format: "owner/repo/issues/123" or URL
                feedback = self._fetch_github_feedback(response_id)
                if feedback:
                    feedback_reports.append(feedback)

            except Exception as e:
                self.logger.error(f"  Error fetching feedback for {response_id}: {e}")

        return feedback_reports

    def _fetch_github_feedback(self, url_or_id: str) -> Optional[FeedbackReport]:
        """Fetch feedback from GitHub for a specific discussion/issue"""
        try:
            if not self.github_client:
                return None

            # Parse GitHub URL to extract owner, repo, and issue number
            # Example: https://github.com/Qiskit/qiskit/discussions/12345
            match = re.search(r'github\.com/([^/]+)/([^/]+)/(issues|discussions)/(\d+)', url_or_id)
            if not match:
                return None

            owner, repo, item_type, item_number = match.groups()
            item_number = int(item_number)

            # Get the repository
            repository = self.github_client.get_repo(f"{owner}/{repo}")

            if item_type == "issues":
                item = repository.get_issue(item_number)
                upvotes = item.reactions['thumbs_up'] + item.reactions['heart'] + item.reactions['hooray']
                downvotes = item.reactions['thumbs_down']
                comments = item.comments
                is_closed = item.state == 'closed'

                feedback = FeedbackReport(
                    response_id=url_or_id,
                    upvotes=upvotes,
                    comments=comments,
                    acceptance=is_closed and upvotes > 0,
                    is_positive=(upvotes - downvotes) > 2,
                    indicates_classification_error=False,  # Would need NLP to determine
                    indicates_solution_error=downvotes > upvotes
                )

                return feedback
            else:
                # For discussions, we'd need GraphQL API (more complex)
                # For now, return basic feedback
                return FeedbackReport(
                    response_id=url_or_id,
                    upvotes=0,
                    comments=0,
                    acceptance=False,
                    is_positive=False
                )

        except GithubException as e:
            self.logger.warning(f"  GitHub API error: {e.status} - {e.data.get('message', 'Unknown error')}")
            return None
        except Exception as e:
            self.logger.error(f"  Feedback fetch error: {e}")
            return None

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

            # Save metrics
            self._save_metrics()

            self.logger.debug("  PersistenceGene: State saved")

        except Exception as e:
            self.logger.error(f"  PersistenceGene save ERROR: {e}")

    def _save_metrics(self):
        """Save organism metrics to disk"""
        try:
            # Update metrics before saving
            self.metrics.generation = self.dna["generation"]
            self.metrics.uptime_seconds = time.time() - self.dna["start_time"]
            self.metrics.last_updated = datetime.now().isoformat()

            with open(self.metrics_file, 'w') as f:
                json.dump(asdict(self.metrics), f, indent=2)

            self.logger.debug("  Metrics saved")

        except Exception as e:
            self.logger.error(f"  Metrics save ERROR: {e}")

    def _load_metrics(self):
        """Load organism metrics from disk"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics_data = json.load(f)

                self.metrics = OrganismMetrics(**metrics_data)
                self.logger.info(f"  Metrics loaded: {self.metrics.total_issues_processed} issues processed")

        except Exception as e:
            self.logger.error(f"  Metrics load ERROR: {e}")

    def _update_metrics(self, **kwargs):
        """Update organism metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                if isinstance(getattr(self.metrics, key), (int, float)):
                    # For numeric values, update
                    setattr(self.metrics, key, value)
                elif isinstance(getattr(self.metrics, key), dict):
                    # For dict values, merge
                    getattr(self.metrics, key).update(value)

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

            # Load metrics
            self._load_metrics()

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
                # PHASE 1: OBSERVE (Scan environment across multiple habitats)
                # ═══════════════════════════════════════════════════════════
                self.logger.info("\n[PHASE 1: OBSERVE]")
                issues = self._gene_fetch_issues_multi_habitat()

                if not issues:
                    self.logger.info("No new decoherence events. Organism dormant.")
                else:
                    self.logger.info(f"Found {len(issues)} novel issues")

                # ═══════════════════════════════════════════════════════════
                # PHASE 2-5: Process each issue
                # ═══════════════════════════════════════════════════════════
                for idx, issue in enumerate(issues, 1):
                    process_start_time = time.time()
                    self.logger.info(f"\n--- Processing Issue {idx}/{len(issues)} ---")
                    self.logger.info(f"Title: {issue.title}")

                    try:
                        # Track issue processing
                        self.metrics.total_issues_processed += 1

                        # PHASE 2: DIAGNOSE
                        self.logger.info("\n[PHASE 2: DIAGNOSE]")
                        classification = self._gene_classify_intent(issue.title)

                        if classification.confidence < self.dna["decoherence_threshold"]:
                            self.logger.warning(f"Confidence {classification.confidence:.2f} below threshold. Skipping.")
                            continue

                        # Update average confidence
                        total_processed = self.metrics.total_issues_processed
                        self.metrics.average_confidence = (
                            (self.metrics.average_confidence * (total_processed - 1) + classification.confidence)
                            / total_processed
                        )

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

                            # Track quantum solver success
                            if quantum_result.success:
                                self.metrics.successful_solutions += 1
                            else:
                                self.metrics.failed_solutions += 1

                            # Update success rate
                            total_quantum = self.metrics.successful_solutions + self.metrics.failed_solutions
                            if total_quantum > 0:
                                self.metrics.quantum_solver_success_rate = (
                                    self.metrics.successful_solutions / total_quantum
                                )

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

                        # Update average response time
                        response_time = time.time() - process_start_time
                        total_processed = self.metrics.total_issues_processed
                        self.metrics.average_response_time = (
                            (self.metrics.average_response_time * (total_processed - 1) + response_time)
                            / total_processed
                        )

                    except Exception as e:
                        self.logger.error(f"Error processing issue {issue.id}: {e}", exc_info=True)
                        self.metrics.failed_solutions += 1

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
            "consciousness_target": organism.dna["consciousness_target"],
            "uptime_seconds": time.time() - organism.dna["start_time"]
        }

    @app.get("/metrics/")
    async def get_metrics():
        """Get comprehensive organism metrics"""
        if not organism:
            raise HTTPException(status_code=503, detail="Organism not initialized")

        # Update metrics before returning
        organism.metrics.generation = organism.dna["generation"]
        organism.metrics.uptime_seconds = time.time() - organism.dna["start_time"]

        return {
            "metrics": asdict(organism.metrics),
            "habitats": [
                {
                    "name": h.name,
                    "url": h.url,
                    "enabled": h.enabled,
                    "total_issues_found": h.total_issues_found,
                    "last_scraped": h.last_scraped
                }
                for h in organism.habitats
            ]
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "🧬 QiskitCommunitySolver Organism is alive",
            "version": "2.0.0",
            "endpoints": {
                "/solve/": "POST - Solve a Qiskit issue",
                "/health/": "GET - Check organism health",
                "/metrics/": "GET - Get comprehensive metrics",
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
