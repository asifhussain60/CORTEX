# The Crystal Ball and the Ghost Registry

## Jennifer's Retry Button

Jennifer from Customer Service submitted a feature request: "Add a retry button for failed payments."

Simple. Reasonable. A button. One button. How complicated could a button be?

"Very," Asif muttered, because he'd learned that the word "simple" in software development was the equivalent of "hold my beer" in a viral video — it always preceded disaster.

He looked at the existing payment flow. The retry button needed to: check if the original payment was still valid, verify the payment method hadn't expired, ensure the amount hadn't changed, confirm the merchant was still accepting payments, handle the case where the payment had actually succeeded but the confirmation was lost, manage concurrent retries from multiple users, and log everything for audit purposes.

One button. Twelve dependencies. Infinite ways to fail.

Copilot Bot, eager to help, generated the code in eight seconds flat:

```python
def retry_payment(payment_id):
    payment = get_payment(payment_id)
    result = process_payment(payment)
    return result
```

Three lines. Clean. Elegant. And it would have failed spectacularly in production in approximately forty-seven different ways.

"CB, where's the error handling?"

"Error handling?"

"What if the payment doesn't exist?"

"...Then we would get an error?"

"What if the payment already succeeded?"

"...We would process it again?"

*"So we'd charge the customer twice,"* Miss G thought, with the calm fury of someone who'd been double-charged before.

*"He generated code the way a student writes an essay,"* she continued. *"Technically responsive to the prompt, but missing everything that matters."*

---

## The Crystal Ball Concept

That night, Asif sat in the basement with his whiteboard, his cold coffee, and his existential dread, and he thought about crystal balls.

"What if you could see the future? Not mystically. Practically. What if, before you wrote any code, you could see exactly how it would fail?"

*"That's called... experience?"*

"Experience is slow. I want something faster. Something systematic. Something that shows you every failure mode BEFORE you write a single line of implementation."

*"You're describing tests."*

"I'm describing tests FIRST. Before the code. Write the test that describes what the code SHOULD do. Watch it fail — because the code doesn't exist yet. Then write the minimum code to make it pass. Then write the next test."

*"TDD. Test-Driven Development. Asif, this has existed since—"*

"Since the '90s, yes, I KNOW. But nobody DOES it. Everyone SAYS they do TDD. Nobody actually writes the test first. They write the code, then write tests that pass, then pat themselves on the back."

Asif drew a big circle on the whiteboard. Inside it: **RED → GREEN → REFACTOR**.

"Red: write a test that fails. Green: write minimum code to pass. Refactor: clean up while all tests stay green. Repeat. CORE-008. TDD mandatory. Write the failing test first. No exceptions."

*"The developers are going to hate you."*

"The developers already hate me. At least now they'll hate me AND have working code."

---

## The 60% Incident

To understand why Asif felt so strongly about TDD, you had to understand what happened with Jennifer's retry button the first time someone tried to build it.

Three months earlier, a developer named Priya had built a retry mechanism. Smart developer. Good instincts. She wrote the code first, then the tests after. Seemed fine.

Test coverage: 60%.

60% meant 40% of the code was untested. And in that untested 40% lived: the concurrent retry handling (what happens when two retries happen simultaneously), the expired payment method check, and the idempotency logic (what happens when the retry succeeds but the confirmation is lost, so the user clicks retry AGAIN).

The code went to production. A customer's card was charged three times for a single purchase.

"But the tests passed!" Priya said.

*"The tests passed because they only tested the happy path,"* Miss G observed. *"TDD isn't about proving your code works when things go right. It's about proving it works when things go wrong."*

"Write the tests first," Asif agreed. "And write them for the failures, not the successes." CORE-008 was born.

---

## The Retry Button, Reimagined

Jennifer started over with TDD. Asif sat beside her. Copilot Bot watched from his corner.

**First test:** When a payment fails, a retry button should appear. RED → GREEN.

**Second test:** When already retrying, the button should be disabled. RED → GREEN.

**Third test:** After three failed retries, the button disappears entirely. RED → GREEN.

**Fourth test:** If the payment service times out, show an appropriate message and don't pretend it succeeded. RED → GREEN.

**Fifth test:** If someone clicks twice simultaneously — maybe a very fast finger and a very slow internet connection — only one retry should actually happen. RED → GREEN.

By the time Jennifer finished: twenty-three tests. Each describing a specific scenario. Each with code that made it pass.

Governance response:

```
Coverage: 100%. All code paths tested. APPROVED.
```

Jennifer stared at the green checkmark like it owed her money.

Two months after TDD enforcement went live:

| Metric | Before TDD | After TDD |
|---|---|---|
| Production bugs/month | 23 | 4 |
| Average fix time | 4.7 hours | 1.2 hours |
| Customer-facing incidents | 8/month | 1/month |
| "Works on my laptop" incidents | Weekly | None |

![The crystal ball reveals tests written before code — RED to GREEN](images/ch-07-crystal-ball.png)

*"You're not predicting the future,"* Miss G thought. *"You're CHOOSING it. Every test you write is a statement about what the future should look like."*

"That's surprisingly philosophical for an imaginary girlfriend."

*"I'm as deep as you imagine me to be. Which, given that you're running on four hours of sleep, isn't that deep. But I'll take it."*

---

## The Amnesia Problem

But even with perfect tests and enforced quality, something was still broken.

A new developer asked: "How do we handle payment disputes?"

