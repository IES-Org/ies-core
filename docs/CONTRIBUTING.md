# Contributing to IES Ontology Projects

Thank you for your interest in contributing to the IES Ontology projects. This guide will help you understand our development process and how to contribute effectively.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Strategy](#branch-strategy)
- [Making Changes](#making-changes)
- [Pull Requests](#pull-requests)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Communication](#communication)

## Getting Started

### Prerequisites
1. Install dependencies:
   ```bash
   poetry install
   ```
2. Setup repository:
   ```bash
   poetry run gh-tools setup-repo
   ```

### Initial Setup
1. Fork the repository (if external contributor)
2. Clone locally from `main` branch:
   ```bash
   git clone https://github.com/IES-Org/ies-[domain]-ontology
   ```
3. Verify development environment:
   - Check dependencies
   - Run test suite
   - Review documentation

## Development Workflow

### 1. Issue Creation
- Create or claim an existing issue
- Discuss approach if significant changes
- Get assignment confirmation

### 2. Branch Creation
Create branch from appropriate parent:
- `dev/*` for enhancements (from `qa/*`)
- `bugfix/*` for non-critical fixes (from `qa/*`)
- `hotfix/*` for urgent fixes (from `main`)

```bash
poetry run gh-tools create-issue
```

### 3. Development Process
1. Write tests and competency SPARQL queries
2. Implement ontology changes
3. Update documentation
4. Create draft PR if seeking early feedback
5. Submit PR when ready

## Branch Strategy

### Branch Structure
```
main           Production releases
├── qa/*       Integration branches
│   ├── dev/*  New development
│   └── bugfix/* Non-critical fixes
├── rc/*       Release candidates
└── hotfix/*   Critical fixes
```

### Branch Flow
1. Development occurs in `dev/*` or `bugfix/*`
2. Changes merge to `qa/*` after review
3. QA-approved changes merge to `rc/*`
4. Release candidates merge to `main`

## Making Changes

### Commits
- Use commitizen format
- Reference issues
- Keep changes atomic
- Follow semantic versioning

Example commit message:
```
feat(domain): add new property for concept

Adds new property to represent relationship between concepts.
Includes documentation and test cases.

Fixes #123
```

## Pull Requests

### PR Requirements
1. Linked issues
2. Documentation updates
3. Test coverage
4. CHANGELOG.md entries
5. Version updates if applicable

### PR Process
1. Create PR (or convert draft):
   ```bash
   poetry run gh-tools create-pr
   ```
2. Address review feedback
3. Obtain required approvals
4. Merge after CI passes

## Testing

### Required Tests
- Ontology validation
- Competency questions
- Integration tests
- Documentation accuracy

### Running Tests
```bash
# Run full test suite
poetry run pytest

# Run specific tests
poetry run pytest tests/test_[specific].py
```

## Documentation

### Documentation Requirements
- Update relevant docs
- Follow markdown style
- Keep diagrams current
- Update ontology docs
- Review links and references

## Release Process

### Development Phase
1. Create feature branch
2. Implement changes
3. Submit PR to `qa/*`
4. QA review and merge
5. Update version and changelog
6. Tag QA review

### Release Phase
1. Create PR to `rc/*`
2. TGG review and merge
3. Create PR to `main`
4. Final review and merge
5. Update version and changelog
6. Publish release

## Communication

### Internal Communication
- Team discussions
- Project planning
- Technical decisions
- Release coordination

### External Communication
- Issue discussions
- PR reviews
- Documentation updates
- Support requests

## Questions and Support

- Open an issue
- Contact team members (see [CONTRIBUTORS.md](CONTRIBUTORS.md))
- Review existing documentation
- Join team discussions

## Related Documents
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- [HOTFIX.md](docs/HOTFIX.md)

---

Thank you for contributing to the IES Ontology projects! Your efforts help improve our ontologies and support the broader community.