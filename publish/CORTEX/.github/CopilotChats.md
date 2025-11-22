manjum_HQY01: /cortex show me the knowledge graph learnings in a concise manor without code snippets. onluy show me phonedir graphs

GitHub Copilot: I'll read the CORTEX knowledge graph and filter for PhoneDir-specific learnings.

Read

The knowledge graph contains only CORTEX/KDS-specific learnings, not PhoneDir. The PhoneDir project doesn't have a CORTEX brain yet - this is the CORTEX repository itself within the CORTEX folder.

Key Learnings (Non-PhoneDir):
🛡️ SKULL Protection Layer (Nov 9, 2025)

Problem: Fixes claimed without tests 3x, integrations without E2E validation
Solution: 4 blocking/warning rules enforcing test-before-claim
Victory: Vision API now actually called vs falling back to mock
Tests: 20/20 passing, incident prevention validated
🔧 PowerShell Patterns

Regex: Use hex escapes (\x27, \x22) not backticks for quotes
Paths: Detect if workspace ends with \KDS to avoid doubling
Jobs: Use -ScriptBlock not -FilePath for parameter passing
Dependencies: Requires powershell-yaml module
🖼️ WPF Testing (Nov 5, 2025)

Problem: Silent failures - app clicked, nothing happens
Cause: XAML errors occur before UI, build success ≠ runtime success
Solution: TDD mandatory for WPF (53 tests created retroactively)
Icon validation: Test PackIconKind enums before XAML (Lightning→Flash fix)
📚 KDS Quadrant Documentation

4 perspectives: Story (narrative) + Technical (specs) + Visual (diagrams) + Architecture (high-level)
Ensures complete understanding across learning styles
