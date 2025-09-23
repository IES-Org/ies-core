import os
import sys
import platform
import json
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, List

import click


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class IssueType(str, Enum):
    DEV = "dev"
    BUGFIX = "bugfix"
    HOTFIX = "hotfix"

class PRType(str, Enum):
    DEV = "dev"      # dev/* or bugfix/* -> qa/*
    QA = "qa"        # qa/* -> rc/vX.Y
    RC = "rc"        # rc/vX.Y -> main
    HOTFIX = "hotfix"  # hotfix/* -> main

@dataclass
class IssueMetadata:
    number: str
    title: str
    issue_type: IssueType
    branch_name: str


def verify_gh_cli():
    """Verify GitHub CLI is available and authenticated"""
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise click.ClickException(
            "GitHub CLI (gh) not found. Please install it first."
        )

    try:
        subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        raise click.ClickException(
            "Not authenticated with GitHub. Please run 'gh auth login' first."
        )


def verify_git_clean():
    """
    Verify git working directory is clean and provide detailed status about any changes.
    Uses git status porcelain v2 format for detailed information.
    """
    # Get status in porcelain v2 format for detailed info
    result = subprocess.run(
        ["git", "status", "--porcelain=v2"],
        capture_output=True,
        text=True,
        check=True,
    )

    if not result.stdout.strip():
        return  # Working directory is clean

    # Initialize counters
    untracked = []
    unstaged = []
    staged = []

    # Parse the porcelain v2 output
    for line in result.stdout.splitlines():
        if line.startswith('?'):  # Untracked files
            untracked.append(line[2:].strip())
        elif line.startswith('1') or line.startswith('2'):  # Changed or renamed files
            entry = line.split()
            status = entry[1]  # Status is the second field
            path = entry[-1]  # Path is the last field

            # Check staged and unstaged changes
            staged_status = status[0]
            unstaged_status = status[1]

            if staged_status != '.':
                staged.append(path)
            if unstaged_status != '.':
                unstaged.append(path)

    # Build the status message
    status_msg = []
    if untracked:
        status_msg.append(f"Untracked files ({len(untracked)}):")
        for file in untracked:
            status_msg.append(f"  • {file}")

    if unstaged:
        if status_msg:
            status_msg.append("")
        status_msg.append(f"Unstaged changes ({len(unstaged)}):")
        for file in unstaged:
            status_msg.append(f"  • {file}")

    if staged:
        if status_msg:
            status_msg.append("")
        status_msg.append(f"Staged changes ({len(staged)}):")
        for file in staged:
            status_msg.append(f"  • {file}")

    # Print the status message
    click.echo("\nWorking directory has uncommitted changes:")
    click.echo("\n".join(status_msg))

    # Ask for confirmation
    if not click.confirm(
            "\nDo you want to continue anyway?",
            default=False,
    ):
        raise click.Abort()


def get_default_branch() -> str:
    """Get the default branch (usually 'main')"""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "defaultBranchRef"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        return data["defaultBranchRef"]["name"]
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError):
        # ToDo this may not be safe
        return "main"  # Fallback to main if default branch not found


def get_default_target_branch(current_branch: str) -> str:
    """
    Determine the default target branch based on the current branch name.
    For dev/*, bugfix/*, and qa/* branches, use the same suffix for the target branch.
    For hotfix/*, always target main.

    Args:
        current_branch (str): Current branch name (e.g. 'dev/new-feat-1' or 'qa/new-feat')
    Returns:
        str: Default target branch name (e.g. 'qa/new-feat' or 'rc/vX.Y')
    Raises:
        click.ClickException: If the branch name pattern is invalid
    """
    # Extract branch type and suffix from current branch
    match = re.match(r"(dev|develop|bugfix|hotfix|qa-ready|qa|rc-ready|rc)/(.*)", current_branch)
    if not match:
        return ""  # No default if pattern doesn't match

    branch_type = match.group(1)
    full_suffix = match.group(2)

    # Strip issue number from suffix if present
    suffix_match = re.match(r"(.*?)-?\d*$", full_suffix)
    if not suffix_match:
        return ""  # Invalid suffix pattern

    suffix = suffix_match.group(1)

    # Handle legacy branch names
    if branch_type == "develop":
        branch_type = "dev"
    elif branch_type == "qa-ready":
        branch_type = "qa"
    elif branch_type == "rc-ready":
        branch_type = "rc"

    # Define target branch type based on source branch type
    if branch_type == "hotfix":
        return "main"
    elif branch_type in ["dev", "bugfix"]:
        return f"qa/{suffix}"
    elif branch_type == "qa":
        # For qa branches, we need to determine which rc/vX.Y to target
        # This would need additional logic or user input to determine the version
        return ""  # Return empty to force user to specify

    return ""


def get_repo_owner() -> str:
    """Get repository owner from git remote"""
    try:
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True
        ).strip()
        # Handle both HTTPS and SSH URLs
        if "github.com:" in remote_url:  # SSH
            owner = remote_url.split("github.com:")[1].split("/")[0]
        else:  # HTTPS
            owner = remote_url.split("github.com/")[1].split("/")[0]
        return owner
    except (subprocess.CalledProcessError, IndexError):
        raise click.ClickException("Could not determine repository owner")


def get_repo_name() -> str:
    """Get repository name from git remote"""
    try:
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True
        ).strip()
        # Handle both HTTPS and SSH URLs
        name = remote_url.split("/")[-1].replace(".git", "")
        return name
    except (subprocess.CalledProcessError, IndexError):
        raise click.ClickException("Could not determine repository name")


