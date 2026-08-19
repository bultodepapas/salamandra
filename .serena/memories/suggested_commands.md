# Suggested commands (Windows PowerShell)

## Setup
- python -m pip install -r calculations/requirements.txt

## Main verification
- python calculations/verify_calculations.py
- python calculations/verify_calculations.py --all-scripts
- python calculations/contract_lint.py
- python calculations/mutation_test.py

## Generated drawings
- python calculations/generate_blueprints.py
- python calculations/generate_blueprints.py --check
- python calculations/drawing_index.py --check

## Useful repository inspection
- rg --files
- rg "pattern" calculations design decisions research
- Get-ChildItem -Force
- Get-Content -Raw path\to\file
- git status --short
- git diff --check
- git diff -- path\to\file

Each individual calculation script can be run as documented in calculations/README.md; its validation must pass before its output is used.
