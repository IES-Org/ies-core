# Specification Overview

This directory contains SHACL shapes and test data for validating the IES Top Ontology.

- **[ies-core.ttl](../ies-core.ttl)** – Main RDF serialization of the IES Top Ontology, including ontology metadata, classes, and properties.
- **[validation_artefacts/](./validation_artefacts/)** – Contains SHACL shapes and test data for ontology validation and conformance:
  - **[BirthStateShape.shacl.ttl](./validation_artefacts/BirthStateShape.shacl.ttl)** – Makes sure that BirthState links to a NaturalState via isAStartOf
  - **[DeathStateShape.shacl.ttl](./validation_artefacts/DeathStateShape.shacl.ttl)** – Ensures DeathState links to a NaturalState via isAEndOf.
  - **[ICalRepresentationShape.shacl.ttl](./validation_artefacts/ICalRepresentationShape.shacl.ttl)** – Validates ICalRepresentation date/time properties are in UTC.
  - **[PersonState.shacl.ttl](./validation_artefacts/PersonState.shacl.ttl)** – Validates PersonState properties and restricts person-only properties to Person states.
  - **[hasIdentifiedGenderShape.shacl.ttl](./validation_artefacts/hasIdentifiedGenderShape.shacl.ttl)** – Ensures hasIdentifiedGender connects PersonState to Gender.
  - **[hasSkillShape.shacl.ttl](./validation_artefacts/hasSkillShape.shacl.ttl)** – Ensures hasSkill connects PersonState to Skill.
  - **[test_data/](./validation_artefacts/test_data/)** – Example data for SHACL validation:
    - **[README.md](./validation_artefacts/test_data/README.md)** – Documentation for test data.
    - **[invalid-shacl-PersonState.ttl](./validation_artefacts/test_data/invalid-shacl-PersonState.ttl)** – Failing test case: Organisation state with gender, missing required Person properties.
    - **[invalid-shacl-PersonState2.ttl](./validation_artefacts/test_data/invalid-shacl-PersonState2.ttl)** – Failing test case: Organisation state with name, missing required Person properties.
    - **[invalid.ttl](./validation_artefacts/test_data/invalid.ttl)** – Failing test case: ICalRepresentation with mismatched timezones in start/end dates.
    - **[valid-shacl-PersonState.ttl](./validation_artefacts/test_data/valid-shacl-PersonState.ttl)** – Passing test case: Person state with gender, name, and skill.
    - **[valid-shacl-PersonState2.ttl](./validation_artefacts/test_data/valid-shacl-PersonState2.ttl)** – Passing test case: Organisation state with valid name.
    - **[valid.ttl](./validation_artefacts/test_data/valid.ttl)** – Passing test case: ICalRepresentation with valid date/time formats.

Use these artefacts to implement, extend, or validate solutions based on the IES Top Ontology.
