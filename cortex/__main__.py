"""CORTEX Package Entry Point.

Enables running CORTEX via: python -m cortex

Delegates to the CLI entry point at cortex.cli.__main__.main().

Author: Asif Hussain
Phase: 110
AC-ID: AC-P110-001
"""

from cortex.cli.__main__ import main

main()
