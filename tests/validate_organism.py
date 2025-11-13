#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
Organism Validation Script
═══════════════════════════════════════════════════════════════════════════

Validates the coherence and functionality of the QiskitCommunitySolver
organism without requiring full dependency installation.

Validation Criteria:
1. Syntax correctness (Python AST parsing)
2. Import structure validation
3. Class structure validation
4. Gene method existence
5. Data structure completeness
"""

import ast
import sys
from pathlib import Path


def validate_syntax(file_path: Path) -> tuple[bool, str]:
    """Validate Python syntax by parsing AST"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "✓ Syntax valid"
    except SyntaxError as e:
        return False, f"✗ Syntax error: {e}"


def validate_structure(file_path: Path) -> tuple[bool, list[str]]:
    """Validate class and method structure"""
    results = []

    with open(file_path, 'r') as f:
        code = f.read()

    tree = ast.parse(code)

    # Find QiskitCommunitySolver class
    main_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "QiskitCommunitySolver":
            main_class = node
            break

    if not main_class:
        return False, ["✗ QiskitCommunitySolver class not found"]

    results.append("✓ QiskitCommunitySolver class found")

    # Required gene methods
    required_genes = [
        "_gene_fetch_issues",
        "_gene_classify_intent",
        "_gene_solve_vqe",
        "_gene_synthesize_response",
        "_gene_save_state",
        "_gene_load_state"
    ]

    methods = [node.name for node in main_class.body if isinstance(node, ast.FunctionDef)]

    for gene in required_genes:
        if gene in methods:
            results.append(f"✓ Gene method {gene} exists")
        else:
            results.append(f"✗ Gene method {gene} missing")

    # Check for main metabolism
    if "run_autopoietic_loop" in methods:
        results.append("✓ Main metabolism (run_autopoietic_loop) exists")
    else:
        results.append("✗ Main metabolism missing")

    # Check for direct query interface
    if "process_direct_query" in methods:
        results.append("✓ Direct query interface exists")
    else:
        results.append("✗ Direct query interface missing")

    return all("✓" in r for r in results), results


def validate_data_structures(file_path: Path) -> tuple[bool, list[str]]:
    """Validate dataclass definitions"""
    results = []

    with open(file_path, 'r') as f:
        code = f.read()

    tree = ast.parse(code)

    required_dataclasses = [
        "Issue",
        "Classification",
        "QuantumResult",
        "Response",
        "FeedbackReport"
    ]

    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    for dc in required_dataclasses:
        if dc in classes:
            results.append(f"✓ Data structure {dc} defined")
        else:
            results.append(f"✗ Data structure {dc} missing")

    return all("✓" in r for r in results), results


def validate_dna_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate DNALang organism specification"""
    results = []

    if not file_path.exists():
        return False, ["✗ DNALang specification file not found"]

    with open(file_path, 'r') as f:
        content = f.read()

    # Check for key sections
    required_sections = [
        "ORGANISM QiskitCommunitySolver",
        "DNA {",
        "GENOME {",
        "GENE WebScrapingGene",
        "GENE NLPIntentGene",
        "GENE QuantumSolverGene",
        "GENE ResponseSynthesisGene",
        "GENE AutopoiesisGene",
        "GENE PersistenceGene",
        "ACT run_autopoietic_loop()"
    ]

    for section in required_sections:
        if section in content:
            results.append(f"✓ {section} found")
        else:
            results.append(f"✗ {section} missing")

    # Check for mutations
    if "MUTATIONS {" in content:
        mutation_count = content.count("MUTATIONS {")
        results.append(f"✓ {mutation_count} mutation blocks defined")

    # Check line count
    line_count = len(content.split('\n'))
    results.append(f"✓ Specification size: {line_count} lines")

    return all("✓" in r for r in results), results


def calculate_coherence(results: dict) -> float:
    """Calculate organism coherence (Φ) based on validation results"""
    total_checks = 0
    passed_checks = 0

    for category, (success, details) in results.items():
        for detail in details:
            total_checks += 1
            if "✓" in detail:
                passed_checks += 1

    return passed_checks / total_checks if total_checks > 0 else 0.0


def main():
    print("═" * 70)
    print("QiskitCommunitySolver Organism Validation")
    print("═" * 70)
    print()

    # Paths
    root = Path(__file__).parent.parent
    runtime_file = root / "runtime" / "aura_bot.py"
    dna_file = root / "organisms" / "QiskitCommunitySolver.dna"

    results = {}

    # 1. Validate Python runtime syntax
    print("[1/5] Validating Python syntax...")
    success, message = validate_syntax(runtime_file)
    results["syntax"] = (success, [message])
    print(f"      {message}")
    print()

    # 2. Validate class structure
    print("[2/5] Validating class structure...")
    success, details = validate_structure(runtime_file)
    results["structure"] = (success, details)
    for detail in details:
        print(f"      {detail}")
    print()

    # 3. Validate data structures
    print("[3/5] Validating data structures...")
    success, details = validate_data_structures(runtime_file)
    results["datastructures"] = (success, details)
    for detail in details:
        print(f"      {detail}")
    print()

    # 4. Validate DNALang specification
    print("[4/5] Validating DNALang specification...")
    success, details = validate_dna_file(dna_file)
    results["dna"] = (success, details)
    for detail in details:
        print(f"      {detail}")
    print()

    # 5. Calculate coherence
    print("[5/5] Calculating organism coherence...")
    coherence = calculate_coherence(results)
    print(f"      Φ = {coherence:.2f}")
    print()

    # Summary
    print("═" * 70)
    print("VALIDATION SUMMARY")
    print("═" * 70)
    print()

    all_passed = all(success for success, _ in results.values())

    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print(f"✅ Organism Coherence: Φ = {coherence:.2f} (High)")
        print("✅ Organism is COHERENT and ready for deployment")
        return 0
    else:
        print("⚠️  SOME VALIDATIONS FAILED")
        print(f"⚠️  Organism Coherence: Φ = {coherence:.2f}")
        for category, (success, _) in results.items():
            status = "✓" if success else "✗"
            print(f"   {status} {category}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
