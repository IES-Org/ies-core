![IES Logo](assets/images/IES-logo-dark.png)

# Information Exchange Standard (IES) - Core Ontology (ies-core)

**Repository:** `Information Exchange Standard (IES) Core Ontology`  
**Description:** `A mid-level ontology built upon ies-core providing a common foundational layer of patterns and concepts useful for expressing information in all manner of domains.`  
**Repository Status:** `In development`

---

## Table of Contents

- [Overview](#overview)
  - [Important Artefacts](#important-artefacts)
- [Governance and Custodianship](#governance-and-custodianship)
- [Repository Contents](#repository-contents)
- [Licensing](#licensing)
- [Contributions and Feedback](#contributions-and-feedback)
- [Changelog](#changelog)
- [References](#references)

---

## Overview

A RDF mid-level ontology built upon ies-core providing a common foundational layer of patterns and concepts useful for expressing information in all manner of domains. Patterns such as Activities, Replaceable Parts, Characteristics and Representations. This also includes lower-level concepts like Persons, Locations etc. Core replaces the top layers of IES4. Domain specific ontologies are expected to be built upon IES-Core.

### Important Artefacts

- [Briefing pack (start here)](./docs/IES_Top_and_Core_Release_Candidate_1-Briefing_Pack_v1.0.pdf)
- [RDF serialisation of the ontology](./spec/ies-core.ttl)
- [Accompanying documentation](./docs/ies-core.md)

## Governance and Custodianship

While the Information Exchange Standard is not a legal entity, it represents a collaborative effort across multiple UK government bodies, including (but not limited to):

* Department for Business and Trade (DBT) *(custodian of this repository)*
* Defence Science and Technology Laboratory (Dstl)
* Ministry of Defence (MOD)
* Metropolitan Police
* Foreign, Commonwealth & Development Office (FCDO)
* Home Office (HO)
* HM Revenue & Customs (HMRC)

These organisations act as the custodians and decision-makers for the ongoing development of the Standard.

The development of this work is supported by private sector suppliers and technical specialists engaged through formal agreements. Their contributions are formally recognized in the [ACKNOWLEDGEMENTS.md](./ACKNOWLEDGEMENTS.md) file.

## Repository Contents

This repository includes:

- **[ACKNOWLEDGEMENTS.md](./ACKNOWLEDGEMENTS.md)** – Formal recognition of contributors
- **[CHANGELOG.md](./CHANGELOG.md)** – List of notable changes and release history
- **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)** – Expected behaviour and reporting guidelines
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** – Guidelines for contributing to this project
- **[LICENSE.md](./LICENSE.md)** – MIT License for source code
- **[OGL_LICENSE.md](./OGL_LICENSE.md)** – Open Government Licence for documentation
- **[MAINTAINERS.md](./MAINTAINERS.md)** – Maintainer contact information
- **[NOTICE.md](./NOTICE.md)** – Legal notices
- **[SECURITY.md](./SECURITY.md)** – Security policy and vulnerability reporting

**Directories:**

- **[assets/images/](./assets/images/)** – Project images and logos
- **[docs/](./docs/)** – Project documentation and reports
  - **[diagrams/](./docs/diagrams/)** – UML and other diagrams
  - **[ies-core.md](./docs/ies-core.md)** – Additional documentation
  - **[IES_Top_and_Core_Release_Candidate_1-Briefing_Pack_v1.0.pdf](./docs/IES_Top_and_Core_Release_Candidate_1-Briefing_Pack_v1.0.pdf)** – Briefing pack
- **[spec/](./spec/)** – Ontology specification files
  - **[ies-core.ttl](./spec/ies-core.ttl)** – RDF serialisation of the ontology
  - **[validation_artefacts/](./spec/validation_artefacts/)** – SHACL validation artefacts and test data

For further information, visit the [IES website](https://www.informationexchangestandard.org).

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

## Licensing

This repository contains both source code and documentation, each released under separate terms:

- **Code** – Licensed under the [MIT License](./LICENSE.md)
- **Documentation** – Licensed under the [Open Government Licence v3.0 (OGL-UK-3.0)](./OGL_LICENSE.md)

By contributing to this repository, you agree that your contributions will be licensed under these terms.

© Crown Copyright 2026.

## Contributions and Feedback

We welcome:

* Feedback and structured suggestions
* Bug reports and clarifications
* Requests for extensions or additional documentation

Please see:

* [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines
* [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) for expected behaviour and reporting concerns
* [MAINTAINERS.md](./MAINTAINERS.md) for maintainer contact information

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a list of changes in each release.

## References

- [1] [de Cesare, S., &amp; Partridge, C. (2016). *BORO as a Foundation to Enterprise Ontology.* *Journal of Information Systems*, 30(2), 83–112.](https://doi.org/10.2308/isys-51428)
- [2] [Florio, S., &amp; Linnebo, Ø. (2021). *The Many and the One: A Philosophical Study of Plural Logic.* Oxford University Press.](https://library.oapen.org/bitstream/handle/20.500.12657/50697/9780198791522.pdf)
- [3] [Partridge, C., de Cesare, S., Mitchell, A., Gailly, F., &amp; Khan, M. (2017). *Developing an Ontological Sandbox: Investigating Multi-Level Modelling’s Possible Metaphysical Structures.* *MODELS 2017*, 2019, 226–234.](http://ceur-ws.org/Vol-2019/multi_3.pdf)
- [4] [Florio, S., &amp; Linnebo, Ø. (2022). *Core Constructional Ontology: The Foundation for the Top-Level Ontology of the Information Management Framework.*](https://borosolutions.net/core-constructional-ontology)

---
