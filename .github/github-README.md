# GitHub Workflows and Issue Templates

This ontology template repository includes definitions for common GitHub workflows and issue templates used across multiple IES ontology development repositories.

## Contents

```ascii
.
├── CODEOWNERS
├── ISSUE_TEMPLATE
│   ├── create-issue.yml
├── github-README.md
└── workflows
    ├── create-issue.yml
    ├── create-ontology-repo.yml
    ├── ontology-qa-review.yml
    ├── ontology-release-candidate.yml
    ├── ontology-validation.yml
    ├── pr-checks.yml
    ├── README-create-ontology-repo.md
    ├── README-development-workflows.md
    ├── README-sync-ies-tools.md
    ├── setup-labels.yml
    └── sync-ies-tools.yml
```

## Usage

[Use this template][ont-template] to create a new repository by running the `create-ontology-repo.yml` workflow.

This will create a new ontology development repository with the workflows and issue templates from this template repository.

To keep the GitHub workflows and IES tools in sync, the `sync-ies-tools.yaml` workflow is scheduled to run weekly. If there are updates to the workflows or IES tools, a PR is created in the domain ontology repository. This enables the updated tools to be merged into the repository.

The GitHub workflows and IES tools can be used as they would be in any other repository.

## Contents

### Workflows

  - `sync-ies-tools.yml` - Syncs workflows and IES tools from the [ies-ontology-template][ont-template] repository to the domain ontology repository
  - `setup-labels.yml` - Sets up standard repository labels for issue tracking
  - `create-ontology-repo.yml` - Workflow to create a new ontology repository from this template
  - `create-issue.yml` - Creates a new issue and associated branch for either a `develop` or `bugfix` issue
  - `ontology-qa-review.yml` - *TBD Workflow for ontology QA review*
  - `ontology-release-candidate.yml` - *TBD Workflow for ontology release candidates*
  - `ontology-validation.yml` - *TBD Workflow for ontology validation*

### Issue Templates
  - `create-issue.yml` - GitHub workflow to open a new issue

## Contributing
When making changes to workflows or templates:

1. Make changes in the [IES Ontology template repository][ont-template] in a `dev` branch
2. Validate in a test consumer repository
3. Once confirmed working, merge changes into `main`
4. All 'consuming' (domain) ontology development repositories will receive the updates via the `sync-ies-tools` workflow, which is scheduled to run weekly.

[ont-template]: https://github.com/IES-Org/ies-ontology-template
