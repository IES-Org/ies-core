# Contribution Guidelines

**Repository:** `Information Exchange Standard (IES) Core Ontology`  
**Description:** `Guidelines for issue reporting, documentation suggestions, and the IES controlled contribution model.`

<!-- SPDX-License-Identifier: OGL-UK-3.0 -->

Thank you for your interest in this repository. The IES Core ontology is built upon [IES Top](https://github.com/IES-Org/ies-top), providing a shared common layer of patterns and concepts for representing information across multiple domains. In most cases, proposed changes will be more appropriately directed toward domain-specific, lower-level modules. Consequently, updates to the Core Ontology are expected only where requirements span many domains and justify inclusion at this level of the IES Ontology Stack.

The Information Exchange Standard (IES) is developed and maintained as a cross-government initiative with contributions from various UK government organisations and technical support from approved contributors and subject matter specialists.

The Department for Business and Trade (DBT) is the current custodian of this repository and the GitHub organisation, acting on behalf of a broader group of stakeholders.

IES follows an **open-source governance model**, where all code is **publicly available** under open-source licences, and collaboration is invited from **approved contributors**. While direct code contributions from the general public are not currently accepted, we **welcome feedback, issue reporting, and documentation suggestions**.

To see a list of contributing organisations and individuals, refer to [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) and the GitHub contributor insights page at [Contributors](https://github.com/IES-Org/ies-core/graphs/contributors).

---

## How You Can Contribute

Public users and contributors are encouraged to engage in the following ways:

- **Reporting bugs and issues** – If you find a problem, please open a GitHub issue.
- **Suggesting documentation improvements** – Propose clarifications or additions to existing documentation.
- **Providing structured feedback** – Use GitHub Issues to share ideas and enhancement suggestions.

All input is welcome and will be reviewed by maintainers, but prioritisation is subject to IES goals and delivery timelines.

At this time, IES does not accept **public pull requests (PRs)** or **direct code contributions**. Code and ontology contributions are made by members of the **IES Technical Group (TG)** - who are made up of approved contributors working under formal arrangements who have write access to this repository. For details on the TG's role and the issue lifecycle, see [Issue Workflow and Governance](#issue-workflow-and-governance). For maintainer contact details, refer to [MAINTAINERS.md](MAINTAINERS.md).

---

## Reporting Issues

If you encounter a bug, error, or inconsistency, please follow these steps:

1. Check for an existing issue under [Issues](https://github.com/IES-Org/ies-core/issues).
2. Open a new issue if none exists. Use one of the available templates.
3. Provide a clear and detailed description, including steps to reproduce if applicable.
4. Use labels (bug, documentation, enhancement, etc.) where appropriate.

For security-related concerns, do not submit a public issue. Follow our [Responsible Disclosure process](SECURITY.md).

---

## Issue Workflow and Governance

Technical issues relating to the IES Core Ontology should be raised as **GitHub Issues**. This ensures:

- A single shared location for problem reporting
- Transparent discussion history
- Clear tracking and assignment
- Visibility for the whole community

GitHub is the starting point for all technical work on IES Core.

### IES Technical Group (TG)

The **IES Technical Group (TG)** is responsible for leading the development of Ontology and/or RDF Implementation changes, which must be initiated using GitHub Issues. All TG members have write permissions to this repository. The TG is collectively responsible for:

- **Triaging** all GitHub Issues relating to the IES Core Model
- **Categorising** issues and assigning appropriate technical owners
- **Determining** whether issues belong in the Core Model space or should be redirected to a domain working group
- **Seeking Quality Assurance** from the IES Core Maintenance Team
- **Managing escalation** to the IES Steering Group once technical discussion is complete

For further details, see [Issue Lifecycle](#issue-lifecycle) below.

### Issue Lifecycle

The process for handling technical issues is as follows:

1. An issue is raised on GitHub.
2. The TG triages the issue and assigns an appropriate **technical owner**.
3. Technical discussion and development of options takes place primarily through **GitHub Issues and comment threads**, which act as the authoritative record for the issue.
4. The issue may also be discussed at domain working groups. However:
   - The appropriate technical owner remains responsible and must be informed about the discussions.
   - Any technical outputs or conclusions from domain working group discussions must be **summarised and recorded on GitHub** in a timely manner so that GitHub remains the authoritative record.
5. Once an agreed approach is reached by the technical community, the appropriate technical owner documents the **final proposal** on GitHub as a pull request (PR). This must include:
   - Appropriate updates to the UML model, RDF serialisation, and documentation
   - The rationale for the proposed approach
   - Any alternative options considered
   - Relevant impacts, dependencies, or constraints
6. The PR undergoes **quality assurance** by the IES Core Maintenance Team to ensure ontological rigour, correct RDF implementation, and alignment with cross-government requirements.
7. Only when this work is complete and the associated PR approved by at least two of the three **IES Core Maintainers** (who were neither the **Author** of the PR nor the **Technical Owner**), should the TG place the issue on the **IES Steering Group** agenda for formal agreement.
8. Only following IES Steering Group formal agreement can the pull request (PR) then be merged into `main`.

**Note:** For changes relating to governance (e.g. contribution policies, maintainer roles, decision-making processes), the same lifecycle applies, but such changes must first be formally recommended by the TG before the associated pull request is raised, and the PR must receive formal IES Steering Group approval before it can be merged.

### Steering Group Submissions

When an item reaches the IES Steering Group, the purpose must be explicitly stated. For example:

- **Approval** of a proposed modelling pattern
- **Endorsement** of a consistent approach
- **Request for policy direction** where domain groups cannot reach consensus

The Steering Group should not be expected to resolve raw or undeveloped technical questions that have not been first discussed by the wider technical community.

---

## Minimum Review Period

New proposals and issues must remain open on GitHub for a clearly defined period (typically **3 to 4 weeks from the date they are raised**) before they can be placed on the IES Steering Group agenda. This:

- Gives contributors time to comment
- Prevents proposals being escalated the day they are published
- Improves the quality of technical discussion
- Avoids rushed or uninformed decision making

Additionally, pull requests that propose changes to governance (e.g. contribution policies, maintainer roles, decision-making processes) must remain open for a minimum of 4 weeks to allow for comment from stakeholders.

---

## Documentation Feedback

If you find an error, need clarification, or have suggestions for improving documentation:

1. Open a GitHub issue using the `documentation` label.
2. Describe the suggestion clearly, referencing specific content where possible.
3. Structured, specific feedback helps us respond more effectively.

Documentation updates are prioritised based on user impact and strategic relevance.

---

## IES Approach to Open-Source Development

- **All code is published under open-source licences.**
- **Development is led by contributors from government and approved contributors.**
- **Feedback is welcome and helps shape ongoing development.**

---

## Branching Strategy

Development work is carried out on feature branches created from `main`. Pull requests are used to propose changes back into `main`, and must follow the approval process described in the [Issue Lifecycle](#issue-lifecycle). Releases are tagged using the semantic versioning format `MAJOR.MINOR.PATCH`.

---

## Contribution Licensing

By submitting feedback, documentation suggestions, or issue reports, you acknowledge that any resulting contributions will be licensed under the same terms as this repository:

- Code (if applicable) is licensed under the **MIT License**.
- Documentation is licensed under the **Open Government Licence v3.0 (OGL v3.0)**.

All contributions are considered Crown copyright.

---

## Repository Maintainers

For current maintainers and contact information, refer to [MAINTAINERS.md](MAINTAINERS.md).
Maintainers review issues, guide contributions, and ensure alignment with programme objectives.

---

**Maintained as part of the Information Exchange Standard initiative.**

© Crown Copyright 2026. This work is currently under the custodianship of the Department for Business and Trade (UK), acting on behalf of a cross-government group of stakeholders.
Licensed under the Open Government Licence v3.0.

For full licensing terms, see [OGL_LICENSE.md](OGL_LICENSE.md).
