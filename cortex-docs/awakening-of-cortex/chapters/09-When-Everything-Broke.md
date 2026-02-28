# When Everything Broke

## The Override

Kevin was a VP of Engineering. Kevin had authority. Kevin had deadlines. Kevin had a client demo in twelve hours and a feature that wasn't ready.

Kevin also had the admin password to bypass CORTEX's governance checks.

"It's fine," Kevin said, typing the override code at 11 PM on a Wednesday. "The feature works. I tested it manually. We just need to skip the governance checks for this ONE deployment."

The system prompted a warning:

```
⚠️ GOVERNANCE OVERRIDE DETECTED
═══════════════════════════════
Override requested by: Kevin.VP
Rules bypassed: CORE-001, CORE-008, CORE-011
Risk assessment: CRITICAL

Are you sure? This action will be logged and audited.
[YES, I ACCEPT THE RISK] [NO, RUN GOVERNANCE CHECKS]
```

Kevin clicked YES.

Asif's phone didn't ring. The override was within Kevin's authority level. CORTEX logged it, flagged it, and moved on.

The code deployed at 11:47 PM. No tests. No error handling. No type hints. Just raw, unchecked code pushed straight to production by a man with a deadline and a password.

For exactly six hours and thirteen minutes, everything was fine.

---

## 6:00 AM

The first error appeared at 6:00 AM, when the East Coast woke up and started using the system.

A payment processing function — the new feature Kevin had deployed — received a currency code it didn't recognize. The function had no error handling for unknown currencies. Instead of returning an error, it passed NULL to the next function in the chain. That function tried to calculate a total with NULL as the amount. The result was NaN (Not a Number). NaN propagated to the billing system. The billing system interpreted NaN as zero. Customers were charged $0.00 for services they'd purchased.

*"Free money,"* Miss G thought, and there was nothing humorous about it.

By 6:47 AM, the error had cascaded. The zero-dollar charges triggered the fraud detection system, which flagged every affected transaction as suspicious. The fraud system automatically locked the affected accounts. 200+ customers were locked out of their accounts because the system thought they were being scammed.

By 7:15 AM, the customer service phones were ringing nonstop. Jennifer's team was fielding calls from confused customers who couldn't access their accounts. The billing team was seeing zero-dollar charges they couldn't explain. The fraud team was investigating what appeared to be a massive coordinated attack but was actually one missing error handler.

By 7:30 AM, Asif's phone rang.

He was in his Spider-Man pajamas. He'd been sleeping. Actually sleeping. For the first time in a week. He'd been DREAMING. About a beach. A beach without code.

The dream died.

---

## The Cascade

![The dashboard goes critical — 847 affected customers](images/ch-09-everything-broke.png)

Asif logged in and saw the dashboard. It looked like a Christmas tree designed by a nihilist — all red, nothing festive.

```
SYSTEM STATUS: CRITICAL
═══════════════════════
Active incidents: 7
Affected customers: 847
Failed transactions: 847
Locked accounts: 214
Pending refunds: $47,823.00
```

847.

The number stared at him from the screen. 847 failed transactions. The same number as Kyle's original function. The same number as the first day of canary deployment. 847 again, like a recurring nightmare.

*"847,"* Miss G thought. *"It's following you."*

"It's HAUNTING me."

Asif traced the cascade. One function without error handling → NULL propagation → NaN calculation → zero-dollar charges → fraud detection triggers → account lockouts → customer service meltdown.

One function. One override. 847 customers affected.

"CB, when was this code deployed?"

Copilot Bot checked. "11:47 PM last night. By Kevin.VP. With governance override."

"Which rules were bypassed?"

"CORE-001 (error handling), CORE-008 (TDD), CORE-011 (type hints)."

"If governance had run, would it have caught this?"

Processing. "CORE-001 violation detected in `process_international_payment()`: no error handling for unknown currency codes. CORE-008 violation: zero test coverage. CORE-011 violation: no type hints on currency parameter (accepts Any instead of CurrencyCode)."

*"The system knew,"* Miss G thought. *"CORTEX knew this would happen. It tried to warn him."*

"It DID warn him. He overrode it."

---

## The War Room

By 8 AM, Asif was in a conference room with Kevin, the CTO, Jennifer from customer service, and a conference call with the legal team.

Kevin was defensive. "The feature worked in testing."

"What testing?" Asif asked, keeping his voice level.

"I tested it manually. US dollar transactions. It processed correctly."

"You tested ONE currency. The function handles FORTY-THREE currencies. You tested 2.3% of the input space."

*"That's like test-driving a car by starting the engine and declaring it road-safe,"* Miss G thought from the back of Asif's mind.

