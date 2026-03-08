# DNALang Framework - Usage Examples

This document provides practical examples for using the DNALang QiskitCommunitySolver organism v2.0.

---

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Configuration Examples](#configuration-examples)
3. [Web API Examples](#web-api-examples)
4. [Multi-Habitat Usage](#multi-habitat-usage)
5. [Metrics and Monitoring](#metrics-and-monitoring)
6. [GitHub Integration](#github-integration)
7. [Testing Examples](#testing-examples)

---

## Basic Usage

### Running the Organism

```bash
# Install dependencies first
pip install -r requirements.txt

# Run autonomous loop only
python runtime/aura_bot.py --mode loop --loop-interval 3600

# Run web service only
python runtime/aura_bot.py --mode server --port 8000

# Run both (recommended)
python runtime/aura_bot.py --mode both --port 8000
```

### Custom Data Directory

```bash
python runtime/aura_bot.py \
  --mode both \
  --data-dir ./my_organism_data \
  --log-level DEBUG
```

---

## Configuration Examples

### Example 1: Minimal Configuration

**File:** `config_minimal.yaml`
```yaml
organism:
  consciousness_target: 0.85

genes:
  web_scraping:
    enabled_habitats:
      - name: "github_discussions"
        url: "https://github.com/Qiskit/qiskit/discussions"
        enabled: true
```

**Usage:**
```bash
python runtime/aura_bot.py --config-path config_minimal.yaml
```

### Example 2: Multi-Habitat Configuration

**File:** `config_multihabitat.yaml`
```yaml
organism:
  consciousness_target: 0.85
  loop_interval_seconds: 1800  # 30 minutes

genes:
  web_scraping:
    enabled_habitats:
      - name: "github_discussions"
        url: "https://github.com/Qiskit/qiskit/discussions"
        enabled: true
        priority: 1

      - name: "stackoverflow"
        url: "https://stackoverflow.com/questions/tagged/qiskit"
        enabled: true
        priority: 2

      - name: "quantum_se"
        url: "https://quantumcomputing.stackexchange.com/questions/tagged/qiskit"
        enabled: true
        priority: 3

    max_issues_per_habitat: 5
```

### Example 3: Quantum Solver Tuning

**File:** `config_quantum.yaml`
```yaml
genes:
  quantum_solver:
    backend: "aer_simulator"
    algorithm: "VQE"
    optimizer: "SLSQP"  # Try different optimizers
    max_iterations: 1000
    ansatz_reps: 5  # Deeper ansatz
```

---

## Web API Examples

### Using cURL

#### Solve a VQE Problem
```bash
curl -X POST "http://localhost:8000/solve/" \
  -H "Content-Type: application/json" \
  -d '{
    "issue": "Find the ground state energy of a 3-qubit Ising model using VQE"
  }'
```

#### Check Organism Health
```bash
curl http://localhost:8000/health/
```

#### Get Metrics
```bash
curl http://localhost:8000/metrics/ | jq
```

### Using Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Solve a VQE Problem
response = requests.post(
    f"{BASE_URL}/solve/",
    json={"issue": "How do I find the ground state of H2 using VQE?"}
)
result = response.json()

print("Solution:")
print(result['solution'])
print(f"\nClassification: {result['classification']['intent']}")
print(f"Confidence: {result['classification']['confidence']:.2f}")

if result['quantum_result']:
    print(f"Eigenvalue: {result['quantum_result']['eigenvalue']:.6f}")
    print(f"Optimizer Time: {result['quantum_result']['optimizer_time']:.2f}s")

# 2. Get organism health
health = requests.get(f"{BASE_URL}/health/").json()
print(f"\nOrganism Generation: {health['generation']}")
print(f"Consciousness Target: {health['consciousness_target']}")

# 3. Get comprehensive metrics
metrics = requests.get(f"{BASE_URL}/metrics/").json()

print(f"\n=== Organism Metrics ===")
print(f"Issues Processed: {metrics['metrics']['total_issues_processed']}")
print(f"Success Rate: {metrics['metrics']['quantum_solver_success_rate']:.2%}")
print(f"Avg Confidence: {metrics['metrics']['average_confidence']:.2f}")
print(f"Uptime: {metrics['metrics']['uptime_seconds']:.0f}s")

print(f"\n=== Habitat Statistics ===")
for habitat in metrics['habitats']:
    print(f"{habitat['name']}: {habitat['total_issues_found']} issues found")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Solve a QAOA problem
async function solveQAOA() {
    const response = await axios.post(`${BASE_URL}/solve/`, {
        issue: 'Solve a 4-node max-cut problem using QAOA'
    });

    console.log('Solution:', response.data.solution);
    console.log('Intent:', response.data.classification.intent);

    if (response.data.quantum_result) {
        console.log('Eigenvalue:', response.data.quantum_result.eigenvalue);
    }
}

// Monitor metrics
async function monitorMetrics() {
    const response = await axios.get(`${BASE_URL}/metrics/`);
    const { metrics, habitats } = response.data;

    console.log('=== Organism Performance ===');
    console.log(`Success Rate: ${(metrics.quantum_solver_success_rate * 100).toFixed(1)}%`);
    console.log(`Avg Response Time: ${metrics.average_response_time.toFixed(2)}s`);
    console.log(`\nActive Habitats: ${habitats.length}`);
}

solveQAOA().then(() => monitorMetrics());
```

---

## Multi-Habitat Usage

### Configuring Multiple Habitats

```yaml
# config.yaml
genes:
  web_scraping:
    enabled_habitats:
      - name: "github_discussions"
        url: "https://github.com/Qiskit/qiskit/discussions"
        enabled: true
        priority: 1

      - name: "stackoverflow"
        url: "https://stackoverflow.com/questions/tagged/qiskit"
        enabled: true
        priority: 2
```

### Monitoring Habitat Performance

```python
import requests

metrics = requests.get("http://localhost:8000/metrics/").json()

print("Habitat Performance:")
for habitat in metrics['habitats']:
    print(f"\n{habitat['name']}:")
    print(f"  Enabled: {habitat['enabled']}")
    print(f"  Total Issues: {habitat['total_issues_found']}")
    print(f"  Last Scraped: {habitat['last_scraped']}")
```

---

## Metrics and Monitoring

### Real-Time Monitoring Script

```python
#!/usr/bin/env python3
"""
Real-time organism monitoring dashboard
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_dashboard():
    # Get metrics
    metrics_resp = requests.get(f"{BASE_URL}/metrics/").json()
    health_resp = requests.get(f"{BASE_URL}/health/").json()

    m = metrics_resp['metrics']

    # Clear screen
    print("\033[2J\033[H")  # ANSI escape codes

    print("="*60)
    print(f"  🧬 QiskitCommunitySolver Organism Dashboard")
    print(f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    print(f"\n📊 PERFORMANCE METRICS")
    print(f"  Generation: {health_resp['generation']}")
    print(f"  Uptime: {m['uptime_seconds']:.0f}s ({m['uptime_seconds']/3600:.1f}h)")
    print(f"  Issues Processed: {m['total_issues_processed']}")
    print(f"  Success Rate: {m['quantum_solver_success_rate']:.1%}")
    print(f"  Avg Confidence: {m['average_confidence']:.2f}")
    print(f"  Avg Response Time: {m['average_response_time']:.2f}s")

    print(f"\n🌍 HABITAT STATISTICS")
    for habitat in metrics_resp['habitats']:
        status = "✅" if habitat['enabled'] else "❌"
        print(f"  {status} {habitat['name']}: {habitat['total_issues_found']} issues")

    print(f"\n💡 SOLUTIONS")
    print(f"  Successful: {m['successful_solutions']}")
    print(f"  Failed: {m['failed_solutions']}")

    print(f"\n🧬 EVOLUTION")
    print(f"  Mutations Triggered: {m['total_mutations_triggered']}")
    print(f"  Classification Accuracy: {m['classification_accuracy']:.1%}")

if __name__ == "__main__":
    while True:
        try:
            print_dashboard()
            time.sleep(5)  # Update every 5 seconds
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
```

**Usage:**
```bash
python monitor_organism.py
```

---

## GitHub Integration

### Setting Up GitHub Token

```bash
# Generate token at https://github.com/settings/tokens
# Permissions needed: read:discussion, read:repo

export GITHUB_TOKEN="ghp_yourPersonalAccessTokenHere"

# Run organism
python runtime/aura_bot.py --mode both
```

### Verifying GitHub Integration

```python
import os
from github import Github

# Check token
token = os.environ.get('GITHUB_TOKEN')
if token:
    g = Github(token)
    rate_limit = g.get_rate_limit()
    print(f"GitHub API Rate Limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    print(f"Reset at: {rate_limit.core.reset}")
else:
    print("GITHUB_TOKEN not set")
```

---

## Testing Examples

### Running All Tests

```bash
# Run full test suite
python tests/test_organism.py

# Run with verbose output
python tests/test_organism.py -v

# Run specific test class
python -m unittest tests.test_organism.TestHamiltonianSynthesis
```

### Testing Specific Functionality

```python
# test_custom.py
import unittest
from runtime.aura_bot import QiskitCommunitySolver

class TestCustom(unittest.TestCase):
    def setUp(self):
        self.organism = QiskitCommunitySolver(data_dir="./test_data")

    def test_my_vqe_problem(self):
        problem = "Find ground state of 2-qubit Heisenberg model"
        classification = self.organism._gene_classify_intent(problem)

        self.assertEqual(classification.intent, "VQE_Problem")

        hamiltonian = self.organism._gene_synthesize_hamiltonian(
            problem, classification.intent
        )

        self.assertEqual(hamiltonian.num_qubits, 2)

if __name__ == '__main__':
    unittest.main()
```

---

## Advanced Examples

### Custom Hamiltonian Injection

```python
from runtime.aura_bot import QiskitCommunitySolver
from qiskit.quantum_info import SparsePauliOp

organism = QiskitCommunitySolver()

# Create custom Hamiltonian
custom_h = SparsePauliOp.from_list([
    ("ZZZZ", 1.0),
    ("XXXX", 0.5),
    ("YYYY", 0.5)
])

# Solve directly
result = organism._gene_solve_vqe(custom_h)

print(f"Ground state energy: {result.eigenvalue}")
print(f"Optimization time: {result.optimizer_time}s")
```

### Batch Processing Issues

```python
import requests

issues = [
    "How do I implement VQE for H2?",
    "Solve max-cut with QAOA",
    "Find ground state of Ising model",
    "Optimize ansatz depth for VQE"
]

results = []
for issue in issues:
    response = requests.post(
        "http://localhost:8000/solve/",
        json={"issue": issue}
    )
    results.append(response.json())

# Analyze results
for issue, result in zip(issues, results):
    print(f"\nIssue: {issue}")
    print(f"Intent: {result['classification']['intent']}")
    print(f"Confidence: {result['classification']['confidence']:.2f}")
```

---

## Troubleshooting

### Common Issues

#### Issue: Import Errors
```bash
# Solution: Ensure all dependencies are installed
pip install -r requirements.txt --upgrade
```

#### Issue: GitHub Rate Limiting
```python
# Check your rate limit
from github import Github
g = Github(token)
print(g.get_rate_limit())

# Solution: Use authenticated token or wait for reset
```

#### Issue: Qiskit Not Found
```bash
# Ensure Qiskit is properly installed
pip install qiskit>=1.0.0 qiskit-aer qiskit-algorithms
```

---

## Production Deployment

### Using Docker (Example)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GITHUB_TOKEN=""
ENV DATA_DIR="/data"

CMD ["python", "runtime/aura_bot.py", "--mode", "both", "--port", "8000"]
```

```bash
# Build and run
docker build -t dnalang-organism .
docker run -p 8000:8000 -e GITHUB_TOKEN="your_token" dnalang-organism
```

---

## Support

For issues or questions:
1. Check [docs/ENHANCEMENTS.md](ENHANCEMENTS.md) for detailed feature documentation
2. Review test examples in [tests/test_organism.py](../tests/test_organism.py)
3. Open an issue on GitHub

---

**Happy Quantum Programming with DNALang! 🧬⚛️**
