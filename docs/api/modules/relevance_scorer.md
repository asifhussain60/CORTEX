# relevance_scorer

Relevance Scorer - Calculate pattern relevance for queries

Scoring factors:
- Text similarity (TF-IDF or simple word overlap)
- Namespace overlap (matching context tags)
- Pattern confidence (stored confidence score)
- Recency (prefer recently used patterns)

Composite score combines all factors for ranking.

Author: Asif Hussain


## Table of Contents

### Classes
- [RelevanceScorer](#relevancescorer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** collections, datetime, json, math, re, typing


## Classes

### RelevanceScorer

```python
class RelevanceScorer
```

Calculate and rank pattern relevance


**Methods:**

  #### `calculate_text_similarity`

  ```python
  calculate_text_similarity(self, query: str, pattern_content: str) -> float
  ```

  Calculate text similarity using word overlap

Args:
    query: Search query
    pattern_content: Pattern content to compare
    
Returns:
    Similarity score (0.0-1.0)

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `pattern_content` (str): Pattern content to compare


  **Returns:** float
    Similarity score (0.0-1.0)


  #### `calculate_namespace_overlap`

  ```python
  calculate_namespace_overlap(self, query_namespaces: List[str], pattern_namespaces: List[str]) -> float
  ```

  Calculate namespace overlap score

Args:
    query_namespaces: Context namespaces from query
    pattern_namespaces: Pattern's namespaces
    
Returns:
    Overlap score (0.0-1.0)

  **Parameters:**

  - `self`
  - `query_namespaces` (List[str]): Context namespaces from query
  - `pattern_namespaces` (List[str]): Pattern's namespaces


  **Returns:** float
    Overlap score (0.0-1.0)


  #### `calculate_recency_score`

  ```python
  calculate_recency_score(self, last_used: Optional[str]) -> float
  ```

  Calculate recency score (prefer recently used patterns)

Args:
    last_used: ISO timestamp of last use
    
Returns:
    Recency score (0.0-1.0)

  **Parameters:**

  - `self`
  - `last_used` (Optional[str]) = `None`: ISO timestamp of last use


  **Returns:** float
    Recency score (0.0-1.0)


  #### `calculate_relevance`

  ```python
  calculate_relevance(self, query: str, pattern_id: str, context_namespaces: Optional[List[str]]) -> Dict[str, Any]
  ```

  Calculate composite relevance score

Args:
    query: Search query
    pattern_id: Pattern to score
    context_namespaces: Optional context namespaces
    
Returns:
    Dict with individual scores and composite score

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `pattern_id` (str): Pattern to score
  - `context_namespaces` (Optional[List[str]]) = `None`: Optional context namespaces


  **Returns:** Dict[str, Any]
    Dict with individual scores and composite score


  #### `rank_patterns`

  ```python
  rank_patterns(self, query: str, pattern_ids: List[str], context_namespaces: Optional[List[str]]) -> List[Dict[str, Any]]
  ```

  Rank patterns by relevance

Args:
    query: Search query
    pattern_ids: List of pattern IDs to rank
    context_namespaces: Optional context namespaces
    
Returns:
    List of patterns ranked by composite score (highest first)

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `pattern_ids` (List[str]): List of pattern IDs to rank
  - `context_namespaces` (Optional[List[str]]) = `None`: Optional context namespaces


  **Returns:** List[Dict[str, Any]]
    List of patterns ranked by composite score (highest first)



---
