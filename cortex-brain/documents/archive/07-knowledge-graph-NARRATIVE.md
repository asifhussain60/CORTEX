# PRESENTATION NARRATIVE: Knowledge Graph (Tier 2)

**Feature:** Pattern Learning and Semantic Search  
**Target Audience:** Data scientists, ML engineers, knowledge engineers  
**Image:** 3D force-directed graph with adaptive weighted connections

---

## IMAGE OVERVIEW

This 3D force-directed graph shows CORTEX's knowledge graph—8,429 purple nodes representing concepts, connected by 24,817 weighted edges. Gold thick edges show strong associations (co-occurrence >50 times), cyan pulsing edges show active learning (Hebbian: nodes that activate together link together), light purple thin edges show weak associations that may prune.

---

## OPENING STATEMENT (30 seconds)

"This is CORTEX's Tier 2 knowledge graph—8,429 concept nodes with adaptive learning connections. Watch edges strengthen in real-time: when 'TDD' and 'Git Checkpoints' activate together, their connection thickens from light purple to cyan to gold. This is Hebbian learning: 'Nodes that activate together, link together.' With 12ms semantic search and 3,214 strong associations, this graph learns usage patterns automatically."

---

## GRAPH STRUCTURE & LEARNING

"Node sizes indicate importance: large nodes like 'TDD Workflow' have 50-100 connections—these are core concepts. Small peripheral nodes like 'Error Handling' have 5-20 connections. Graph physics arranges them naturally: strongly connected nodes pulled close, weakly connected pushed apart."

**Visual Cue:** Point to node size variations

"Left panel shows Hebbian learning live: 'Feature Planning' and 'ADO Integration' nodes flash simultaneously (user query mentioned both), their edge thickens from 0.25 weight to 0.55, color changes light purple → cyan indicating active learning. After multiple co-activations, edge turns gold at 0.85 weight. This is the graph teaching itself usage patterns."

**Visual Cue:** Show learning progression animation

---

## SEMANTIC CLUSTERS

"Four semantic clusters visible: TDD & Testing (top-left, red-purple tint), Architecture & Design (top-right, blue-purple), Operations & Workflows (bottom-left, green-purple), User Interactions (bottom-right, amber-purple). Force-directed layout creates these clusters naturally—frequently co-occurring concepts gravitate together. No manual categorization needed."

**Visual Cue:** Circle each cluster region

---

## SEMANTIC SEARCH (FTS5)

"Right side: FTS5 search beam enters, query 'How does TDD work with git checkpoints?' activates relevant nodes, golden trail highlights shortest path (TDD → Test Success → Git Checkpoint, 2 hops). Context expansion illuminates 1-hop neighbors. 8,429 nodes searched, 24 matches found in 12ms. This is semantic search: understanding relationships, not just keyword matching."

**Visual Cue:** Trace search activation and path finding

---

## CLOSING STATEMENT (30 seconds)

"CORTEX's knowledge graph combines classic graph theory with adaptive learning. Force-directed physics organizes concepts naturally. Hebbian learning strengthens frequently-used connections automatically. FTS5 semantic search finds relationships in milliseconds. The result: a self-organizing knowledge base that learns from every interaction."

---

## KEY TAKEAWAYS

1. **8,429 nodes & 24,817 edges** form adaptive knowledge network with Hebbian learning
2. **Force-directed layout** naturally clusters related concepts without manual categorization
3. **Weighted edges** (gold=strong, cyan=learning, light purple=weak) show relationship strength
4. **12ms semantic search** using FTS5 full-text engine with graph traversal
5. **Self-organizing clusters** emerge from usage patterns, not predefined categories