def get_current_repo_info():
    """Get the current repository name and organization from git remote URL.

    Returns:
        tuple: (org_name, repo_name) or (None, None) if not in a git repo
    """
    try:
        # Get the remote URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()

        # Parse GitHub URL to get org and repo
        # Handles both HTTPS and SSH URLs:
        # https://github.com/org/repo.git
        # git@github.com:org/repo.git
        if 'github.com' not in remote_url:
            return None, None

        if remote_url.startswith('git@'):
            path = remote_url.split('github.com:')[1]
        else:
            path = remote_url.split('github.com/')[1]

        # Remove .git suffix if present and split into org/repo
        path = path.replace('.git', '')
        org, repo = path.split('/')
        return org, repo
    except subprocess.CalledProcessError:
        return None, None
    except Exception:
        return None, None


def get_project_id() -> Optional[str]:
    """Get project ID from repository variables"""
    try:
        result = subprocess.run(
            ["gh", "variable", "list", "--json", "name,value"],
            capture_output=True,
            text=True,
            check=True,
        )
        variables = json.loads(result.stdout)
        for var in variables:
            if var["name"] == "PROJECT_ID":
                return var["value"]
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def setup_submodules() -> bool:
    """Initialize and update required git submodules"""
    try:
        # Skip if we are in the ies-common or ies-ontology-template repository
        repo_name = get_repo_name()
        if repo_name == "ies-common" or repo_name == "ies-ontology-template":
            click.echo(f"ℹ️  Skipping submodule setup in {repo_name} repository")
            return True

        common_repo = "https://github.com/IES-Org/ies-common.git"
        submodule_path = "common"

        click.echo("🔍 Checking submodules...")

        # Check if submodule already exists
        if not os.path.exists(os.path.join(submodule_path, ".git")):
            click.echo("🔗 Adding common submodule...")
            subprocess.run(
                ["git", "submodule", "add", common_repo, submodule_path],
                check=True,
                capture_output=True,
            )

        # Update the submodule
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            check=True,
            capture_output=True,
        )

        click.echo("✨ Submodules setup completed")
        return True

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to setup submodules: {e.stderr}", err=True)
        return False


