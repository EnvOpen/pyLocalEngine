- [x] Make full CI/CD script to emulate the GitHub Actions workflow (Without pypi push)
- [x] fix below issue:

**Problem Title:** ~~Fix Failing CI Job and Type Issues in pyLocalEngine~~ ✅ RESOLVED

**Problem Statement:** ~~RESOLVED - All type issues have been fixed~~

✅ **All issues have been successfully resolved:**

1. ✅ Updated `pyproject.toml` to use Python 3.10 for mypy compatibility
2. ✅ Replaced `X | Y` union types with `Union[X, Y]` in `locale_detector.py`
3. ✅ Removed invalid `type: ignore` comments
4. ✅ Fixed `winreg` import and attribute access issues
5. ✅ Added missing type stubs for `requests` and `PyYAML`
6. ✅ Fixed type issues in `file_manager.py`:
   - ✅ Converted Path objects to str before appending to lists
   - ✅ Added proper type annotations for variables
   - ✅ Fixed return types and assignments
7. ✅ Added explicit type annotations to all function definitions in `engine.py`
8. ✅ Fixed line length issues for flake8 compliance
9. ✅ Created comprehensive CI test script (`ci-test.sh`)

**Final Status:** 
- ✅ mypy: No issues found in 6 source files
- ✅ flake8: All linting checks pass
- ✅ black: Code formatting is consistent
- ✅ isort: Import organization is clean
- ✅ pytest: All 24 tests pass
- ✅ Examples: All demonstration scripts work correctly

The CI/CD pipeline should now pass completely.
