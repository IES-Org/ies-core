# SHACL Data Validation Testing

This README describes how to test RDF data files against SHACL shapes using [pySHACL](https://github.com/RDFLib/pySHACL).

## Prerequisites

- Install [pySHACL](https://github.com/RDFLib/pySHACL):

```bash
pip install pyshacl
```

- Test your data with pyshacl

```bash
pyshacl -s (path to shacl file) -d (path to invalid_data file)
```

## Test that valid data conforms True

```bash
pyshacl -s standard/ies5_core_shacl/ICalRepresentationShape.shacl.ttl -d tests/ICalRepresentationShape/valid.ttl
```

## Test that invalid data conforms False

```bash
pyshacl -s standard/ies5_core_shacl/ICalRepresentationShape.shacl.ttl -d tests/ICalRepresentationShape/invalid.ttl
```

## Notes

- The `-s` flag specifies the SHACL shape file.
- The `-d` flag specifies the data file to validate.
