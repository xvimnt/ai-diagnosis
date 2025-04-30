import pytest
import sys

if __name__ == "__main__":
    # Run pytest with verbose output and show locals on failures
    sys.exit(pytest.main(["-v", "--tb=short", "--showlocals", "tests/"]))
