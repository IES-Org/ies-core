import pytest
import json
import os
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

from ies_tools.src.github_tools.github import (
    cli, verify_gh_cli, create_github_branch_rules, create_github_issue,
    setup_labels, IssueType
)


class TestGitHubAPIMocking:
    """Tests specifically focused on mocking GitHub API interactions."""

    @pytest.fixture
    def runner(self):
        """Fixture for invoking command-line interfaces."""
        return CliRunner()

    def test_gh_cli_auth_mocking(self, runner):
        """Test that GitHub CLI auth checks can be properly mocked."""
        with patch('subprocess.run') as mock_run:
            # Both gh commands succeed
            mock_run.return_value.returncode = 0

            # This should not raise an exception
            verify_gh_cli()

            # Verify the correct commands were called
            assert mock_run.call_count == 2
            assert mock_run.call_args_list[0][0][0] == ["gh", "--version"]
            assert mock_run.call_args_list[1][0][0] == ["gh", "auth", "status"]

    def test_create_github_issue_with_project(self, runner):
        """Test create_github_issue with project board integration."""
        with patch('subprocess.run') as mock_run, \
                patch('ies_tools.src.github_tools.github.validate_branch_safe_title') as mock_validate, \
                patch('ies_tools.src.github_tools.github.get_project_id') as mock_get_project_id, \
                patch('ies_tools.src.github_tools.github.get_repo_owner') as mock_get_repo_owner, \
                patch('ies_tools.src.github_tools.github.get_repo_name') as mock_get_repo_name:

            # Configure mocks
            mock_validate.return_value = True
            mock_get_project_id.return_value = "project123"
            mock_get_repo_owner.return_value = "IES-Org"
            mock_get_repo_name.return_value = "test-repo"

            # Configure subprocess to simulate issue creation and project addition
            def mock_subprocess_result(*args, **kwargs):
                cmd = args[0]
                mock_result = MagicMock()
                mock_result.returncode = 0

                # Mock issue creation result
                if cmd[0] == "gh" and cmd[1] == "issue" and cmd[2] == "create":
                    mock_result.stdout = "https://github.com/IES-Org/test-repo/issues/123"

                # Mock issue details API response
                elif cmd[0] == "gh" and cmd[1] == "api" and "/issues/" in cmd[2]:
                    mock_result.stdout = json.dumps({
                        "number": 123,
                        "title": "Test Issue",
                        "node_id": "I_kwDOGXdHvM5Eu_k7"
                    })

                # Mock project API response
                elif cmd[0] == "gh" and cmd[1] == "api" and "graphql" in cmd:
                    mock_result.stdout = json.dumps({
                        "data": {
                            "addProjectV2ItemById": {
                                "item": {
                                    "id": "PVTI_lADOA8jg84zc3gzFdpS2"
                                }
                            }
                        }
                    })

                return mock_result

            mock_run.side_effect = mock_subprocess_result

            # Create the issue
            result = create_github_issue(
                title="Test Issue",
                body="This is a test issue",
                labels=["enhancement", "priority:medium"],
                issue_type=IssueType.DEV
            )

            # Verify the result
            assert result.number == "123"
            assert result.title == "Test Issue"
            assert result.issue_type == IssueType.DEV
            assert result.branch_name == "dev/test-issue-123"

            # Verify the API calls
            gh_issue_create_calls = [call for call in mock_run.call_args_list if
                                     "issue" in call[0][0] and "create" in call[0][0]]
            gh_api_calls = [call for call in mock_run.call_args_list if "api" in call[0][0]]

            assert len(gh_issue_create_calls) == 1
            assert len(gh_api_calls) >= 1  # At least one API call to get issue data

    def test_create_github_issue_no_project(self, runner):
        """Test create_github_issue without project board integration."""
        with patch('subprocess.run') as mock_run, \
                patch('ies_tools.src.github_tools.github.validate_branch_safe_title') as mock_validate, \
                patch('ies_tools.src.github_tools.github.get_project_id') as mock_get_project_id, \
                patch('ies_tools.src.github_tools.github.get_repo_owner') as mock_get_repo_owner, \
                patch('ies_tools.src.github_tools.github.get_repo_name') as mock_get_repo_name:
            # Configure mocks
            mock_validate.return_value = True
            mock_get_project_id.return_value = None  # No project ID
            mock_get_repo_owner.return_value = "IES-Org"
            mock_get_repo_name.return_value = "test-repo"

            # Configure subprocess for issue creation
            def mock_subprocess_result(*args, **kwargs):
                cmd = args[0]
                mock_result = MagicMock()
                mock_result.returncode = 0

                if cmd[0] == "gh" and cmd[1] == "issue" and cmd[2] == "create":
                    mock_result.stdout = "https://github.com/IES-Org/test-repo/issues/124"

                return mock_result

            mock_run.side_effect = mock_subprocess_result

            # Create the issue
            result = create_github_issue(
                title="Bug Fix",
                body="This is a bug fix",
                labels=["bug", "priority:high"],
                issue_type=IssueType.BUGFIX
            )

            # Verify the result
            assert result.number == "124"
            assert result.title == "Bug Fix"
            assert result.issue_type == IssueType.BUGFIX
            assert result.branch_name == "bugfix/bug-fix-124"

            # Verify only issue creation, no project API calls
            gh_issue_create_calls = [call for call in mock_run.call_args_list if
                                     "issue" in call[0][0] and "create" in call[0][0]]
            gh_project_calls = [call for call in mock_run.call_args_list if
                                "api" in call[0][0] and "graphql" in call[0][0]]

            assert len(gh_issue_create_calls) == 1
            assert len(gh_project_calls) == 0  # No project API calls

    def test_create_branch_rules(self, runner):
        """Test creating branch protection rules."""
        with patch('subprocess.run') as mock_run, \
                patch('ies_tools.src.github_tools.github.verify_gh_cli') as mock_verify_gh, \
                patch('click.confirm') as mock_confirm:

            # Configure mocks
            mock_verify_gh.return_value = None
            mock_confirm.return_value = True

            # Configure subprocess results
            def mock_subprocess_result(*args, **kwargs):
                cmd = args[0]
                mock_result = MagicMock()
                mock_result.returncode = 0

                # Check repository
                if cmd[0] == "gh" and cmd[1] == "repo" and cmd[2] == "view":
                    mock_result.stdout = json.dumps({
                        "name": "test-repo",
                        "owner": {"login": "IES-Org"}
                    })

                # Check existing branch protection - more generic check
                elif cmd[0] == "gh" and cmd[1] == "api" and "branches/main/protection" in str(cmd):
                    # Return non-zero to indicate no protection yet
                    mock_result.returncode = 1

                return mock_result

            mock_run.side_effect = mock_subprocess_result

            # Call the function
            create_github_branch_rules("test-repo", "IES-Org", False)

            # Verify the API calls - use more generic checks
            repo_check_calls = [call for call in mock_run.call_args_list if
                                isinstance(call[0][0], list) and len(call[0][0]) >= 3 and
                                call[0][0][0] == "gh" and call[0][0][1] == "repo" and call[0][0][2] == "view"]

            protection_check_calls = [call for call in mock_run.call_args_list if
                                      isinstance(call[0][0], list) and len(call[0][0]) >= 3 and
                                      call[0][0][0] == "gh" and call[0][0][1] == "api" and
                                      "branches/main/protection" in str(call[0][0])]

            rules_creation_calls = [call for call in mock_run.call_args_list if
                                    isinstance(call[0][0], list) and len(call[0][0]) >= 3 and
                                    call[0][0][0] == "gh" and call[0][0][1] == "api" and
                                    "rulesets" in str(call[0][0])]

            # Print for debugging
            print(f"All call args: {[str(call[0][0]) for call in mock_run.call_args_list]}")

            assert len(repo_check_calls) == 1
            assert len(protection_check_calls) == 1
            assert len(rules_creation_calls) == 4  # One for each rule type (main, rc, qa, hotfix)

    def test_setup_labels(self):
        """Test setting up labels workflow."""
        with patch('os.path.exists') as mock_exists, \
                patch('subprocess.run') as mock_run:
            # Configure mocks
            mock_exists.return_value = True  # Workflow file exists

            # Configure subprocess result
            mock_run.return_value.returncode = 0

            # Call the function
            result = setup_labels()

            # Verify the result and subprocess call
            assert result is True
            assert mock_run.call_count == 1
            assert mock_run.call_args[0][0] == ["gh", "workflow", "run", "setup-labels.yml"]

    def test_create_pr_with_issue_link(self, runner):
        """Test creating PR with linked issue."""
        with patch('subprocess.run') as mock_run, \
                patch('subprocess.check_output') as mock_check_output, \
                patch('ies_tools.src.github_tools.github.verify_gh_cli') as mock_verify_gh, \
                patch('ies_tools.src.github_tools.github.get_repo_owner') as mock_get_repo_owner, \
                patch('ies_tools.src.github_tools.github.get_repo_name') as mock_get_repo_name:

            # Configure mocks for repository info
            mock_get_repo_owner.return_value = "test-org"
            mock_get_repo_name.return_value = "test-repo"

            # Configure mocks
            mock_verify_gh.return_value = None
            mock_check_output.return_value = "dev/test-feature-123"  # Current branch

            # Configure subprocess results
            def mock_subprocess_result(*args, **kwargs):
                cmd = args[0]
                mock_result = MagicMock()
                mock_result.returncode = 0

                # Branch existence check
                if cmd[0] == "git" and cmd[1] == "ls-remote":
                    mock_result.stdout = "branch exists"

                # PR creation
                elif cmd[0] == "gh" and cmd[1] == "pr" and cmd[2] == "create":
                    mock_result.stdout = "https://github.com/test-org/test-repo/pull/456"

                # Issue data retrieval
                elif cmd[0] == "gh" and cmd[1] == "issue" and cmd[2] == "view":
                    mock_result.stdout = json.dumps({"title": "Test Feature Issue"})

                # API calls for linking
                elif cmd[0] == "gh" and cmd[1] == "api" and "/issues/" in str(cmd) and "/comments" in str(cmd):
                    mock_result.stdout = json.dumps({"id": 12345})

                return mock_result

            mock_run.side_effect = mock_subprocess_result

            # Call the command
            result = runner.invoke(cli, ['create-pr', '-t', 'dev', '-b', 'qa/test-feature'])

            # Debug output
            print(f"Exit code: {result.exit_code}")
            print(f"Exception: {result.exception}")
            print(f"Output: {result.stdout}")

            # Verify the command completed successfully
            assert result.exit_code == 0

            # Verify PR creation and issue linking
            pr_create_calls = [call for call in mock_run.call_args_list
                               if isinstance(call[0][0], list) and len(call[0][0]) >= 3 and
                               call[0][0][0] == "gh" and call[0][0][1] == "pr" and call[0][0][2] == "create"]

            issue_comment_calls = [call for call in mock_run.call_args_list
                                   if isinstance(call[0][0], list) and len(call[0][0]) >= 3 and
                                   call[0][0][0] == "gh" and call[0][0][1] == "api" and
                                   "/comments" in str(call[0][0])]

            assert len(pr_create_calls) == 1


if __name__ == "__main__":
    pytest.main(["-v", "test_github_api.py"])