def create_github_branch_rules(repo, org, dry_run):
    """Create branch protection rules for a repository"""

    try:
        # Verify GitHub CLI authentication
        verify_gh_cli()

        # Check if repository exists and is accessible
        click.echo("🔍 Checking repository access...")
        result = subprocess.run(
            ["gh", "repo", "view", f"{org}/{repo}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise click.ClickException(f"Repository '{org}/{repo}' not found or not accessible")

        # Get existing branch protection rules
        click.echo("🔍 Checking existing branch protection rules...")
        result = subprocess.run(
            ["gh", "api", f"/repos/{org}/{repo}/branches/main/protection"],
            capture_output=True,
            text=True
        )
        has_existing_rules = result.returncode == 0

        if has_existing_rules and not dry_run:
            if not click.confirm("Branch protection rules already exist. Do you want to proceed and overwrite them?"):
                raise click.Abort()

        if dry_run:
            click.echo("\nDRY RUN - Would create the following branch protection rules:")
            click.echo("\nMain branch protection:")
            click.echo("  - No direct pushes")
            click.echo("  - Requires PR from rc/vX.Y or hotfix/* branches")
            click.echo("  - Required reviewers: IES Ontology Managers")

            click.echo("\nRelease Candidate (rc/v*) branch protection:")
            click.echo("  - No direct pushes")
            click.echo("  - Requires PR from qa/* branches")
            click.echo("  - Required reviewers: IES TGG")

            click.echo("\nQA (qa/*) branch protection:")
            click.echo("  - No direct pushes")
            click.echo("  - Requires PR from dev/* or bugfix/* branches")
            click.echo("  - Required reviewers: IES Ontology QA")

            click.echo("\nHotfix (hotfix/*) branch protection:")
            click.echo("  - Direct pushes allowed by IES Ontology Developers")
            click.echo("  - Can only target main branch")
            return

        # Setup branch protection rules using GitHub API
        click.echo("\n🔧 Setting up branch protection rules...")

        # Main branch protection
        click.echo("📝 Configuring main branch protection...")
        main_protection = {
            "name": "Main Branch Protection",
            "target": "branch",
            "enforcement": "active",
            "conditions": {
                "ref_name": {
                    "include": ["refs/heads/main"],
                    "exclude": []
                },
                "repository_name": {
                    "exclude": ["ies-building"]
                }
            },
            "rules": [
                {
                    "type": "required_pull_request_reviews",
                    "parameters": {
                        "dismiss_stale_reviews": True,
                        "require_code_owner_reviews": False,
                        "required_approving_review_count": 1
                    }
                }
            ],
            "bypass_actors": []
        }

        subprocess.run([
            "gh", "api",
            "/orgs/IES-Org/rulesets",
            "--method", "POST",
            "--input", "-",
            "--header", "Accept: application/vnd.github+json",
            "--header", "X-GitHub-Api-Version: 2022-11-28"
        ], input=json.dumps(main_protection), text=True, check=True)

        # RC branch pattern protection (updated for new pattern)
        click.echo("📝 Configuring RC branch pattern protection...")
        rc_protection = {
            "name": "RC Branch Protection",
            "target": "branch",
            "enforcement": "active",
            "conditions": {
                "ref_name": {
                    "include": ["refs/heads/rc/v*"],
                    "exclude": []
                },
                "repository_name": {
                    "exclude": ["ies-building"]
                }
            },
            "rules": [
                {
                    "type": "required_pull_request_reviews",
                    "parameters": {
                        "dismiss_stale_reviews": True,
                        "require_code_owner_reviews": False,
                        "required_approving_review_count": 1
                    }
                }
            ],
            "bypass_actors": []
        }

        subprocess.run([
            "gh", "api",
            "/orgs/IES-Org/rulesets",
            "--method", "POST",
            "--input", "-",
            "--header", "Accept: application/vnd.github+json",
            "--header", "X-GitHub-Api-Version: 2022-11-28"
        ], input=json.dumps(rc_protection), text=True, check=True)

        # QA branch pattern protection
        click.echo("📝 Configuring QA branch pattern protection...")
        qa_protection = {
            "name": "QA Branch Protection",
            "target": "branch",
            "enforcement": "active",
            "conditions": {
                "ref_name": {
                    "include": ["refs/heads/qa/*"],
                    "exclude": []
                },
                "repository_name": {
                    "exclude": ["ies-building"]
                }
            },
            "rules": [
                {
                    "type": "required_pull_request_reviews",
                    "parameters": {
                        "dismiss_stale_reviews": True,
                        "require_code_owner_reviews": False,
                        "required_approving_review_count": 1
                    }
                }
            ],
            "bypass_actors": []
        }

        subprocess.run([
            "gh", "api",
            "/orgs/IES-Org/rulesets",
            "--method", "POST",
            "--input", "-",
            "--header", "Accept: application/vnd.github+json",
            "--header", "X-GitHub-Api-Version: 2022-11-28"
        ], input=json.dumps(qa_protection), text=True, check=True)

        # Hotfix branch pattern protection
        click.echo("📝 Configuring Hotfix branch pattern protection...")
        hotfix_protection = {
            "name": "Hotfix Branch Protection",
            "target": "branch",
            "enforcement": "active",
            "conditions": {
                "ref_name": {
                    "include": ["refs/heads/hotfix/*"],
                    "exclude": []
                },
                "repository_name": {
                    "exclude": ["ies-building"]
                }
            },
            "rules": [
                {
                    "type": "required_pull_request_reviews",
                    "parameters": {
                        "dismiss_stale_reviews": True,
                        "require_code_owner_reviews": False,
                        "required_approving_review_count": 1
                    }
                }
            ],
            "bypass_actors": [
                {
                    "actor_id": "IES Ontology Developers",
                    "actor_type": "Team",
                    "bypass_mode": "always"
                }
            ]
        }

        subprocess.run([
            "gh", "api",
            "/orgs/IES-Org/rulesets",
            "--method", "POST",
            "--input", "-",
            "--header", "Accept: application/vnd.github+json",
            "--header", "X-GitHub-Api-Version: 2022-11-28"
        ], input=json.dumps(hotfix_protection), text=True, check=True)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise click.ClickException(f"Failed to create branch protection rules: {error_msg}")
    except click.Abort:
        click.echo("Operation cancelled")
        sys.exit(1)
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


def setup_required_branches(title: str) -> Tuple[str, str]:
    """
    Create and push qa/* branches if they don't exist
    Note: RC branches are now created on-demand during PR creation

    Args:
        title (str): Title of the issue
    Returns:
        str: Name of the created qa branch
    """
    try:
        # Get default branch (usually main)
        default_branch = get_default_branch()

        # Get list of existing branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            check=True,
        )
        existing_branches = result.stdout.strip().split('\n')
        existing_branches = [b.strip('* ').strip() for b in existing_branches]

        # Extract issue number if present in title
        # Modified regex to only remove trailing issue number, preserving all other hyphens
        title_parts = re.match(r"(.*?)(?:-\d+)?$", title)
        if title_parts:
            clean_title = title_parts.group(1)
        else:
            clean_title = title

        # Create qa branch name from clean title
        safe_title = re.sub(r"[^a-zA-Z0-9]", "-", clean_title.lower())
        qa_branch = f"qa/{safe_title}"

        def create_branch_if_missing(branch_name: str, existing_branches: list[str], base_branch: str) -> None:
            if not any(b.endswith(branch_name) for b in existing_branches):
                click.echo(f"🌱 Creating {branch_name} branch...")
                subprocess.run(
                    ["git", "checkout", f"origin/{base_branch}"],
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    check=True,
                    capture_output=True,
                )
                click.echo(f"⬆️  Pushing {branch_name} branch to remote...")
                subprocess.run(
                    ["git", "push", "-u", "origin", branch_name],
                    check=True,
                    capture_output=True,
                )
            else:
                click.echo(f"ℹ️  Branch {branch_name} already exists")

        # Setup qa branch only
        create_branch_if_missing(qa_branch, existing_branches, default_branch)
        click.echo("✨ Branch setup completed")
        return qa_branch

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to setup branches: {e.stderr}", err=True)
        raise click.ClickException("Failed to setup required branches")


def setup_rc_branch(version: str) -> str:
    """
    Create and push rc/vX.Y branch if it doesn't exist.

    Args:
        version (str): Version number in format vX.Y (e.g. v5.1)
    Returns:
        str: Name of the created rc branch
    """
    try:
        # Validate version format (now expects vX.Y instead of vX.Y.Z)
        if not re.match(r"^v\d+\.\d+$", version):
            raise click.ClickException(
                "Version must follow format vX.Y (e.g. v5.1)"
            )

        rc_branch = f"rc/{version}"

        # Check if branch exists
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            check=True,
        )
        existing_branches = result.stdout.strip().split('\n')
        existing_branches = [b.strip('* ').strip() for b in existing_branches]

        if not any(b.endswith(rc_branch) for b in existing_branches):
            click.echo(f"🌱 Creating {rc_branch} branch...")
            # Create from main
            subprocess.run(
                ["git", "checkout", "origin/main"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "checkout", "-b", rc_branch],
                check=True,
                capture_output=True,
            )
            click.echo(f"⬆️  Pushing {rc_branch} branch to remote...")
            subprocess.run(
                ["git", "push", "-u", "origin", rc_branch],
                check=True,
                capture_output=True,
            )
        else:
            click.echo(f"ℹ️  Branch {rc_branch} already exists")

        return rc_branch

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to setup RC branch: {e.stderr}", err=True)
        raise click.ClickException("Failed to setup RC branch")


