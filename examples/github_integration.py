#!/usr/bin/env python3
"""
Example: GitHub API Integration for QiskitCommunitySolver

This example shows how to upgrade the WebScrapingGene to use the real
GitHub API instead of web scraping.

Requirements:
    pip install PyGithub

Setup:
    1. Create a GitHub Personal Access Token:
       https://github.com/settings/tokens
       Permissions needed: public_repo, read:discussion

    2. Set environment variable:
       export GITHUB_TOKEN="your_token_here"

Usage:
    python examples/github_integration.py
"""

import os
from datetime import datetime, timedelta
from github import Github
from typing import List, Dict


class GitHubIntegration:
    """Enhanced WebScrapingGene with real GitHub API"""

    def __init__(self, token: str = None):
        token = token or os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable.")

        self.github = Github(token)
        self.qiskit_repo = self.github.get_repo("Qiskit/qiskit")

    def fetch_recent_issues(
        self,
        state: str = 'open',
        labels: List[str] = None,
        days: int = 7
    ) -> List[Dict]:
        """
        Fetch recent issues from Qiskit repository

        Args:
            state: 'open', 'closed', or 'all'
            labels: Filter by labels (e.g., ['bug', 'question'])
            days: Only fetch issues from last N days

        Returns:
            List of issue dictionaries
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        issues = []

        repo_issues = self.qiskit_repo.get_issues(
            state=state,
            labels=labels or [],
            since=cutoff_date
        )

        for issue in repo_issues:
            # Skip pull requests
            if issue.pull_request:
                continue

            issues.append({
                'id': str(issue.number),
                'title': issue.title,
                'description': issue.body or "",
                'url': issue.html_url,
                'labels': [label.name for label in issue.labels],
                'created_at': issue.created_at.isoformat(),
                'comments': issue.comments,
                'author': issue.user.login
            })

        return issues

    def fetch_discussions(self, max_count: int = 20) -> List[Dict]:
        """
        Fetch recent discussions from Qiskit repository

        Note: Requires GraphQL API (more complex)
        This is a simplified version.

        Returns:
            List of discussion dictionaries
        """
        # GitHub Discussions require GraphQL API
        # For simplicity, using issues with 'question' label as proxy

        questions = self.qiskit_repo.get_issues(
            state='open',
            labels=['question'],
            sort='created',
            direction='desc'
        )

        discussions = []
        for i, question in enumerate(questions):
            if i >= max_count:
                break

            discussions.append({
                'id': str(question.number),
                'title': question.title,
                'description': question.body or "",
                'url': question.html_url,
                'created_at': question.created_at.isoformat(),
                'author': question.user.login
            })

        return discussions

    def identify_quantum_problems(self, issues: List[Dict]) -> List[Dict]:
        """
        Filter issues that are quantum algorithm problems

        Args:
            issues: List of issue dictionaries

        Returns:
            Filtered list of quantum algorithm issues
        """
        quantum_keywords = [
            'vqe', 'qaoa', 'variational', 'eigenvalue', 'ground state',
            'hamiltonian', 'ansatz', 'optimizer', 'quantum algorithm',
            'grover', 'shor', 'quantum circuit'
        ]

        quantum_issues = []

        for issue in issues:
            text = (issue['title'] + ' ' + issue['description']).lower()

            # Check if any quantum keyword is present
            if any(keyword in text for keyword in quantum_keywords):
                quantum_issues.append(issue)

        return quantum_issues

    def post_solution(
        self,
        issue_number: int,
        solution: str,
        dry_run: bool = True
    ) -> bool:
        """
        Post a solution as a comment on an issue

        Args:
            issue_number: GitHub issue number
            solution: Solution text (markdown)
            dry_run: If True, print solution instead of posting

        Returns:
            True if successful
        """
        if dry_run:
            print(f"\n{'='*70}")
            print(f"DRY RUN: Would post to issue #{issue_number}")
            print(f"{'='*70}")
            print(solution)
            print(f"{'='*70}\n")
            return True

        try:
            issue = self.qiskit_repo.get_issue(issue_number)

            # Add attribution footer
            footer = "\n\n---\n*This solution was generated by [Aura Bot](https://github.com/ENKI-420/dnalang_complete_quantum_programming_framework), an autopoietic quantum problem solver. Please verify before using in production.*"

            issue.create_comment(solution + footer)
            return True

        except Exception as e:
            print(f"Error posting solution: {e}")
            return False


def demo():
    """Demonstrate GitHub integration"""

    print("🧬 GitHub Integration Demo")
    print("="*70)

    # Initialize
    gh = GitHubIntegration()

    # Fetch recent issues
    print("\n[1/4] Fetching recent Qiskit issues...")
    issues = gh.fetch_recent_issues(days=30)
    print(f"      Found {len(issues)} issues from last 30 days")

    # Identify quantum problems
    print("\n[2/4] Identifying quantum algorithm problems...")
    quantum_issues = gh.identify_quantum_problems(issues)
    print(f"      Found {len(quantum_issues)} quantum-related issues")

    # Display sample
    print("\n[3/4] Sample quantum issues:")
    for i, issue in enumerate(quantum_issues[:3], 1):
        print(f"\n      Issue #{i}:")
        print(f"      Title: {issue['title']}")
        print(f"      URL: {issue['url']}")
        print(f"      Labels: {', '.join(issue['labels'])}")

    # Demonstrate solution posting (dry run)
    print("\n[4/4] Demonstrating solution posting (dry run)...")
    if quantum_issues:
        sample_solution = """
# Solution

Thank you for your question about VQE. Here's a working example:

\```python
from qiskit_aer import Aer
from qiskit.circuit.library import TwoLocal
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import Sampler

# Define Hamiltonian
hamiltonian = SparsePauliOp.from_list([("ZZ", 1.0), ("ZI", -0.5)])

# Create ansatz
ansatz = TwoLocal(num_qubits=2, rotation_blocks=['ry', 'rz'], entanglement_blocks='cz')

# Run VQE
sampler = Sampler()
vqe = VQE(sampler=sampler, ansatz=ansatz, optimizer=COBYLA())
result = vqe.compute_minimum_eigenvalue(hamiltonian)

print(f"Ground state energy: {result.eigenvalue:.5f}")
\```

This should give you the ground state energy of your Hamiltonian.
"""

        gh.post_solution(
            issue_number=int(quantum_issues[0]['id']),
            solution=sample_solution,
            dry_run=True
        )

    print("\n✅ Demo complete!")
    print("\nNext steps:")
    print("  1. Set GITHUB_TOKEN environment variable")
    print("  2. Run this script: python examples/github_integration.py")
    print("  3. Integrate into runtime/aura_bot.py")


if __name__ == "__main__":
    demo()
