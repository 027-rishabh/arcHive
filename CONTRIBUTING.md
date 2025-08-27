# Contributing to Library Management System

Thank you for considering a contribution to **Library Management System**!  
We welcome bug reports, feature requests, documentation improvements, and pull-requests.  
This guide explains the workflow, coding standards, and community expectations so you can contribute effectively.

---

## Table of Contents
1. [Code of Conduct](#code-of-conduct)  
2. [Getting Started](#getting-started)  
3. [Ways to Contribute](#ways-to-contribute)  
4. [Development Environment](#development-environment)  
5. [Branching & Commit Guidelines](#branching--commit-guidelines)  
6. [Pull-Request Checklist](#pull-request-checklist)  
7. [Issue Reporting Guide](#issue-reporting-guide)  
8. [Style Guide](#style-guide)  
9. [Testing](#testing)  
10. [Release Process](#release-process)  
11. [Community Communication](#community-communication)  

---

## Code of Conduct
All contributors must adhere to the **Contributor Covenant Code of Conduct** (see `CODE_OF_CONDUCT.md`).  
Be respectful, inclusive, and supportive in all interactions.

---

## Getting Started
1. **Fork** the repository to your GitHub account.  
2. **Clone** your fork locally:
   ```bash
   git clone git@github.com:<your-username>/library-management-system.git
   cd library-management-system
   ```
3. **Configure upstream** to keep your fork up-to-date:
   ```bash
   git remote add upstream git@github.com:027-rishabh/arcHive.git
   git fetch upstream
   ```

---

## Ways to Contribute

| Type                     | Examples                                                                    |
|--------------------------|-----------------------------------------------------------------------------|
| **Bug Fixes**            | Crashes, incorrect results, GUI glitches                                    |
| **Enhancements**         | New features, performance improvements, UI polish                           |
| **Documentation**        | Tutorials, screenshots, clarifying README, API docs                        |
| **Testing**              | Adding unit tests, integration tests, test-coverage scripts                 |
| **Translations**         | Adding locale files for interface text                                      |
| **DevOps / CI**          | GitHub Actions workflows, packaging improvements                            |

---

## Development Environment

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # linters, test tools
```

### 3. Pre-Commit Hooks *(optional but recommended)*
```bash
pre-commit install
```
This runs **black**, **flake8**, and **isort** automatically before each commit.

### 4. Database
The app auto-creates `data/library_management.db` on first run.  
For dev, you can reset anytime:
```bash
python -c "from src.models.database import DatabaseManager; DatabaseManager().reset_database()"
```

---

## Branching & Commit Guidelines

* **main** — Always deployable; merged via reviewed PRs only.  
* **feature/<topic>** — New features and enhancements.  
* **fix/<issue-id>** — Bug fixes.  
* **docs/** — Documentation-only updates.

**Commit message format**

```
<type>(<scope>): <subject>
```
*Types*: feat, fix, docs, test, refactor, chore  
*Scope*: module or file, optional  
Example:
```
feat(transaction): add late-fee grace period
```

---

## Pull-Request Checklist

1. The PR title follows the commit message style.  
2. Code **compiles and runs** without errors.  
3. New code is **type-hinted** and **PEP 8** compliant (`flake8`).  
4. **Black** formatter produces no diff: `black --check src/`.  
5. **Unit tests** added/updated; `pytest` passes.  
6. No **debug prints** or commented-out blocks remain.  
7. If UI changes, include **before/after screenshots** in the PR description.  
8. Linked to a relevant **Issue** with `Fixes #123` (if applicable).  
9. Documentation updated (README, docstrings, or docs/).

---

## Issue Reporting Guide

When filing an issue, include:

1. **Environment** – OS, Python version, branch/commit hash.  
2. **Steps to Reproduce** – precisely how to trigger the bug.  
3. **Expected vs Actual** – what you thought would happen and what did happen.  
4. **Logs/Traceback** – paste error messages inside triple back-ticks.  
5. **Screenshots** *(UI bugs)*.  
6. **Minimal reproducible example** if possible.

Clear, detailed reports help maintainers fix problems faster.

---

## Style Guide

| Category            | Rule / Tool                    |
|---------------------|--------------------------------|
| **Formatting**      | [`black`](https://black.readthedocs.io/) (line length = 88) |
| **Imports**         | [`isort`](https://pycqa.github.io/isort/) |
| **Linting**         | [`flake8`](https://flake8.pycqa.org/) |
| **Docstrings**      | PEP 257 / NumPy style          |
| **Typing**          | Use Python type hints          |
| **UI Strings**      | Title-case labels, sentence-case messages |

---

## Testing

Run all tests:
```bash
pytest -v
```
Generate coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html   # view in browser
```
Write tests for every new public method or bug fix.

---

## Release Process

1. Ensure **main** is green (CI passing).  
2. Update `CHANGELOG.md` with notable changes.  
3. Bump version in `src/__init__.py` (semantic versioning).  
4. Create a **GitHub Release** with tag `vX.Y.Z`, attaching release notes.  
5. Build and upload distribution (future PyPI packaging).

---

## Community Communication

* **Issues** – Bug reports & feature requests  
* **Pull Requests** – Code contributions  
* **Discussions** – General questions, ideas, design debates  
* **Security vulnerabilities** – Please **do not** open public issues.  Email the maintainer for responsible disclosure.

---

Thank you for helping improve Library Management System!  
Your time and effort make the project better for everyone.
