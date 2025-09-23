# IES Sync Tools Workflow

This workflow automatically synchronizes GitHub workflows and IES tools from the template `ies-ontology-template` repository.

## Overview

The workflow:

1. Runs weekly every Sunday 0100 UTC
2. Can be manually triggered
3. Creates a PR when changes are detected
4. Preserves the sync workflow file itself in consuming repos

## Prerequisites

1. IES Ontology Template repository (`ies-ontology-template`) containing the master `.github/` configuration
2. Organization-level secret configured with a Personal Access Token (PAT) with the following permissions on both repositories:

- `contents:write`
- `workflows:write`

## Setup

1. Create an Organization PAT:

- Go to your GitHub Organization Settings → Personal access tokens → Settings → Fine-grained tokens
- Create new token with:
   
  - Repository access: Selected repositories (`ies-github-workflows` and consuming repos)
  - Repository permissions:
     
    - Contents: Write
    - Workflows: Write

2. There's no need to add the Organization PAT as it is visible to all repositories in the Organization.

3. The `sync-tools.yml` workflow is scheduled to execute weekly every Sunday 0100 UTC in any repository created from `ies-ontology-template`, or it can be run manually.

## How It Works

1. Checks `ies-ontology-template` repository for contents as specified in the `sync-config.yml` file.
2. Downloads all files and directories to compare with the content in the domain ontology repository.
3. If changes are detected, it:
   - Creates new branch
   - Updates files in the domain ontology repository
   - Creates a PR with detailed changes
   - PR requires review and approval before merging changes into `main`

## Special Handling

- Changes to workflow files require special permissions (hence the PAT requirement)
- The sync process is atomic - all changes are made in a single PR

## Debugging

The workflow includes debug steps that show:

- API access status
- Repository contents
- File change detection
- PR creation process

Check the workflow run logs for detailed information about each step.

## Manual Trigger

To manually trigger the sync:

1. Go to the Actions tab in your repository
2. Select "Sync IES Tools"
3. Click "Run workflow"
4. Select branch (usually 'main')
5. Click "Run workflow"

## Troubleshooting

1. Permission errors:

   - Verify PAT has correct permissions
   - Ensure PAT is added as `IES_ONTOLOGIES_PAT`
   - Check PAT hasn't expired

2. 404 errors:

   - Verify repository paths
   - Check repository access permissions
   - Ensure specified content (e.g. `.github/`, `ies_tools/`) exists in `ies-ontology-template` repository.

3. Push/PR failures:

   - Ensure branch protection rules allow GitHub Actions
   - Verify PR creation permissions
