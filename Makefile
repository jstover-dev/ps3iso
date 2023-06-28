MODULE_PATH     := ps3iso
TESTS_PATH      := tests

default:
	@echo "Available targets: lint-check,lint-fix"

lint-check:
	poetry run autoflake --check-diff $(MODULE_PATH) $(TESTS_PATH)
	poetry run mypy -p $(MODULE_PATH)


lint-fix:
	poetry run autoflake --in-place $(MODULE_PATH) $(TESTS_PATH)
