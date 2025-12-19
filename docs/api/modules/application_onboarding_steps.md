# application_onboarding_steps

Application Onboarding Steps

Concrete step implementations for the CORTEX application onboarding experience.
Includes crawler orchestration, documentation generation, and smart analysis.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CopyEntryPointsStep](#copyentrypointsstep)
- [InstallToolingStep](#installtoolingstep)
- [InitializeBrainTiersStep](#initializebraintiersstep)
- [CrawlApplicationStep](#crawlapplicationstep)
- [AnalyzeDiscoveriesStep](#analyzediscoveriesstep)
- [GenerateSmartQuestionsStep](#generatesmartquestionsstep)
- [PresentOnboardingSummaryStep](#presentonboardingsummarystep)

### Functions
- [register_application_onboarding_steps](#register_application_onboarding_steps)


## Overview

- **Classes:** 7
- **Functions:** 1
- **Dependencies:** datetime, demo_discovery, epm, logging, os, pathlib, shutil, src, typing


## Classes

### CopyEntryPointsStep

```python
class CopyEntryPointsStep(OnboardingStep)
```

Copy CORTEX entry points to target application


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Validate that project root is accessible

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Copy CORTEX entry points to target project

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

### InstallToolingStep

```python
class InstallToolingStep(OnboardingStep)
```

Detect and validate tooling requirements


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Always return True - tooling detection can always run

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Detect tooling and provide installation guidance

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

### InitializeBrainTiersStep

```python
class InitializeBrainTiersStep(OnboardingStep)
```

Initialize CORTEX brain tiers for the application


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Validate project root exists

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Initialize brain tier directories

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

### CrawlApplicationStep

```python
class CrawlApplicationStep(OnboardingStep)
```

Crawl application to discover architecture, tech stack, and patterns


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Validate project root exists and has source files

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Execute discovery crawlers and generate reports

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

### AnalyzeDiscoveriesStep

```python
class AnalyzeDiscoveriesStep(OnboardingStep)
```

Analyze crawler discoveries and extract insights


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Always return True - analysis can always run

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Analyze discoveries and generate insights

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

### GenerateSmartQuestionsStep

```python
class GenerateSmartQuestionsStep(OnboardingStep)
```

Generate contextual questions based on discoveries


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Always return True - question generation can always run

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Generate smart questions

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

### PresentOnboardingSummaryStep

```python
class PresentOnboardingSummaryStep(OnboardingStep)
```

Present comprehensive onboarding summary


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> bool
  ```

  Always return True - summary can always be presented

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> StepResult
  ```

  Present onboarding summary

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** StepResult



---

## Functions

### register_application_onboarding_steps

```python
register_application_onboarding_steps(registry: StepRegistry)
```

Register all application onboarding steps with the step registry


**Parameters:**

- `registry` (StepRegistry)


---
