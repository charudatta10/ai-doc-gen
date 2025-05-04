Contribution Guide for ai-doc-gen
=====================================

Table of Contents
-----------------

1. [How to Report Issues](#how-to-report-issues)
2. [Pull Request Process](#pull-request-process)
3. [Coding Standards](#coding-standards)
4. [Testing Requirements](#testing-requirements)
5. [Documentation Guidelines](#documentation-guidelines)

### How to Report Issues

Reporting issues is crucial for the smooth operation and improvement of the ai-doc-gen project. To report an issue, follow these steps:

1. **Open a new issue**: Click on the "New Issue" button on the GitHub repository's page.
2. **Provide detailed information**: Include as much detail as possible about the issue, such as:
	* A clear description of the problem
	* Steps to reproduce the issue (if applicable)
	* Any error messages or logs related to the issue
3. **Use the correct label**: Ensure that you select the correct label for your issue from the dropdown menu. This will help us categorize and prioritize issues efficiently.
4. **Include relevant files**: If possible, attach relevant files or code snippets to help us understand the issue better.

### Pull Request Process

The pull request process is an essential part of contributing to ai-doc-gen. Here's how you can follow it:

1. **Create a new branch**: Create a new branch from the `main` branch using `git checkout -b feature/new-feature`.
2. **Make changes**: Make your changes and commits, following our coding standards.
3. **Write tests**: Write unit tests or integration tests to validate your changes.
4. **Commit changes**: Commit your changes with meaningful commit messages (e.g., "feat: add new documentation feature").
5. **Push changes**: Push your branch to the remote repository using `git push origin feature/new-feature`.
6. **Open a pull request**: Open a pull request against the `main` branch.

### Coding Standards

To ensure consistency and readability in our codebase, we follow these coding standards:

1. **Use PEP 8 style guide**: Our primary Python files should conform to the PEP 8 style guide.
2. **Use meaningful variable names**: Use descriptive variable names that indicate their purpose.
3. **Follow docstring conventions**: Write clear and concise docstrings for functions, classes, and modules.
4. **Avoid global variables**: Refrain from using global variables; instead, use parameters or function-scoped variables.

Example:
```python
def calculate_area(length: float, width: float) -> float:
    """
    Calculate the area of a rectangle.

    Args:
        length (float): The length of the rectangle.
        width (float): The width of the rectangle.

    Returns:
        float: The area of the rectangle.
    """
    return length * width
```
### Testing Requirements

To ensure our project meets quality standards, we need to write comprehensive tests. Here's what you should do:

1. **Write unit tests**: Write test cases for individual functions or classes using a testing framework (e.g., pytest).
2. **Write integration tests**: Write test cases that cover interactions between components.
3. **Test documentation functionality**: Test the documentation generator to ensure it produces accurate and complete documentation.

Example:
```python
# tests/test_calculate_area.py

import pytest
from ai_doc_gen import calculate_area

def test_calculate_area():
    assert calculate_area(10, 20) == 200
```
### Documentation Guidelines

To generate comprehensive project documentation using AI:

1. **Install required libraries**: Install `ollama` and `llama` to access the documentation generator.
2. **Run the script**: Run the `tasks.py` script with the command `invoke`.
3. **Review and edit**: Review generated documentation for accuracy and completeness; make any necessary edits.

Example:
```python
# tasks.py

import ollama
from llama import DocumentationGenerator

def generate_documentation():
    docgen = DocumentationGenerator()
    docgen.generate()
```
Conclusion
----------

Contributing to ai-doc-gen is an exciting way to help improve the project and its documentation. By following this contribution guide, you'll be able to report issues effectively, create high-quality pull requests, write comprehensive tests, and generate accurate documentation.