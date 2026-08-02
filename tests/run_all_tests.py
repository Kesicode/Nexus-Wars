import unittest
import sys
import os

def main():
    print("==========================================================")
    print(" EXECUTING MASTER UNIT TEST SUITE (tests/)")
    print("==========================================================")
    
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("==========================================================")
    if result.wasSuccessful():
        print("ALL UNIT TESTS PASSED SUCCESSFULLY! ✅")
        sys.exit(0)
    else:
        print(f"UNIT TEST FAILURES DETECTED: {len(result.failures)} Failures, {len(result.errors)} Errors ❌")
        sys.exit(1)

if __name__ == '__main__':
    main()
