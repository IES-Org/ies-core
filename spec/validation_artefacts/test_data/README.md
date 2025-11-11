## Test that valid data conforms True

`pyshacl -s (path to shacl file) -d (path to valid_data file)`

e.g.

```bash
pyshacl -s standard/ies5_core_shacl/ICalRepresentationShape.shacl.ttl -d tests/ICalRepresentationShape/valid.ttl
```

## Test that invalid data conforms False


`pyshacl -s (path to shacl file) -d (path to invalid_data file)`

e.g.

```bash
pyshacl -s standard/ies5_core_shacl/ICalRepresentationShape.shacl.ttl -d tests/ICalRepresentationShape/invalid.ttl
```
