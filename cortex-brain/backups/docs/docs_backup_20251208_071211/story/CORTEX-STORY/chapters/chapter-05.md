# Chapter 5: The Knowledge Graph Incident

"""Simple, effective knowledge graph edges"""
    REFERENCES = "references"  # File A imports File B
    INFLUENCES = "influences"   # Decision A led to Implementation B
    CONFLICTS = "conflicts_with" # Approach A contradicts Approach B
```

Three relationships. Three simple edges that could represent 80% of the connections that mattered.

His wife appeared in the doorway—she had a sixth sense for 2 AM breakthroughs. Two coffee mugs in hand.

"You figured it out," she said. Not a question.

"You were right."

"I'm always right. Took you three days to realize it this time." She handed him a mug, settled into the thinking chair. "Show me."

He walked through the implementation. Three relationship types. Automatic detection based on code analysis, conversation content, git history. Entity extraction from text. Relationship scoring based on frequency and recency.

"Simple," she said when he finished. "Elegant. Actually implementable."

"Unlike my previous design."

"Unlike your previous seventeen designs." She sipped her coffee. "You're learning. Slowly. Painfully. But learning."

"I have a good teacher."

"You have a patient wife who's tired of hearing 'but what if we need to represent seventeen types of epistemological relationships.'" She softened the words with a smile. "Build this one. See what breaks. Iterate."

By 7 AM, Tier 2 was operational. The knowledge graph started connecting conversations, files, decisions, implementations. Not perfectly. Not comprehensively. But usefully.

CORTEX asked him: "Implement caching layer."

CORTEX's response: "I found three related contexts: 1) Your PostgreSQL decision from last week, 2) Your discussion about Redis two weeks ago, 3) Your performance concerns from last month. Would you like me to synthesize an approach that addresses all three?"

Codenstein stared at the response. CORTEX wasn't just remembering conversations. It was connecting them. Understanding how past decisions influenced present needs.

"It's thinking," he said quietly.

Not thinking like a human. But thinking like something new. Something that could see patterns across time, connect ideas across contexts, build understanding from accumulated knowledge.

His wife had gone back to bed hours ago, leaving a note on his keyboard: "Don't forget to eat. Don't forget to sleep. Don't forget you still haven't cleaned the mold mugs. - Management"

He looked at the coffee mug timeline. Mug seventeen had definitely achieved sentience and was plotting revolution.

But that was a problem for tomorrow.

Tonight, CORTEX had learned to connect dots.

---

# Chapter 6: The Token Crisis

"We have a problem," Codenstein announced at breakfast (an actual breakfast, at an actual morning time—his wife had implemented a strict "no coding after midnight" rule after the fourth 3 AM breakthrough).

She didn't look up from her phone. "Define 'we.'"

"CORTEX is becoming expensive."

That got her attention. She set down her phone with the deliberate motion of someone preparing for bad news. "Expensive how?"

He pulled up his laptop, showing her the token analytics. "The main prompt file. It started at 8,000 tokens. Then I added the agent definitions—12,000 tokens. Then Tier architecture documentation—19,000 tokens. Then response templates—"

"How many tokens is it now?"

"Seventy-four thousand."

She set down her coffee with slightly more force than necessary. "Tokens are... expensive?"

"Very. And every request loads the full prompt. Seventy-four thousand tokens, every single time. We're burning through API costs like—" He paused, knowing what was coming.

"Like you burn through coffee?"

"Worse. Coffee is cheap. Tokens are not." He showed her the cost analysis. "At current usage, CORTEX would cost about $8,000 a month to run."

"For one user?"

"For one user."

She was quiet for a moment, processing the implications. "So your brilliant AI assistant that gives Copilot perfect memory and specialized agents and knowledge graphs... costs more per month than our mortgage?"

"Technically yes, but—"

"No buts. That's not sustainable." She took his laptop, scrolling through the token breakdown with the focused intensity of an auditor finding fraud. "What's taking up the most space?"

"Response templates. Thirty-two templates, each with examples, variations, conditions—"

"Do you load all thirty-two templates every time?"

"Yes? They're in the main prompt file—"

"Why?"

He opened his mouth. Closed it. Opened it again. The truth was embarrassing. "...Because that's where I put them?"

"That's not a reason. That's a tautology." She stood, grabbing her own laptop with the energy of someone about to perform surgery. "Show me these templates."

---

## The Great Token Purge

What followed was three hours of his wife systematically dismantling his beautiful, elegant, completely unsustainable prompt architecture.

She declared each cut with surgical precision. "Response templates don't need to be in the main prompt. They're static. Move them to a YAML file. Load on demand." She highlighted thirty-two templates for deletion.

"But then we need logic to—"

"Yes. Write logic. That's what developers do." She moved to the next section without pause. "Agent definitions. Do you need the full implementation details in the prompt?"

"It helps Copilot understand—"


---


## Navigation

← [Previous: Chapter 4](chapter-04.md) | [📚 Story Home](../THE-AWAKENING-OF-CORTEX.md) | [Next: Chapter 6 →](chapter-06.md)

