"""Shared detection for the custom distribution README.

The upstream documentation catalog checks apply to the standard CleanYourTV front page. This fork
uses README.md as a custom-edition landing page, so those catalog checks should not reject it for
omitting sections that belong to the upstream front page.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CUSTOM_README = "# CleanYourTV - Custom Edition"


def is_custom_readme():
    return (ROOT / "README.md").read_text(encoding="utf-8").lstrip("\ufeff").startswith(CUSTOM_README)


def skip_standard_readme_test(test_case):
    if is_custom_readme():
        test_case.skipTest("the custom-edition README does not use the standard project catalog")