def setup_implementation_branch(issue_number: str, title: str, issue_type: IssueType, qa_ready_branch: str) -> str:
    """Create and switch to a new implementation branch"""
    try:
        # Generate branch name
        safe_title = re.sub(r"[^a-zA-Z0-9]", "-", title.lower())
        branch_name = f"{issue_type.value}/{safe_title}-{issue_number}"

        # Create branch from issue using GitHub CLI
        subprocess.run(
            [
                "gh", "issue", "develop",
                issue_number,
                "--base", qa_ready_branch,
                "--name", branch_name,
                "--checkout"
            ],
            check=True,
            capture_output=True,
        )

        return branch_name

    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating branch: {e.stderr}", err=True)
        raise click.ClickException("Failed to create implementation branch")


def setup_labels() -> bool:
    """Run the labels setup workflow"""
    try:
        workflow_path = ".github/workflows/setup-labels.yml"

        # Check if workflow file exists
        if not os.path.exists(workflow_path):
            click.echo(f"❌ Workflow file not found: {workflow_path}", err=True)
            return False

        click.echo("🏷️  Running labels setup workflow...")
        subprocess.run(
            ["gh", "workflow", "run", "setup-labels.yml"],
            check=True,
            capture_output=True,
        )
        click.echo("✨ Labels setup workflow triggered successfully")
        return True

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to run labels workflow: {e.stderr}", err=True)
        return False


