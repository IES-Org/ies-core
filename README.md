# <img src="./assets/images/IES-logo-dark.png" alt="IES Logo" width="50" align="absmiddle"> Core Ontology (ies-core)

**Repository:** `IES Core Ontology (ies-core)`<br>
**Description:** `A mid-level ontology built upon IES-Top providing a common foundational layer of patterns and concepts useful for expressing information in all manner of domains.`<br>
**Repository Status:** `In development`

---

## Overview

A RDF mid-level ontology built upon IES-Top providing a common foundational layer of patterns and concepts useful for expressing information in all manner of domains. Patterns such as Activities, Replaceable Parts, Characteristics and Representations. This also includes lower-level concepts like Persons, Locations etc. Core replaces the top layers of IES4. Domain specific ontologies are expected to be built upon IES-Core. 

Important artefacts include:
- [Briefing pack (start here)](./docs/IES_Top_and_Core_Release_Candidate_1-Briefing_Pack_v1.0.pdf)
- [RDF serialisation of the ontology](./spec/ies-core.ttl)
- [Accompanying documentation](./docs/ies-core.md)

## Work in progress
This is not a finished piece of work. More development is still required. This release candidate (RC1) is provided to give the community the opportunity to review and comment. Feedback will be taken into two subsequent release candidates (RC2 and RC3) before the final publication in spring/summer 2026.

Specific work that is still to be done:
1. Develop IES-Core class and property definitions (with support from the community). The IES-Core RC1 definitions are drafts and many of them carry-over from IES4. We have the aspiration of creating definitions based on spatial-temporal extents.
2. Update the Location pattern in light of work being done in the community regarding the integration of IES with GeoSparql.
3. Update Measurements pattern in light of new analysis conducted in this area by members of the community.
4. Test and validate Entitlement/Rights pattern.
5. Test and validate Accounts pattern.
6. Develop a general Registration pattern (for use cases such as registeredCountry (for ships and companies) and registeredPort (for ships)).
7. Redeveloping NamingScheme following change to how IES is extended.

## Changelog
See [CHANGELOG](./CHANGELOG.md) for a list of changes in each release.

## Licensing

This repository contains both source code and documentation, each released under separate terms:  

- **Code** – Licensed under the [MIT License](./LICENSE.md)  
- **Documentation** – Licensed under the [Open Government Licence v3.0 (OGL-UK-3.0)](./OGL_LICENSE.md)  

By contributing to this repository, you agree that your contributions will be licensed under these terms.

---
© Crown Copyright 2025.