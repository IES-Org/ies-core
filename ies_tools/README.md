# IES Tools

## Important
These common tools are maintained in the [IES Ontology Template][ont-template] repository. The tools are automatically updated daily in the domain ontology repositories using the `sync-tools.yml` GitHub workflow.

**DO NOT MODIFY THE TOOLS IN THIS REPOSITORY DIRECTLY. RATHER MAKE CHANGES IN [IES Ontology Template][ont-template]**

## Overview
A collection of automation tools for IES projects. Currently, includes:
- GitHub automation tools for managing issues and workflows
- Build tools for diagrams, ontology formats, and validation

## Directory Structure
```ascii
.
├── ies-tools/
│   └── src/
│       ├── build/            # Build automation tools
│       │   └── build.py      # CLI for generating diagrams and ontology formats
│       └── github-tools/     # GitHub automation tools
│           └── github.py     # CLI for managing GitHub issues and workflows
│           └── README.md     # Specific README for the GitHub tools script
├── tests/                    # Test directory
│   ├── integration/
│   └── unit/
├── README.md                 # This README file
```

## Usage
### Build Tools
The build package provides tools for generating diagrams, SHACL SHAPEs, and alternative RDF formats:

```bash
# Generate diagrams from docs/diagrams/
poetry run ies-build build-diagrams

# Generate SHACL shapes from TTL
poetry run ies-build build-shacl ontology.ttl

# Generate RDF formats (ttl, xml, n3, json-ld) from the default source ontology file, `src/ontology.ontology.ttl`
poetry run ies-build build-ontology
# ... or use a specific source `.ttl` and specific output formats
poetry run ies-build build-ontology /path/to/ontology.ttl -f xml -f n3  # specific formats
```

### GitHub Tools
The github-tools package provides a CLI for managing GitHub issues and workflows:
    
```bash
# Create a new feature request
poetry run gh-tools create-issue

# Create a pull request
poetry run gh-tools create-pr

# Sync your local repo with the remote
poetry run gh-tools sync
```

Run `poetry run gh-tool --help` or `poetry run ies-build --help` to see all available commands.

## Contributing
  1. Make changes in [IES Ontology Template repository][ont-template]
  2. Add tests for new features
  3. Test in a "consumer" domain ontology repository created from the template
  4. Once verified, create a PR on the `main` branch. The updated IES tools will be automatically synced to all domain ontology repositories.

[ont-template]: http://github.com/IES-Org/ies-ontology-template