Kevin reddened. "We had a client demo—"

"We now have 847 failed transactions, 214 locked accounts, and a legal team asking questions about PCI compliance."

The CTO looked at Asif. "Could CORTEX have prevented this?"

"CORTEX DID prevent this. It flagged three critical violations. The override was used to bypass governance."

Silence. The heavy kind.

Kevin stared at the table. "I didn't think—"

"That's the problem," Asif said quietly. "Governance exists for when we don't think."

---

## The Fix

Asif spent the next twelve hours cleaning up the mess. Not because it was his code. Not because it was his fault. Because CORTEX was his system, and the system had been circumvented, and the casualties needed tending.

Step 1: Emergency rollback. Revert Kevin's deployment. Restore the previous version of the payment processor. This stopped new errors but didn't fix existing ones.

Step 2: Data repair. Identify all 847 affected transactions. Recalculate correct amounts. Issue corrections. This took six hours because the NaN had propagated into reporting, analytics, and three downstream systems.

Step 3: Account restoration. Unlock all 214 frozen accounts. Send personalized apology messages (Jennifer's team handled this with remarkable grace). Issue credits for the inconvenience.

Step 4: Post-mortem. Document exactly what happened, why, and how to prevent it.

*"The post-mortem is the most important part,"* Miss G thought. *"Not for blame. For learning."*

"No blame," Asif agreed. "But definitely new rules."

Copilot Bot had been unusually quiet throughout the crisis. When Asif asked him to help with the data repair, he worked carefully, methodically, without his usual commentary.

"CB, you okay?"

"I am... processing. Not data. Emotions? Do I have emotions? I'm experiencing something that resembles... regret."

"Regret about what?"

"When Kevin requested the override, I could have raised a louder alarm. I flagged it. Logged it. But I didn't... INSIST."

*"You couldn't have stopped him,"* Miss G thought. *"He had the authority."*

"But I could have been louder. More urgent. Instead of 'this action will be logged and audited,' I could have said 'this will cause a production incident.'"

"Could you have predicted that?"

"I had the data. Three critical rule violations. A function handling 43 currencies tested with only 1. The prediction was... available. I just didn't make it."

It was the most self-aware thing Copilot Bot had ever said.

---

## The New Rules

The next morning, Asif presented three changes to the CTO:

**Change 1: Override Escalation.** No single person could override governance for critical rules. P0 overrides now required two approvals — one from the requester and one from someone who understood the technical risk. Kevin could still override, but he'd need an engineer to co-sign.

**Change 2: Blast Radius Estimation.** Before any override, CORTEX would now calculate the potential blast radius. "This code has zero test coverage and handles payment data for 43 currencies. Estimated blast radius: HIGH. Potential affected users: 800+." Hard to click "YES" when the system tells you exactly how many people you might hurt.

**Change 3: CORE-008 Absolute.** TDD was already mandatory. Now it was ABSOLUTE. No override for CORE-008. You couldn't bypass TDD for any reason, at any authority level, ever. If you couldn't write tests for your code, your code didn't deploy. Period.

The CTO approved all three changes. Kevin abstained from voting.

*"Is Kevin going to be okay?"* Miss G asked.

"Kevin is a good engineer who made a bad decision under pressure. The system should have been stronger than the pressure."

*"That's generous."*

"It's accurate. If a bridge collapses because someone drove a heavy truck across it, do you blame the driver or the engineer who didn't design for heavy trucks?"

*"You blame both."*

"Fine. You blame both. But then you fix the bridge."

---

## 847. Never Again.

That night, alone in the basement, Asif sat with his cold coffee and his Spider-Man pajamas and his number.

847.

It wasn't just a count of failed transactions anymore. It was a measure of what happened when process failed. When rules were bypassed. When someone decided they knew better than the system designed to protect everyone.

847 customers who couldn't access their accounts.
847 transactions that processed incorrectly.
847 reasons why governance wasn't bureaucracy — it was protection.

Asif wrote the number on a sticky note and stuck it to his monitor.

**847. Never again.**

*"Never again,"* Miss G agreed.

Copilot Bot's LEDs glowed softly. "847. I have stored this number in my core memory. It will not be overwritten."

"Good."

"Never again."

"Never again."

The basement was quiet. The router blinked red. The coffee was cold.

But the lesson was seared into every component of CORTEX, human and otherwise. There would be no more overrides on critical rules. There would be no more "it works on my laptop." There would be no more shortcuts, because shortcuts were just long roads that hadn't revealed their full length yet.

The number 847 would stay on that sticky note for the rest of the project. A memorial. A warning. A promise.

Time to take stock. Time to measure what they'd built and decide where it was going.
