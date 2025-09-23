# Create a New Repository from Template

⚠️ **WARNING**: This workflow should only be executed from the `ies-ontology-template` repository. Do not attempt to run it from ontology repositories that were created using this workflow, as it may lead to unexpected results.

## Overview

This [GitHub Actions][github-actions] workflow automates the process of creating a new ontology repository from the `ies-ontology-template` template. It performs the following tasks:

1. Creates a new repository from the template
2. Sets up a standard set of repository labels for issue tracking
3. Creates a GitHub Project for the new repository
4. Links the Project to the repository
5. Sets up the PROJECT_ID as a repository variable

## Usage

The workflow can be triggered manually from the Actions tab of the `ies-ontology-template` repository. You will need to provide:

- Repository name
- Repository description
- Public/Private status (defaults to private)

## Required Permissions

### Organization-level PAT Requirements

The `IES_ONTOLOGIES_PAT` (Personal Access Token) needs the following permissions:

- `repo` - Full control of private repositories
  - Needed for creating repositories and managing their settings
- `workflow` - Update GitHub Action workflows
  - Required for setting up repository variables
- `admin:org` - Full control of orgs and teams
  - Needed for creating and managing projects
- `project` - Full control of organization projects
  - Required for creating and configuring projects

### Workflow Permissions

The workflow itself requires:

```yaml
permissions:
  contents: write        # For creating repository content
  pull-requests: write   # For potential future PR creation features
```

## Maintenance Considerations

### Token Management

- Ensure the `IES_ONTOLOGIES_PAT` token expires, e.g. 366 days
- Regularly audit token permissions
- Have a process for token rotation

### Error Handling

The workflow includes error handling for:

- Project creation
- Variable setting
- Repository creation

Failed steps will output relevant information to the workflow logs for debugging.

### Template Updates

When updating the template repository:

- Test the workflow after significant changes
- Ensure new template features don't break the repository creation process
- Update workflow permissions if new features require additional access

## Troubleshooting

Common issues and their solutions:

1. Permission Errors

   - Verify PAT permissions
   - Check organization membership roles
   - Ensure the PAT hasn't expired

2. Variable Creation Failures

   - Check workflow logs for specific error messages
   - Verify repository settings allow variable creation
   - Ensure PAT has correct scope

3. Project Creation Issues

   - Verify organization project settings
   - Check project quota limits
   - Ensure project templates (if used) exist

## Standard Labels

The workflow automatically creates a standard set of labels in each new repository:

| Label              | Description                                | Color   |
|-------------------|--------------------------------------------|---------| 
| bug               | Something isn't working                    | #d73a4a |
| documentation     | General documentation tasks                | #0075ca |
| duplicate         | This issue or pull request already exists  | #cfd3d7 |
| enhancement       | New feature or request                     | #a2eeef |
| good first issue  | Good for newcomers                        | #7057ff |
| help wanted       | Extra attention is needed                  | #008672 |
| invalid           | This doesn't seem right                    | #e4e669 |
| question          | Further information is requested           | #d876e3 |
| wontfix           | This will not be worked on                 | #ffffff |
| priority-high     | Urgent issues                             | #b60205 |
| priority-medium   | Important but not urgent                  | #fbca04 |
| priority-low      | Nice to have                              | #0e8a16 |
| wip               | Work in progress                           | #1d76db |
| docs-new          | New documentation needed                   | #3A4520 |
| docs-update       | Updates to existing docs                   | #464444 |
| docs-fix          | Documentation fixes                        | #C90572 |
| tech-review-needed| Needs technical review                     | #48C5DA |
| ready-for-review  | Documentation ready for final review       | #F795DF |
| docs-clarity      | Improvements to documentation clarity      | #7B61B1 |
| has-issue         | PR linked to an issue                      | #0E8A16 |

These labels help maintain consistency across all repositories and facilitate issue management.

## Potential Future Enhancements

- Support for custom project templates
- Additional repository configuration options
- Automated team access setup
- Integration with other organization tooling

## Contributing

When modifying this workflow:

1. Test changes in a safe environment first
2. Document any new inputs or variables
3. Update error handling for new functionality
4. Keep this documentation in sync with changes

[github-actions]: https://docs.github.com/IES-Org/ieso-ontology-template/actions
