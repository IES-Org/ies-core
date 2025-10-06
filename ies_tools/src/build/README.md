# IES Build Tools

A toolkit for IES Ontology development providing diagram generation, format conversion, and validation capabilities.

## Features

- Diagram generation from source files
  - Mermaid (.mmd, .mermaid) diagrams
  - Graphviz (.dot) diagrams
  - Multiple output formats (SVG, PNG)
- Ontology format conversion and validation
  - SHACL shape generation from Turtle files
  - RDF format conversion (RDF/XML, N3, JSON-LD)
- Build directory management
- Error handling and logging
- Poetry integration

## Prerequisites

1. Python 3.9+
2. Poetry
3. Node.js and NPM (for Mermaid):
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs

   # macOS
   brew install node

   # Windows
   winget install OpenJS.NodeJS
   ```

4. Mermaid CLI:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

5. Graphviz:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install graphviz

   # macOS
   brew install graphviz

   # Windows
   winget install graphviz
   ```

## Installation

```bash
poetry install
```

## Usage

### Diagram Generation

```bash
# Generate all diagrams
poetry run ies-build build-diagrams

# Custom docs directory
poetry run ies-build build-diagrams --docs-dir /path/to/docs
```

### SHACL Shape Generation

```bash
# Generate SHACL shapes on default `/src/ontology/ontology.ttl` file
poetry run ies-build build-shacl

# From custom location
poetry run ies-build build-shacl path/to/ontology.ttl
```

### RDF Format Conversion

```bash
# Convert to all formats (RDF/XML, N3, JSON-LD) from the default `src/ontology/ontology.ttl` source file
poetry run ies-build build-ontology

# ... or use an alternative source and specific formats
poetry run ies-build build-ontology /path/to/ontology.ttl -f xml -f n3
```

### Directory Structure

```
ontology-repo/
├── docs/
│   └── diagrams/           # Source diagram files
│       ├── diagram1.mmd    # Mermaid diagram
│       └── diagram2.dot    # Graphviz diagram
├── src/
│   └── ontology/          # Source ontology files
│       └── ontology.ttl    # Input ontology
└── build/
    ├── docs/
    │   └── diagrams/      # Generated diagrams
    └── ontology/          # Generated files
        ├── ontology.shacl  # SHACL shapes
        ├── ontology.rdf    # RDF/XML format
        ├── ontology.n3     # N3 format
        └── ontology.json   # JSON-LD format
```

### SHACL Shape Generation Details

Generates SHACL shapes including:
- `sh:targetClass` for classes
- `sh:targetSubjectsOf` and `sh:targetObjectsOf` for properties

Example:
```ttl
# Input ontology.ttl
@prefix ies-common: <http://ies.data.gov.uk/ontology/ies-common#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ies-common:aCopyOf a owl:ObjectProperty ;
    rdfs:domain ies-common:IndividualDocument ;
    rdfs:range ies-common:WorkOfDocumentation .
```

```ttl
# Output ontology.shacl
@prefix ies-common: <http://ies.data.gov.uk/ontology/ies-common#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

ies-common:aCopyOfDomainShape a sh:NodeShape ;
    sh:class ies-common:IndividualDocument ;
    sh:severity sh:Warning ;
    sh:targetSubjectsOf ies-common:aCopyOf .

ies-common:aCopyOfRangeShape a sh:NodeShape ;
    sh:class ies-common:WorkOfDocumentation ;
    sh:severity sh:Warning ;
    sh:targetObjectsOf ies-common:aCopyOf .
```

## Troubleshooting

1. **Dependency Issues**
   - Verify installations: `node --version`, `mmdc --version`, `dot -V`
   - Reinstall if needed using package manager

2. **Build Issues**
   - Check directory structure matches expected layout
   - Verify write permissions in build directory
   - Check file locks

## Contributing

1. Navigate to [IES Common repository][ies-common-repo]
2. Add new features in `build.py`
3. Add tests under `tests/unit/`
4. Update documentation
5. Submit PR

## License

MIT - see [LICENCE][LICENSE]

[ies-common-repo]: https://github.com/IES-Org/ies-common
[LICENSE]: ../../../LICENSE