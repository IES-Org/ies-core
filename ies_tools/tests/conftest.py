import pytest
import sys
import os
from unittest.mock import patch

# Add the parent directory to sys.path to allow imports of the application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import click to mock its confirmation dialog
import click


# Mock environment variables that might be needed
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict('os.environ', {
        'GITHUB_TOKEN': 'fake-token',
        'HOME': '/home/user'  # For gh cli config
    }):
        yield


# Prevent real subprocess calls during tests
@pytest.fixture(autouse=True)
def prevent_real_subprocess_calls():
    """Prevent any real subprocess calls during tests."""
    # This will cause tests to fail if they try to make real subprocess calls
    with patch('subprocess.run') as mock_run, \
            patch('subprocess.check_output') as mock_check_output, \
            patch('subprocess.check_call') as mock_check_call, \
            patch('subprocess.Popen') as mock_popen:
        # Configure default return values to prevent errors
        mock_process = mock_run.return_value
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""

        mock_check_output.return_value = ""
        yield


# Prevent actual creation of files or directories
@pytest.fixture(autouse=True)
def prevent_real_filesystem_operations():
    """Prevent real filesystem operations during tests."""
    with patch('os.makedirs') as mock_makedirs, \
            patch('os.mkdir') as mock_mkdir, \
            patch('os.path.exists') as mock_exists, \
            patch('builtins.open', create=True) as mock_open:
        # Default to files not existing
        mock_exists.return_value = False
        yield


# Prevent actual network calls
@pytest.fixture(autouse=True)
def prevent_real_network_calls():
    """Prevent real network calls during tests."""
    with patch('urllib.request.urlopen') as mock_urlopen:
        yield
