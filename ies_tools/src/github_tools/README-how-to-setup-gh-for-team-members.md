# GitHub Tools

A command-line tool for managing GitHub issues, project boards, and development workflows. This tool integrates with your GitHub repository to automate common development tasks.

## Development

- Create development issues and branches with standardized templates
- Automatically add issues to GitHub project boards
- Create and manage `qa/*`, `rc/*`, `dev/*`, `bugfix/*`, and `hotfix/*` branches
- Synchronize local and remote branches
- Create pull requests linked to issues

## Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- GitHub CLI (`gh`) installed and authenticated
- Git configured with your repository

### GitHub CLI Setup

1. Install the GitHub CLI:

   ```bash
   # macOS
   brew install gh

   # Windows
   winget install --id GitHub.cli

   # Linux
   type -p curl >/dev/null || apt install curl -y
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
   && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
   && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
   && apt update \
   && apt install gh -y
   ```

2. Configure Authentication:

```bash
# Log out of any existing auth
gh auth logout

# Login with browser
gh auth login
# Select "GitHub.com"
# Select "HTTPS"
# Select "Login with a web browser"

# Add required scopes
gh auth refresh --scopes "repo,project"

# Verify setup
gh auth status
```

## Organization Setup

### Admin Configuration

Organization administrators need to configure:

1. Organization Member Privileges (`Organization Settings -> Member privileges`):

   - Base permissions: `Write`
   - Allow repository creation
   - Enable repository discussions
   - Projects base permissions: `Write`

2. Project Access:

   - Set "Base Role" to `Write` for organization members
   - Ensure project visibility matches repository settings

### Repository Setup

1. Ensure the PROJECT_ID is set as a repository variable (this is done if the repository is created with the workflow [create-ontology-repo.yml][create-repo], or manually:

```bash
gh variable set PROJECT_ID --body "PVT_xxx..."
```

2. The required repository labels can be installed using the [setup-labels.yml][setup-labels] workflow:

```bash
poetry run gh-tools setup-labels
```

The standard labels can be viewed with:

```bash
gh label list
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository>

# Install dependencies
poetry install
```

## Usage

### Creating a Feature Request

```bash
# Interactive mode
poetry run gh-tools create-issue

# With direct arguments
poetry run gh-tools create-issue \
  --title "abc-def" \
  --type dev \
  --description "Development description" \
  --review "abc-def"
  --acceptance "Done when..." \
  --priority medium \
  --size m
```

This will:

1. Create a new issue with the `dev` prefix and associated issue number
2. Add it to the repo project board
3. Create `qa/abc-def` and `dev/abc-def`|`bugfix/abc-def`|`hotfix/abc-def`) branches
4. Push the branch to remote

### Syncing Branches

```bash
# Sync current branch
poetry run gh-tools sync

# Sync specific branch
poetry run gh-tools sync dev/abc-def

# Force sync (stashing local changes)
poetry run gh-tools sync --force
```

### Creating Pull Requests

```bash
# Create PR to `qa/*` branch
poetry run gh-tools create-pr

# Create as draft PR
poetry run gh-tools create-pr --draft

# Target different base branch
poetry run gh-tools create-pr --base "qa/x-y-z"
```

## Branch Strategy

The tool supports:
- `main` - Production branch
- `qa/*` - QA Review branch
- `rc/*` - Release candidate branch
- `dev/*` - Ontology enhancement branches
- `bugfix/*` - Non-urgent bug fixes
- `hotfix/*` - Production hotfix branches

## Troubleshooting

### Authentication Issues

If you see permission errors:

```bash
# Check status
gh auth status

# Refresh token
gh auth refresh --scopes "repo,project"

# Verify organization membership
gh org list
```

### Project Board Issues

If issues aren't being added:

1. Verify your PROJECT_ID:

```bash
gh variable list
```

2. Ensure:

- Organization membership is active
- Project's base role is set to `Write`
- You have `Write` repository access

3. Try refreshing with additional scopes:

```bash
gh auth refresh --scopes "repo,project,write:org"
```

### Branch Sync Issues

If branch sync fails:

1. Check for local changes:

```bash
git status
```

2. Use force sync if needed:

```bash
poetry run gh-tools sync --force
```

## Contributing

1. Create a issue branch:

```bash
poetry run gh-tools create-issue
```

2. Make your changes
3. Create a pull request:

```bash
poetry run gh-tools create-pr
```

## License

These scripts are licensed under the MIT License. See [LICENCE][LICENCE] for details.

[create-repo]: ../../../.github/workflows/create-ontology-repo.yml
[licence]: ../../../LICENSE
[setup-labels]: ../../../.github/workflows/setup-labels.yml
