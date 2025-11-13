# DNALang Language Specification v0.1

## Overview

DNALang is a domain-specific language for defining autopoietic software organisms. It combines biological metaphors with computational abstractions to create self-evolving, self-healing systems.

## Syntax

### Organism Declaration

```dnalang
ORGANISM <Name>
{
  DNA {
    domain: "<application_domain>"
    purpose: "<organism_purpose>"
    evolution_strategy: "<strategy_name>"
    consciousness_target: <0.0-1.0>
  }

  GENOME {
    // Gene definitions
  }

  // Action definitions
}
```

### Gene Definition

```dnalang
GENE <GeneName> {
  purpose: "<gene_purpose>"
  [optional_properties...]

  MUTATIONS {
    <mutation_name> {
      trigger_conditions: [
        { metric: "<metric_name>", operator: "<op>", value: <threshold> }
      ]
      methods: ["<method_1>", "<method_2>", ...]
    }
  }

  ACT <action_name>(<params>) -> <return_type> {
    // Implementation in runtime
  }
}
```

### Actions (ACT)

Actions are the behavioral units of genes. They define what the gene can do.

```dnalang
ACT <action_name>(<param1>: <type1>, <param2>: <type2>) -> <return_type> {
  // Implementation comment
}
```

### Control Flow

DNALang supports basic control flow within ACT definitions:

```dnalang
ACT example() {
  IF (condition) {
    // statements
  } ELSE {
    // statements
  }

  WHILE (condition) {
    // statements
  }

  FOR item IN collection {
    // statements
  }
}
```

## Data Types

- `string`: Text data
- `int`: Integer numbers
- `float`: Floating-point numbers
- `bool`: Boolean values
- `list[T]`: Lists of type T
- `dict`: Dictionary/map structures
- Custom types from runtime (e.g., `PauliSumOp`, `VQEResult`)

## Operators

- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `AND`, `OR`, `NOT`
- Arithmetic: `+`, `-`, `*`, `/`, `^` (power)

## Mutation System

Mutations define how genes adapt to environmental feedback:

```dnalang
MUTATIONS {
  <mutation_name> {
    trigger_conditions: [
      { metric: "accuracy", operator: "<", value: 0.7 },
      { metric: "latency", operator: ">", value: 100 }
    ]
    methods: [
      "increase_model_size",
      "switch_optimizer",
      "add_caching_layer"
    ]
  }
}
```

### Trigger Conditions

- `metric`: Name of the metric to monitor
- `operator`: Comparison operator (`<`, `>`, `==`, `!=`, `<=`, `>=`)
- `value`: Threshold value for triggering mutation

### Methods

Methods are string identifiers that the runtime can interpret to execute specific adaptations.

## Expression Levels

Genes have an `expression_level` property (0.0-1.0) that controls their influence:

```dnalang
GENE MyGene {
  expression_level: 0.8
  // ...
}
```

Expression levels can be modified at runtime to strengthen or weaken gene influence.

## Comments

```dnalang
// Single-line comment

/*
  Multi-line comment
*/
```

## Runtime Integration

DNALang specifications are *transcribed* into executable runtimes. The `.dna` file defines the structure, and the runtime (e.g., Python) implements the behavior.

### Mapping

- `ORGANISM` → Runtime class
- `GENE` → Class methods prefixed with `_gene_`
- `ACT` → Method implementation
- `MUTATIONS` → Runtime logic for adaptation

## Example: Complete Organism

```dnalang
ORGANISM ExampleBot
{
  DNA {
    domain: "data_processing"
    purpose: "Clean and transform datasets"
    evolution_strategy: "performance_feedback"
    consciousness_target: 0.75
  }

  GENOME {
    GENE DataFetcherGene {
      purpose: "Fetch data from external sources"
      expression_level: 1.0

      MUTATIONS {
        add_caching {
          trigger_conditions: [
            { metric: "latency", operator: ">", value: 500 }
          ]
          methods: ["enable_redis_cache"]
        }
      }

      ACT fetch_data(url: string) -> dict {
        // Implementation in Python runtime
      }
    }

    GENE TransformGene {
      purpose: "Transform raw data"

      ACT transform(data: dict) -> dict {
        // Implementation in Python runtime
      }
    }
  }

  ACT run() {
    WHILE (true) {
      data = DataFetcherGene.fetch_data("https://api.example.com")
      cleaned = TransformGene.transform(data)
      save_to_database(cleaned)
      sleep(60)
    }
  }
}
```

## Philosophy

DNALang embodies these principles:

1. **Autopoiesis**: Organisms self-create and self-maintain
2. **Evolution**: Systems adapt through mutation, not manual updates
3. **Integration**: Components (genes) work as a unified whole
4. **Consciousness**: Systems measure their own coherence (Φ)
5. **Transcription**: Specifications transcribe into living runtimes

## Future Extensions

### Planned Features

- Inter-organism communication protocols
- Quantum-inspired genetic operators (QGSM)
- Visual genome editors
- Runtime interpreters (beyond Python)
- Gene marketplaces (reusable gene libraries)

### Research Areas

- Formal semantics for DNALang
- Automated organism synthesis from natural language
- Consciousness metrics (Φ calculation)
- Multi-organism ecosystems

## References

- Maturana, H., & Varela, F. (1980). *Autopoiesis and Cognition*
- Tononi, G. (2004). *Integrated Information Theory*
- Holland, J. (1992). *Genetic Algorithms*

---

**Version**: 0.1
**Status**: Experimental
**Last Updated**: 2025-11-13