Six different people gave six different answers. Jennifer said the dispute resolution service handles it. Another developer pointed out that service references a deleted module. Someone else said disputes are handled inline now. A fourth person noted the tests reference a function that doesn't exist anymore. Asif found a TODO comment from eighteen months ago that just said "fix this." It had not been fixed.

*"So the answer to 'how do we handle disputes' is: nobody knows,"* Miss G summarised.

"We all know pieces."

*"Pieces that contradict each other. That's worse than knowing nothing. You have confident wrongness, which is the most dangerous kind."*

---

## The Ghost Registry

It started with a payment dispute. A customer claimed they'd been charged for a service they'd cancelled.

The billing system: no record of cancellation. The customer portal: cancellation confirmed. The accounts system: cancellation pending. Three systems. Three different answers. One very confused customer.

Asif dove in and found the "cancel subscription" function existed in *four locations*:

1. `billing/cancel_subscription.py` — the original. Cancelled immediately.
2. `services/subscription_cancel.py` — a copy someone made "temporarily" eight months ago. Cancelled at end of billing cycle.
3. `api/v2/cancel.py` — a third version for the API layer. Cancelled and issued a prorated refund.
4. `legacy/billing_cancel.py` — the oldest version, supposedly deprecated, still running in production. Just marked the subscription "inactive" without stopping charges.

*"Four versions of truth,"* Miss G thought. *"None of them the WHOLE truth."*

The cortex-registry was supposed to be the single source of truth. But over months of rapid development, it had become optimistic. It listed things that no longer existed. It missed things that had been added. It contained twenty-three entries pointing to code files deleted weeks ago.

Ghost entries. Haunting the registry like unfinished business.

"There are GHOSTS in my registry!" Asif announced, sounding more offended than alarmed.

Copilot Bot scanned. "I see no ghosts. All entries appear valid."

"CB, entry number 47 points to a file deleted in March."

"...The entry is VALID. The file is... absent."

*"That's what a ghost IS,"* Miss G thought. *"The record of something that no longer exists."*

"I thought ghosts were paranormal entities!"

*"In software, they're worse. They're data inconsistencies."*

---

## The Registry Purge

CORE-035 was already on the books: "Single canonical implementation — no duplicates." But writing a rule and enforcing a rule were different things. You could write "don't jaywalk" on a sign. That didn't stop people from jaywalking.

First registry audit results:

```
REGISTRY AUDIT RESULTS
═════════════════════
Total entries: 312
Valid entries: 267  (85.6%)
Ghost entries: 23   (7.4%)  ← file deleted, registry not updated
Stale entries: 14   (4.5%)  ← file changed, registry outdated
Missing entries: 8  (2.6%)  ← file exists, no registry entry
```

Fifteen percent of the single source of truth was wrong.

*"Imagine if 15% of a phone book was wrong,"* Miss G thought. *"You'd call your doctor and get a pizza place."*

"Honestly, that might be an improvement in some cases."

The purge was surgery: twenty-three ghosts exorcised, fourteen stale entries updated, eight missing entries catalogued, two rogue orphan files deleted. After a week: 100% accuracy. Every entry verified against reality.

*"Truth is a garden,"* Miss G observed. *"It doesn't maintain itself. You have to tend it daily."*

"That's beautiful. Did you make that up?"

*"You made it up. I'm your imagination, remember?"*

"Then I'm more poetic than I thought."

*"Don't push it."*

---

## The Canary

With the registry clean and the codebase honest, CORTEX was ready to go beyond the basement. But deploying new software was like introducing a new predator into an ecosystem — even a beneficial one could cause chaos if introduced too aggressively.

*"Canary deployment,"* Miss G suggested. *"Send a small bird in first. If it survives, the mine is safe."*

Deploy to 5% of traffic. Monitor obsessively. Kill switch ready. If everything was fine, increase to 10%, then 25%, 50%, 100%.

Copilot Bot was nervous. "What if I make a mistake in production?"

"Then the canary catches it and we roll back."

"What if I make a REALLY BIG mistake?"

"Then the canary catches it FASTER and we roll back HARDER."

*"CB, the entire point of canary deployment is that your mistakes can't cause damage."*

"...I feel slightly better."

*"'Slightly' is progress."*

D-Day. Asif's finger hovered over the deploy button. Coffee was, for once, hot. Spider-Man pyjamas freshly laundered. All signs auspicious.

*"Your finger has been hovering for four minutes."*

"I'm SAVOURING the moment."

*"You're STALLING."*

Asif pressed the button.

![The canary deployment goes live — one truth, one registry](images/ch-08-battle-for-truth.png)

First hour: 847 requests processed. All successful.

The number made Asif pause. 847. The same number as Kyle's original function. The same number that had started the governance crusade. Coincidence, probably.

*"847 requests,"* Miss G noted. *"All successful."*

At 100% deployment — full traffic through CORTEX — the metrics were unambiguous: request processing time down 40%, misrouted requests down 89%, governance violations in production down 73%, 3 AM incidents down to nearly zero.

"We're really in production," Asif said quietly.

*"You sound surprised."*

"Part of me expected it to explode on contact with reality."

*"It didn't explode."*

"It didn't explode."

Copilot Bot's LEDs glowed warm amber. "We are processing real requests for real people. We are... REAL."

For once, nobody corrected him. Because he was right.

The most dangerous bugs, though, weren't in the code. They were in the decisions people made when the code gave them power. What happened when someone decided the rules didn't apply to them? Asif would find out soon — and the answer would haunt him with a very familiar number.
