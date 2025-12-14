# CORTEX Setup Orchestration

This diagram illustrates CORTEX's automated setup process.

**Start** initiates the setup orchestrator.

**Platform Detection** identifies OS (Windows/Mac/Linux) and configures environment accordingly.

**Install Dependencies** installs Python packages, validates versions, and checks for required tools.

**Configuration** creates cortex.config.json from template, prompts for API keys (optional).

**Brain Initialization** creates tier databases, loads protection rules, validates schema.

**Done** confirms CORTEX is ready for use with health check report.

This orchestration handles cross-platform differences automatically - the same command works on any OS.