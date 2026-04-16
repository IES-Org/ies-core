# Specification Overview

This directory contains SHACL shapes and test data for validating the IES Top Ontology.

## Table of Contents

- [Directory Structure](#directory-structure)
- [SHACL Data Validation Testing](#shacl-data-validation-testing)
  - [Prerequisites](#prerequisites)
  - [Test valid data](#test-that-valid-data-conforms-true)
  - [Test invalid data](#test-that-invalid-data-conforms-false)
  - [Notes](#notes)

## Directory Structure

- **[ies-core.ttl](../ies-core.ttl)** – Main RDF serialization of the IES Top Ontology, including ontology metadata, classes, and properties.
- **[validation_artefacts/](./validation_artefacts/)** – Contains SHACL shapes and test data for ontology validation and conformance:
  - **[test_data/](./validation_artefacts/test_data/)** – Example data for SHACL validation:

Use these artefacts to validate solutions based on the IES Top Ontology.

## SHACL Data Validation Testing

This section describes how to test RDF data files against SHACL shapes using [pySHACL](https://github.com/RDFLib/pySHACL).

### Prerequisites

- Install [pySHACL](https://github.com/RDFLib/pySHACL):

```bash
pip install pyshacl
```

- Test your data with pyshacl

```bash
pyshacl -s (path to shacl file) -d (path to invalid_data file)
```

### Test that valid data conforms True

```bash
pyshacl -s standard/ies5_core_shacl/ICalRepresentationShape.shacl.ttl -d tests/ICalRepresentationShape/valid.ttl
```

### Test that invalid data conforms False

```bash
pyshacl -s standard/ies5_core_shacl/ICalRepresentationShape.shacl.ttl -d tests/ICalRepresentationShape/invalid.ttl
```

### Notes

- The `-s` flag specifies the SHACL shape file.
- The `-d` flag specifies the data file to validate.

---

© Crown Copyright 2026.