def get_platform_type() -> str:
    """Determine the platform type more accurately"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed"""
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
        click.echo("✓ GitHub CLI is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("❌ GitHub CLI (gh) is not installed", err=True)

        # Provide installation instructions based on platform
        platform_type = get_platform_type()
        if platform_type == "macos":
            click.echo("To install on macOS:")
            click.echo("  brew install gh")
        elif platform_type == "linux":
            click.echo("To install on Linux:")
            click.echo(
                "  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg")
            click.echo(
                "  echo \"deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list")
            click.echo("  sudo apt update")
            click.echo("  sudo apt install gh")
        elif platform_type == "windows":
            click.echo("To install on Windows:")
            click.echo("  winget install GitHub.cli")
            click.echo("  # or")
            click.echo("  choco install gh")
        return False


def validate_branch_safe_title(title: str) -> bool:
    """
    Validate that a title will result in a valid git branch name.
    Raises ClickException if invalid.
    """
    safe_title = re.sub(r"[^a-zA-Z0-9]", "-", title.lower())

    # Updated pattern to use new "dev" prefix
    test_branch = f"dev/{safe_title}-123"  # Using dummy issue number
    pattern = r"^(?!.*\.\.)(dev|bugfix)/(?![-./])[-a-zA-Z0-9]+(?:[-a-zA-Z0-9]+)*-(\d+)(?<!\.lock)$"

    if not re.match(pattern, test_branch):
        raise click.ClickException(
            "Issue title would result in invalid branch name. "
            "Title must only contain letters, numbers, and spaces. "
            "When converted to a branch name, it must not: "
            "start with '.', '-', or '/', "
            "contain '..', or "
            "end in '.lock'"
        )
    return True


def validate_pr_target(source_branch: str, target_branch: str) -> bool:
    """
    Validate if the PR can target the specified branch based on branch naming rules.

    Args:
        source_branch (str): Source branch name
        target_branch (str): Target branch name
    Returns:
        bool: True if the PR can target the branch
    Raises:
        click.ClickException: If the PR cannot target the branch
    """
    # Extract branch types from names
    source_type = re.match(r"^(dev|bugfix|hotfix|qa-ready|qa|rc-ready|rc)/", source_branch)
    # Updated pattern to match new rc/vX.Y format
    target_type = re.match(r"^(qa-ready|qa|rc-ready|rc)/([^/]+)$|^main$", target_branch)

    if not source_type or not target_type:
        raise click.ClickException("Invalid branch naming pattern")

    source_prefix = source_type.group(1)
    target_prefix = target_type.group(1) if target_branch != "main" else "main"

    # Handle legacy branch names
    if source_prefix == "qa-ready":
        source_prefix = "qa"
    elif source_prefix == "rc-ready":
        source_prefix = "rc"

    # Define valid transitions
    valid_transitions = {
        "dev": ["qa"],
        "bugfix": ["qa"],
        "qa": ["rc"],
        "hotfix": ["main"]
    }

    # Check if transition is valid
    if source_prefix not in valid_transitions or target_prefix not in valid_transitions.get(source_prefix, []):
        raise click.ClickException(
            f"Invalid branch transition: {source_prefix} -> {target_prefix}\n"
            f"Valid transitions are:\n"
            f"- dev/* or bugfix/* -> qa/*\n"
            f"- qa/* -> rc/vX.Y\n"
            f"- hotfix/* -> main"
        )

    return True


def create_github_issue(
        title: str, body: str, labels: List[str], issue_type: IssueType
) -> IssueMetadata:
    """
    Create an issue and return its metadata

    Args:
        title (str): Issue title
        body (str): Issue body
        labels (List[str]): List of labels to add to the issue
        issue_type (IssueType): Type of issue being created

    Returns:
        IssueMetadata: Metadata for the created issue
    """
    # Validate title will result in valid branch name
    validate_branch_safe_title(title)

    try:
        # Construct the gh issue create command
        cmd = [
            "gh",
            "issue",
            "create",
            "--title",
            f"{title}",  # Removed the [Development]/[Bugfix]/[Hotfix] prefix
            "--body",
            body
        ]

        # Add labels
        for label in labels:
            cmd.extend(["-l", label])

        # Execute the command with output capture
        click.echo("Creating issue...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract issue number from the URL in the output
        issue_url = result.stdout.strip()
        issue_number = issue_url.split('/')[-1]

        # Get the Project ID and add to project board
        project_id = get_project_id()

        if project_id:
            try:
                # Get issue node ID using REST API
                click.echo("🔍 Getting issue ID...")
                issue_query = subprocess.run(
                    ["gh", "api", f"/repos/{get_repo_owner()}/{get_repo_name()}/issues/{issue_number}"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                issue_data = json.loads(issue_query.stdout)
                issue_id = issue_data["node_id"]  # GitHub's node ID for GraphQL

                # Add to project
                click.echo("📌 Adding to project board...")
                project_mutation_cmd = [
                    "gh", "api", "graphql",
                    "--raw-field",
                    f'query=mutation($projectId: ID!, $contentId: ID!) {{ addProjectV2ItemById(input: {{ projectId: $projectId, contentId: $contentId }}) {{ item {{ id }} }} }}',
                    "--raw-field", f'projectId={project_id}',
                    "--raw-field", f'contentId={issue_id}'
                ]

                project_mutation = subprocess.run(
                    project_mutation_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                if project_mutation.returncode == 0:
                    click.echo("✨ Added issue to project board")

            except subprocess.CalledProcessError as e:
                click.echo(f"Warning: Failed to add issue to project: {e.stderr}")
                # Continue since issue was created successfully
        else:
            click.echo("⚠️  Warning: PROJECT_ID not found. Issue won't be added to project board.")

        # Generate branch name
        safe_title = re.sub(r"[^a-zA-Z0-9]", "-", title.lower())
        branch_name = f"{issue_type.value}/{safe_title}-{issue_number}"

        return IssueMetadata(
            number=issue_number,
            title=title,
            issue_type=issue_type,
            branch_name=branch_name,
        )

    except subprocess.CalledProcessError as e:
        click.echo("Error creating issue. GitHub CLI output:", err=True)
        if e.stdout:
            click.echo(f"stdout: {e.stdout}", err=True)
        if e.stderr:
            click.echo(f"stderr: {e.stderr}", err=True)

        if "could not create issue" in str(e.stderr):
            click.echo(
                "Please check that you're authenticated with 'gh auth status'"
            )
        # Add more specific error handling
        elif "Validation Failed" in str(e.stderr):
            click.echo("GitHub validation failed. Check if all required labels exist.")
        elif "Not Found" in str(e.stderr):
            click.echo("Repository not found or you don't have access.")
        raise click.ClickException(f"Failed to create issue: {e.stderr}")


def check_branch_status() -> Tuple[bool, bool, bool]:
    """Check branch status returning (has_local_changes, has_unpushed, has_unmerged)"""
    # Check for local changes
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    has_local_changes = bool(status.stdout.strip())

    # Check for unpushed commits
    unpushed = subprocess.run(
        ["git", "log", "@{u}..HEAD", "--oneline"],
        capture_output=True,
        text=True,
        check=True,
    )
    has_unpushed = bool(unpushed.stdout.strip())

    # Check for unmerged changes
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        check=True,
    )
    has_unmerged = bool(unmerged.stdout.strip())

    return has_local_changes, has_unpushed, has_unmerged


def sync_remote_branch(branch_name: str, force: bool = False):
    """Sync local branch with remote"""
    try:
        # Fetch the latest from remote
        click.echo("📡 Fetching remote changes...")
        subprocess.run(
            ["git", "fetch", "origin"], check=True, capture_output=True
        )

        # Check if branch exists remotely
        remote_exists = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", branch_name],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        if not remote_exists:
            raise click.ClickException(f"Branch {branch_name} does not exist on remote")

        # Check branch status
        has_local_changes, has_unpushed, has_unmerged = check_branch_status()

        # Handle local changes
        if has_local_changes:
            if force:
                click.echo("⚠️ Stashing local changes...")
                subprocess.run(["git", "stash"], check=True)
            else:
                raise click.ClickException(
                    "You have local changes. Commit, stash, or use --force to proceed"
                )

        # Handle unpushed commits
        if has_unpushed:
            if force:
                click.echo("⚠️ Resetting to remote branch...")
                subprocess.run(
                    ["git", "reset", "--hard", f"origin/{branch_name}"],
                    check=True
                )
            else:
                raise click.ClickException(
                    "You have unpushed commits. Push them or use --force to proceed"
                )

        # Handle unmerged changes
        if has_unmerged:
            raise click.ClickException(
                "You have unmerged changes. Resolve conflicts first"
            )

        # Create/update local branch tracking remote
        click.echo("🔄 Updating local branch...")
        subprocess.run(
            ["git", "checkout", "-B", branch_name, f"origin/{branch_name}"],
            check=True,
            capture_output=True,
        )

        # Pop stashed changes if we stashed them
        if force and has_local_changes:
            click.echo("📝 Reapplying local changes...")
            subprocess.run(["git", "stash", "pop"], check=True)

        click.echo("✨ Branch synchronized successfully")

    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Failed to sync branch: {e}")


@click.group()
def cli():
    """CLI for managing GitHub issues and workflows"""
    pass


@cli.command()
def setup_repo():
    """Set up repository with develop branch and required tools"""
    success_count = 0
    total_steps = 2  # Minimum required steps

    click.echo("🔧 Setting up repository...")

    # Check for gh CLI installation
    check_gh_cli()

    # Verify GitHub CLI authentication
    try:
        verify_gh_cli()
        click.echo("✓ GitHub CLI authenticated")
    except click.ClickException as e:
        click.echo(f"❌ {str(e)}", err=True)
        return

    # Setup submodules
    if setup_submodules():
        success_count += 1

    # Setup labels
    if setup_labels():
        success_count += 1

    # Final status report
    if success_count == total_steps:
        click.echo("🎉 Repository setup completed successfully!")
    else:
        click.echo(f"⚠️  Repository setup completed with {total_steps - success_count} failures")
        click.echo("Please check the logs above and fix any issues manually")


@cli.command()
@click.option('--repo', help='Repository name (defaults to current repo)')
@click.option('--org', help='GitHub organization name (defaults to current repo org)')
@click.option('--dry-run', is_flag=True, help='Print actions without executing them')
def create_branch_rules(repo, org, dry_run):
    """Create branch protection rules for a repository"""
    # Get defaults from current git repo if not specified
    default_org, default_repo = get_current_repo_info()

    if not org and not default_org:
        raise click.ClickException("No organization specified and not in a GitHub repository")
    if not repo and not default_repo:
        raise click.ClickException("No repository specified and not in a GitHub repository")

    org = org or default_org
    repo = repo or default_repo

    try:
        click.echo(f"Creating branch protection rules for {org}/{repo}")
        create_github_branch_rules(repo, org, dry_run)

    except click.ClickException as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option(
    "--issue_type",
    "-t",
    type=click.Choice([t.value for t in IssueType], case_sensitive=False),
    prompt="Issue type",
    help="Type of issue to create",
)
@click.option(
    "--title",
    prompt="Issue title",
    help="Title of the issue"
)
@click.option(
    "--qa_branch",
    prompt="QA branch name (leave empty to use issue title)",
    default="",
    help="Name for the qa/* branch (without qa/ prefix)",
)
@click.option(
    "--description",
    "-d",
    prompt="Issue description",
    help="Detailed description of the issue",
)
@click.option(
    "--acceptance",
    "-a",
    prompt="Acceptance criteria",
    help="What needs to be true for this issue to be complete",
)
@click.option(
    "--priority",
    "-p",
    type=click.Choice([p.value for p in PriorityLevel], case_sensitive=False),
    prompt="Priority level",
    help="Priority level of the issue",
)
@click.option(
    "--size",
    "-s",
    type=click.Choice(["xs", "s", "m", "l", "xl"], case_sensitive=False),
    prompt="Size estimate",
    help="Estimated size of the issue",
)
def create_issue(
        issue_type: str,
        title: str,
        qa_branch: str,
        description: str,
        acceptance: str,
        priority: str,
        size: str,
):
    """Create a new issue and set up implementation branch"""
    issue_type_enum = IssueType(issue_type)
    verify_gh_cli()
    verify_git_clean()

    # Create implementation section based on issue type
    if issue_type_enum == IssueType.HOTFIX:
        implementation_text = """## Implementation
🔄 Implementation branch will be created and linked to the issue.
🔄 PRs should target `main` branch."""
    else:
        # Determine qa branch name
        if qa_branch:
            # Clean up provided qa branch name
            qa_branch_name = re.sub(r"[^a-zA-Z0-9-]", "-", qa_branch.lower())
        else:
            # Extract issue name from title for qa branch
            safe_title = re.sub(r"[^a-zA-Z0-9]", "-", title.lower())
            # Partition `safe_title` to get the part before the last hyphen
            partitions = safe_title.rpartition('-')
            if not partitions[0]:
                raise click.ClickException("Could not extract issue name from title")
            qa_branch_name = f"qa/{partitions[0]}"

        implementation_text = f"""## Implementation
🔄 Implementation branch will be created and linked to the issue.
🔄 PRs should target `qa/{qa_branch_name}` branch."""

    body = f"""## Description
{description}

## Acceptance Criteria
{acceptance}

## Type
{'Development' if issue_type_enum == IssueType.DEV else 'Bugfix' if issue_type_enum == IssueType.BUGFIX else 'Hotfix'}

## Priority
{priority}

## Size
{size}

{implementation_text}"""

    try:
        # Create issue
        metadata = create_github_issue(
            title=title,
            body=body,
            labels=[
                "enhancement" if issue_type_enum == IssueType.DEV else "bug" if issue_type_enum == IssueType.BUGFIX else "hotfix",
                f"priority:{priority}",
                f"size:{size}",
            ],
            issue_type=issue_type_enum,
        )
        click.echo(
            f"✨ {issue_type_enum.value.title()} issue '{title}' created as issue #{metadata.number}"
        )

        if issue_type_enum == IssueType.HOTFIX:
            # Create and switch to hotfix branch from main
            branch_name = setup_implementation_branch(
                qa_ready_branch="main",  # Use main as base for hotfixes
                issue_number=metadata.number,
                title=title,
                issue_type=issue_type_enum,
            )
        else:
            # Use qa_branch_name instead of extracting from title again
            qa_branch = setup_required_branches(qa_branch_name if qa_branch else title)

            # Create and switch to the implementation branch from the qa branch
            branch_name = setup_implementation_branch(
                qa_ready_branch=qa_branch,
                issue_number=metadata.number,
                title=title,
                issue_type=issue_type_enum,
            )

        click.echo(f"🌿 Created and switched to branch '{branch_name}'")

    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option(
    "--pr_type",
    "-t",
    type=click.Choice([t.value for t in PRType], case_sensitive=False),
    prompt="PR type",
    help="Type of PR to create (dev, qa, rc, or hotfix)",
)
@click.option(
    "--base",
    "-b",
    help="Target branch (qa/*, rc/vX.Y, or main)",
)
@click.option(
    "--head",
    "-h",
    help="Source branch (e.g., dev/feat-x-1). Defaults to current branch",
)
@click.option("--draft/--no-draft", default=False, help="Create as draft PR")
def create_pr(pr_type: str, base: str, head: str, draft: bool = False):
    """Create a pull request for the specified head branch"""
    verify_gh_cli()

    try:
        # Get head branch - either specified or current branch
        if head:
            source_branch = head
            # Verify the branch exists
            try:
                subprocess.run(
                    ["git", "rev-parse", "--verify", f"origin/{head}"],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                raise click.ClickException(f"Head branch '{head}' does not exist")
        else:
            source_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
            ).strip()

        # Extract branch type and issue number from head branch
        match = re.match(r"(dev|develop|bugfix|hotfix|qa|rc)/(?:v(\d+\.\d+)|([^/]+?)(?:-(\d+))?$)", source_branch)
        if not match:
            raise click.ClickException(
                f"Head branch '{source_branch}' doesn't follow the naming convention"
            )

        branch_type = match.group(1)
        version_number = match.group(2)  # For rc/vX.Y branches
        branch_suffix = match.group(3)   # For other branches
        issue_number = match.group(4)    # May be None

        # Handle legacy branch names
        if branch_type == "develop":
            branch_type = "dev"

        # Validate PR type matches branch type
        pr_type_enum = PRType(pr_type)
        if pr_type_enum == PRType.DEV and branch_type not in ["dev", "bugfix"]:
            raise click.ClickException("Dev PRs must come from dev/* or bugfix/* branches")
        elif pr_type_enum == PRType.QA and branch_type != "qa":
            raise click.ClickException("QA PRs must come from qa/* branches")
        elif pr_type_enum == PRType.RC and branch_type != "rc":
            raise click.ClickException("RC PRs must come from rc/vX.Y branches")
        elif pr_type_enum == PRType.HOTFIX and branch_type != "hotfix":
            raise click.ClickException("Hotfix PRs must come from hotfix/* branches")

        # Determine target branch if not specified
        if not base:
            if pr_type_enum == PRType.DEV:
                # Extract feature name from head branch (everything after dev/bugfix/ up to the last hyphen)
                feature_match = re.match(r"(?:dev|bugfix)/(.+?)(?:-\d+)?$", source_branch)
                if not feature_match:
                    raise click.ClickException("Could not extract feature name from branch")
                feature_name = feature_match.group(1)
                base = f"qa/{feature_name}"
            elif pr_type_enum == PRType.QA:
                raise click.ClickException(
                    "QA PRs require target RC branch (--base rc/vX.Y)"
                )
            elif pr_type_enum == PRType.RC:
                # RC branches target main
                base = "main"
            elif pr_type_enum == PRType.HOTFIX:
                # Hotfix branches target main
                base = "main"
            else:
                raise click.ClickException("Invalid PR type")

        # Validate base branch pattern based on PR type
        if pr_type_enum == PRType.DEV:
            if not re.match(r"^qa/[^/]+$", base):
                raise click.ClickException("Dev PRs must target a qa/* branch")
        elif pr_type_enum == PRType.QA:
            if not re.match(r"^rc/v\d+\.\d+$", base):
                raise click.ClickException("QA PRs must target an rc/vX.Y branch")
        elif pr_type_enum == PRType.RC:
            if base != "main":
                raise click.ClickException("RC PRs must target main branch")
        elif pr_type_enum == PRType.HOTFIX:
            if base != "main":
                raise click.ClickException("Hotfix PRs must target main branch")

        # Create or verify base branch exists
        try:
            # Check if branch exists remotely
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", base],
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                # Branch doesn't exist, create it based on type
                click.echo(f"🌱 Target branch '{base}' does not exist. Creating it...")

                if base == "main":
                    raise click.ClickException("Cannot create main branch - it should already exist")

                # Determine base branch for creation
                if base.startswith("qa/"):
                    # Create qa branch from main
                    create_from = "main"
                elif base.startswith("rc/"):
                    # Create rc branch from main
                    create_from = "main"
                else:
                    raise click.ClickException(f"Cannot determine how to create '{base}' branch")

                # Create and push the branch
                subprocess.run(
                    ["git", "fetch", "origin", create_from],
                    check=True,
                    capture_output=True,
                )

                # Create a new branch from origin/main
                subprocess.run(
                    ["git", "checkout", "-b", base, f"origin/{create_from}"],
                    check=True,
                    capture_output=True,
                )

                # Push the new branch
                subprocess.run(
                    ["git", "push", "origin", base],
                    check=True,
                    capture_output=True,
                )

                # Go back to original branch
                subprocess.run(
                    ["git", "checkout", source_branch],
                    check=True,
                    capture_output=True,
                )

                click.echo(f"✨ Created and pushed branch '{base}'")

        except subprocess.CalledProcessError as e:
            raise click.ClickException(
                f"Failed to verify or create base branch: {e.stderr if hasattr(e, 'stderr') else str(e)}")

        # Extract feature name from target branch for PR title
        if pr_type_enum == PRType.RC:
            # For RC PRs, use version number from source branch
            if version_number:
                pr_title = f"[{pr_type.upper()}] Release v{version_number}"
            else:
                pr_title = f"[{pr_type.upper()}] Release Candidate"
        else:
            # For other PR types, extract feature name
            feature_match = re.match(r"qa/([^/]+)|rc/v([^/]+)", base)
            if feature_match:
                feature_name = feature_match.group(1) or feature_match.group(2)
                pr_title = f"[{pr_type.upper()}] {feature_name.replace('-', ' ').title()}"
            else:
                # For other cases, extract from source branch
                source_feature_match = re.match(r"(?:dev|bugfix|hotfix)/(.+?)(?:-\d+)?$", source_branch)
                if source_feature_match:
                    feature_name = source_feature_match.group(1)
                    pr_title = f"[{pr_type.upper()}] {feature_name.replace('-', ' ').title()}"
                else:
                    # Fallback to branch name for title
                    fallback_name = branch_suffix or version_number or "Untitled"
                    pr_title = f"[{pr_type.upper()}] {fallback_name.replace('-', ' ').title()}"

        # Base PR command
        cmd = [
            "gh",
            "pr",
            "create",
            "--head",
            source_branch,
            "--base",
            base,
            "--title",
            pr_title,
        ]

        # Add body with issue reference if available
        # Extract issue number from head branch if not already set
        if not issue_number:
            issue_match = re.search(r"-(\d+)$", source_branch)
            if issue_match:
                issue_number = issue_match.group(1)

        if issue_number:
            try:
                # Get issue details
                issue_data = subprocess.run(
                    ["gh", "issue", "view", issue_number, "--json", "title"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                issue = json.loads(issue_data.stdout)

                # Add issue reference
                if pr_type_enum == PRType.RC:
                    body = f"Closes #{issue_number}\n\n{issue['title']}"
                else:
                    body = f"Related to #{issue_number}\n\n{issue['title']}"

                cmd.extend(["--body", body])

            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                click.echo(f"⚠️  Warning: Could not fetch issue #{issue_number}: {e}")
                # Continue with basic body
                cmd.extend(["--body", "PR created without issue reference"])
        else:
            cmd.extend(["--body", "PR created from branch without associated issue"])

        # Add appropriate labels based on PR type and state
        if pr_type_enum == PRType.DEV:
            type_label = "enhancement" if branch_type == "dev" else "bug"
        elif pr_type_enum == PRType.HOTFIX:
            type_label = "hotfix"
        elif pr_type_enum == PRType.RC:
            type_label = "enhancement"  # Default to enhancement for RC PRs
        else:  # QA PRs
            # Don't add type label for QA PRs as they may include multiple types
            type_label = None

        if type_label:
            cmd.extend(["-l", type_label])

        if draft:
            cmd.extend(["-l", "wip"])
            cmd.append("--draft")
        else:
            cmd.extend(["-l", "ready-for-review"])

        # Create PR
        click.echo(f"Creating PR from {source_branch} to {base}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        pr_number = pr_url.split('/')[-1]

        # Link PR to issue
        if issue_number:
            try:
                owner = get_repo_owner()
                repo = get_repo_name()

                # Link by creating a reference comment
                comment_cmd = [
                    "gh", "api",
                    f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
                    "--method", "POST",
                    "-f", f"body=Linked to #{pr_number}"
                ]

                result = subprocess.run(comment_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    click.echo(f"✨ Linked to issue #{issue_number}")
                else:
                    click.echo(f"⚠️  Warning: Failed to link issue #{issue_number}")
                    click.echo(f"Error: {result.stderr}")

            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                click.echo(f"⚠️  Warning: Failed to link issue #{issue_number}")
                click.echo(f"Error: {str(e)}")
                if hasattr(e, 'stderr'):
                    click.echo(f"stderr: {e.stderr}")

        click.echo(f"✨ Pull request created: {pr_url}")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        click.echo(f"Error creating PR: {error_msg}", err=True)
    except json.JSONDecodeError as e:
        click.echo(f"Error parsing JSON response: {e}", err=True)


@cli.command()
@click.argument("branch_name", required=False)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force sync, stashing local changes",
)
def sync(branch_name: Optional[str] = None, force: bool = False):
    """Sync local repository with remote changes"""
    verify_gh_cli()

    try:
        if not branch_name:
            # Get current branch
            branch_name = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True
            ).strip()

        click.echo(f"🔍 Checking branch: {branch_name}")

        # Sync the branch
        sync_remote_branch(branch_name, force)

    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
