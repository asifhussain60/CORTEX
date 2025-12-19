# swagger_estimation_utility

SWAGGER Estimation Utility

SWAGGER = Scientific Wild Ass Guess Given by Experts with Rationale

Provides Definition of Ready (DoR) validation, work decomposition, and project
estimation with ADO-ready output. Replaces swagger_entry_point_orchestrator.py.

Author: Asif Hussain
Version: 1.0.0 (Migrated from orchestrator)

CRITICAL: Estimation is BLOCKED until DoR score >= 80%

Self-Test: python3 -m src.operations.modules.estimation.swagger_estimation_utility


## Table of Contents

### Classes
- [DoRStatus](#dorstatus)
- [WorkItemType](#workitemtype)
- [StoryPointScale](#storypointscale)
- [DoRQuestion](#dorquestion)
- [DoRValidationResult](#dorvalidationresult)
- [ADOStory](#adostory)
- [ADOFeature](#adofeature)
- [WorkDecompositionResult](#workdecompositionresult)

### Functions
- [initialize_dor_questions](#initialize_dor_questions)
- [get_next_unanswered_question](#get_next_unanswered_question)
- [get_questions_by_category](#get_questions_by_category)
- [validate_answer](#validate_answer)
- [submit_dor_answer](#submit_dor_answer)
- [validate_dor](#validate_dor)
- [generate_dor_progress_summary](#generate_dor_progress_summary)
- [get_dor_answers_dict](#get_dor_answers_dict)
- [extract_requirements_from_dor](#extract_requirements_from_dor)
- [is_feature_relevant](#is_feature_relevant)
- [generate_feature_acceptance_criteria](#generate_feature_acceptance_criteria)
- [calculate_feature_priority](#calculate_feature_priority)
- [estimate_story_points](#estimate_story_points)
- [recommend_team_size](#recommend_team_size)
- [generate_ado_export_json](#generate_ado_export_json)
- [generate_markdown_summary](#generate_markdown_summary)
- [decompose_work](#decompose_work)
- [check_dor_before_estimation](#check_dor_before_estimation)
- [generate_estimation](#generate_estimation)
- [get_enhanced_estimation](#get_enhanced_estimation)


## Overview

- **Classes:** 8
- **Functions:** 20
- **Dependencies:** dataclasses, datetime, enum, hashlib, json, math, pathlib, src, tempfile, time, typing


## Classes

### DoRStatus

```python
class DoRStatus(Enum)
```

Definition of Ready validation status.



---

### WorkItemType

```python
class WorkItemType(Enum)
```

ADO work item types.



---

### StoryPointScale

```python
class StoryPointScale(Enum)
```

Modified Fibonacci scale for story points.



---

### DoRQuestion

```python
class DoRQuestion
```

**Decorators:** `dataclass`

Definition of Ready validation question.


**Attributes:**

- `id`: str
- `category`: str
- `question`: str
- `required`: bool
- `follow_up_questions`: List[str]
- `validation_hints`: List[str]
- `answer`: Optional[str]
- `is_valid`: bool



---

### DoRValidationResult

```python
class DoRValidationResult
```

**Decorators:** `dataclass`

Result of DoR validation.


**Attributes:**

- `status`: DoRStatus
- `score`: float
- `questions_answered`: int
- `questions_total`: int
- `missing_categories`: List[str]
- `ambiguous_answers`: List[Dict[str, str]]
- `recommendations`: List[str]
- `can_estimate`: bool
- `validation_timestamp`: datetime



---

### ADOStory

```python
class ADOStory
```

**Decorators:** `dataclass`

ADO-ready User Story.


**Attributes:**

- `id`: str
- `title`: str
- `description`: str
- `acceptance_criteria`: List[str]
- `story_points`: int
- `priority`: int
- `tags`: List[str]
- `parent_feature_id`: Optional[str]
- `implementation_plan`: List[str]
- `technical_notes`: str
- `dependencies`: List[str]
- `estimated_hours`: float
- `complexity`: str



---

### ADOFeature

```python
class ADOFeature
```

**Decorators:** `dataclass`

ADO-ready Feature.


**Attributes:**

- `id`: str
- `title`: str
- `description`: str
- `business_value`: str
- `acceptance_criteria`: List[str]
- `priority`: int
- `tags`: List[str]
- `stories`: List[ADOStory]
- `total_story_points`: int
- `estimated_sprints`: float
- `risk_level`: str



---

### WorkDecompositionResult

```python
class WorkDecompositionResult
```

**Decorators:** `dataclass`

Result of work decomposition.


**Attributes:**

- `original_description`: str
- `features`: List[ADOFeature]
- `total_stories`: int
- `total_story_points`: int
- `estimated_sprints`: float
- `estimated_hours`: float
- `team_size_recommendation`: str
- `ado_export_json`: str
- `markdown_summary`: str



---

## Functions

### initialize_dor_questions

```python
initialize_dor_questions() -> List[DoRQuestion]
```

Initialize DoR question list from templates.

Returns:
    List of DoRQuestion instances
    
Example:
    >>> questions = initialize_dor_questions()
    >>> len(questions)
    15


**Returns:** List[DoRQuestion]
  List of DoRQuestion instances


---

### get_next_unanswered_question

```python
get_next_unanswered_question(questions: List[DoRQuestion]) -> Optional[DoRQuestion]
```

Get the next unanswered question from DoR questionnaire.

Args:
    questions: List of DoR questions
    
Returns:
    Next unanswered question or None if all answered
    
Example:
    >>> questions = initialize_dor_questions()
    >>> next_q = get_next_unanswered_question(questions)
    >>> next_q.id
    'req_1'


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions


**Returns:** Optional[DoRQuestion]
  Next unanswered question or None if all answered


---

### get_questions_by_category

```python
get_questions_by_category(questions: List[DoRQuestion], category: str) -> List[DoRQuestion]
```

Filter questions by category.

Args:
    questions: List of DoR questions
    category: Category name (requirements, dependencies, technical, security, testing)
    
Returns:
    Questions matching category
    
Example:
    >>> questions = initialize_dor_questions()
    >>> req_questions = get_questions_by_category(questions, "requirements")
    >>> len(req_questions)
    4


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions
- `category` (str): Category name (requirements, dependencies, technical, security, testing)


**Returns:** List[DoRQuestion]
  Questions matching category


---

### validate_answer

```python
validate_answer(question: DoRQuestion, answer: str) -> Tuple[bool, List[str]]
```

Validate a DoR answer for completeness and specificity.

Args:
    question: DoR question being answered
    answer: User's answer text
    
Returns:
    (is_valid, feedback_messages)
    
Example:
    >>> q = DoRQuestion(id="test", category="requirements", question="Test?")
    >>> is_valid, feedback = validate_answer(q, "Vague answer")
    >>> is_valid
    False


**Parameters:**

- `question` (DoRQuestion): DoR question being answered
- `answer` (str): User's answer text


**Returns:** Tuple[bool, List[str]]
  (is_valid, feedback_messages)


---

### submit_dor_answer

```python
submit_dor_answer(questions: List[DoRQuestion], question_id: str, answer: str) -> Tuple[bool, List[str]]
```

Submit and validate an answer for a DoR question.

Args:
    questions: List of DoR questions
    question_id: ID of question being answered
    answer: User's answer text
    
Returns:
    (is_valid, feedback_messages)
    
Example:
    >>> questions = initialize_dor_questions()
    >>> is_valid, feedback = submit_dor_answer(questions, "req_1", "Fix login timeout after 30 seconds of inactivity")
    >>> is_valid
    True


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions
- `question_id` (str): ID of question being answered
- `answer` (str): User's answer text


**Returns:** Tuple[bool, List[str]]
  (is_valid, feedback_messages)


---

### validate_dor

```python
validate_dor(questions: List[DoRQuestion]) -> DoRValidationResult
```

Perform full DoR validation and scoring.

CRITICAL: Returns can_estimate=True only if score >= 80%

Args:
    questions: List of DoR questions with answers
    
Returns:
    DoRValidationResult with score and recommendations
    
Example:
    >>> questions = initialize_dor_questions()
    >>> result = validate_dor(questions)
    >>> result.can_estimate
    False


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions with answers


**Returns:** DoRValidationResult
  DoRValidationResult with score and recommendations


---

### generate_dor_progress_summary

```python
generate_dor_progress_summary(questions: List[DoRQuestion]) -> str
```

Generate Markdown summary of DoR progress.

Args:
    questions: List of DoR questions with answers
    
Returns:
    Markdown-formatted progress summary
    
Example:
    >>> questions = initialize_dor_questions()
    >>> summary = generate_dor_progress_summary(questions)
    >>> "Definition of Ready" in summary
    True


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions with answers


**Returns:** str
  Markdown-formatted progress summary


---

### get_dor_answers_dict

```python
get_dor_answers_dict(questions: List[DoRQuestion]) -> Dict[str, str]
```

Extract answers from questions as dictionary.

Args:
    questions: List of DoR questions with answers
    
Returns:
    Dictionary mapping question_id to answer
    
Example:
    >>> questions = initialize_dor_questions()
    >>> answers = get_dor_answers_dict(questions)
    >>> isinstance(answers, dict)
    True


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions with answers


**Returns:** Dict[str, str]
  Dictionary mapping question_id to answer


---

### extract_requirements_from_dor

```python
extract_requirements_from_dor(dor_answers: Dict[str, str]) -> Dict[str, Any]
```

Extract structured requirements from DoR answers.

Args:
    dor_answers: Dictionary of DoR question_id -> answer
    
Returns:
    Structured requirements dictionary
    
Example:
    >>> dor_answers = {"req_1": "Fix login timeout", "req_2": "Admins"}
    >>> reqs = extract_requirements_from_dor(dor_answers)
    >>> "problem_statement" in reqs
    True


**Parameters:**

- `dor_answers` (Dict[str, str]): Dictionary of DoR question_id -> answer


**Returns:** Dict[str, Any]
  Structured requirements dictionary


---

### is_feature_relevant

```python
is_feature_relevant(feature_name: str, requirements: Dict[str, Any]) -> bool
```

Determine if a feature is relevant based on requirements.

Args:
    feature_name: Name of feature (Backend API, Database, etc.)
    requirements: Structured requirements from DoR
    
Returns:
    True if feature should be included
    
Example:
    >>> reqs = {"problem_statement": "Need database for user data"}
    >>> is_feature_relevant("Database", reqs)
    True


**Parameters:**

- `feature_name` (str): Name of feature (Backend API, Database, etc.)
- `requirements` (Dict[str, Any]): Structured requirements from DoR


**Returns:** bool
  True if feature should be included


---

### generate_feature_acceptance_criteria

```python
generate_feature_acceptance_criteria(feature_name: str) -> List[str]
```

Generate acceptance criteria templates for a feature.

Args:
    feature_name: Name of feature
    
Returns:
    List of acceptance criteria strings
    
Example:
    >>> ac = generate_feature_acceptance_criteria("Backend API")
    >>> len(ac) >= 3
    True


**Parameters:**

- `feature_name` (str): Name of feature


**Returns:** List[str]
  List of acceptance criteria strings


---

### calculate_feature_priority

```python
calculate_feature_priority(feature_name: str, risk: str) -> int
```

Calculate ADO priority (1-4) for a feature.

Args:
    feature_name: Name of feature
    risk: Risk level (low, medium, high)
    
Returns:
    Priority number (1=Critical, 2=High, 3=Medium, 4=Low)
    
Example:
    >>> calculate_feature_priority("Backend API", "high")
    1


**Parameters:**

- `feature_name` (str): Name of feature
- `risk` (str): Risk level (low, medium, high)


**Returns:** int
  Priority number (1=Critical, 2=High, 3=Medium, 4=Low)


---

### estimate_story_points

```python
estimate_story_points(complexity: str) -> int
```

Estimate story points based on complexity.

Args:
    complexity: Complexity level (trivial, simple, moderate, complex, very_complex, epic)
    
Returns:
    Story points (1, 2, 3, 5, 8, or 13)
    
Example:
    >>> estimate_story_points("moderate")
    3


**Parameters:**

- `complexity` (str): Complexity level (trivial, simple, moderate, complex, very_complex, epic)


**Returns:** int
  Story points (1, 2, 3, 5, 8, or 13)


---

### recommend_team_size

```python
recommend_team_size(total_story_points: int, target_sprints: int) -> str
```

Recommend team size based on story points and target timeline.

Args:
    total_story_points: Total story points for project
    target_sprints: Desired number of sprints
    
Returns:
    Team size recommendation string
    
Example:
    >>> recommend_team_size(120, 3)
    'Team of 1 developer (40 points/sprint velocity)'


**Parameters:**

- `total_story_points` (int): Total story points for project
- `target_sprints` (int): Desired number of sprints


**Returns:** str
  Team size recommendation string


---

### generate_ado_export_json

```python
generate_ado_export_json(features: List[ADOFeature]) -> str
```

Generate ADO-ready JSON export.

Args:
    features: List of ADO features with stories
    
Returns:
    JSON string ready for ADO import
    
Example:
    >>> feature = ADOFeature(id="F1", title="Test", description="Test", business_value="", acceptance_criteria=[], priority=1, tags=[], stories=[], total_story_points=0, estimated_sprints=0, risk_level="Low")
    >>> json_str = generate_ado_export_json([feature])
    >>> "work_items" in json_str
    True


**Parameters:**

- `features` (List[ADOFeature]): List of ADO features with stories


**Returns:** str
  JSON string ready for ADO import


---

### generate_markdown_summary

```python
generate_markdown_summary(features: List[ADOFeature], work_description: str) -> str
```

Generate Markdown summary of work decomposition.

Args:
    features: List of ADO features with stories
    work_description: Original work description
    
Returns:
    Markdown-formatted summary
    
Example:
    >>> feature = ADOFeature(id="F1", title="Test", description="Test", business_value="", acceptance_criteria=[], priority=1, tags=[], stories=[], total_story_points=5, estimated_sprints=0.1, risk_level="Low")
    >>> summary = generate_markdown_summary([feature], "Test work")
    >>> "# Work Decomposition Summary" in summary
    True


**Parameters:**

- `features` (List[ADOFeature]): List of ADO features with stories
- `work_description` (str): Original work description


**Returns:** str
  Markdown-formatted summary


---

### decompose_work

```python
decompose_work(work_description: str, dor_answers: Dict[str, str], max_features: int) -> WorkDecompositionResult
```

Decompose work into ADO Features and Stories.

Args:
    work_description: High-level work description
    dor_answers: DoR answers dictionary
    max_features: Maximum number of features to generate
    
Returns:
    WorkDecompositionResult with features, stories, and estimates
    
Example:
    >>> dor_answers = {"req_1": "User authentication system with OAuth2", "req_2": "Web and mobile users"}
    >>> result = decompose_work("User auth", dor_answers)
    >>> len(result.features) > 0
    True


**Parameters:**

- `work_description` (str): High-level work description
- `dor_answers` (Dict[str, str]): DoR answers dictionary
- `max_features` (int) = `7`: Maximum number of features to generate


**Returns:** WorkDecompositionResult
  WorkDecompositionResult with features, stories, and estimates


---

### check_dor_before_estimation

```python
check_dor_before_estimation(questions: List[DoRQuestion]) -> Dict[str, Any]
```

Check if DoR is complete before allowing estimation.

Args:
    questions: List of DoR questions
    
Returns:
    Status dictionary with can_estimate flag
    
Example:
    >>> questions = initialize_dor_questions()
    >>> status = check_dor_before_estimation(questions)
    >>> status["can_estimate"]
    False


**Parameters:**

- `questions` (List[DoRQuestion]): List of DoR questions


**Returns:** Dict[str, Any]
  Status dictionary with can_estimate flag


---

### generate_estimation

```python
generate_estimation(work_description: str, questions: List[DoRQuestion]) -> Dict[str, Any]
```

Generate project estimation with DoR validation.

CRITICAL: Returns error if DoR not complete.

Args:
    work_description: High-level work description
    questions: List of DoR questions with answers
    
Returns:
    Estimation result with decomposition and metrics
    
Example:
    >>> questions = initialize_dor_questions()
    >>> result = generate_estimation("Test project", questions)
    >>> "status" in result
    True


**Parameters:**

- `work_description` (str): High-level work description
- `questions` (List[DoRQuestion]): List of DoR questions with answers


**Returns:** Dict[str, Any]
  Estimation result with decomposition and metrics


---

### get_enhanced_estimation

```python
get_enhanced_estimation(work_description: str, questions: List[DoRQuestion], complexity_score: float, team_size: int) -> Dict[str, Any]
```

Get enhanced estimation with TimeframeEstimator integration.

Provides parallel track analysis, timelines, and what-if scenarios.

Args:
    work_description: High-level work description
    questions: List of DoR questions with answers
    complexity_score: SWAGGER complexity score (0-100)
    team_size: Target team size
    
Returns:
    Enhanced estimation with parallel tracks and scenarios
    
Example:
    >>> questions = initialize_dor_questions()
    >>> result = get_enhanced_estimation("Test", questions)
    >>> "status" in result
    True


**Parameters:**

- `work_description` (str): High-level work description
- `questions` (List[DoRQuestion]): List of DoR questions with answers
- `complexity_score` (float) = `50.0`: SWAGGER complexity score (0-100)
- `team_size` (int) = `1`: Target team size


**Returns:** Dict[str, Any]
  Enhanced estimation with parallel tracks and scenarios


---
