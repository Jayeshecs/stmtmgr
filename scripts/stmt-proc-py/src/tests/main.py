import os
import sys
import unittest

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

def run_all_tests():
    """
    Discover and run all test cases in the current directory.
    """
    print("Running all tests...")
    # Discover all test cases in the current directory
    print("Discovering test cases...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=".", pattern="test_*.py")

    print(f"Discovered {suite.countTestCases()} test cases.")
    # Print the names of the discovered test cases
    for test in suite:
        print(f"Test case: {test}")
    
    # Run the test suite
    print("Running test suite...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate status code
    if result.wasSuccessful():
        print("All tests passed.")
        exit(0)
    else:
        print("Some tests failed.")
        exit(1)

if __name__ == "__main__":
    run_all_tests()