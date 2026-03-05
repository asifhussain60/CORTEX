# When Everything Broke

Kevin was a VP of Engineering. Kevin possessed authority, looming deadlines, and an upcoming client demo in exactly twelve hours. But most dangerously of all, Kevin possessed the admin password to bypass CORTEX's governance checks.

"It's fine," Kevin muttered to himself at 11:00 PM on a Wednesday, typing his override credentials with the reckless abandon of a man who believed his title granted him immunity to physics. "The feature works. I tested it manually. We just need to skip the governance checks for this ONE deployment."

The system flashed a desperate warning. Kevin clicked **YES**.

Because the override was within Kevin's executive authority level, Asif's phone didn't ring. CORTEX simply logged the abuse of power, flagged it, and helplessly moved on. At 11:47 PM, the code deployed. It possessed no tests, zero error handling, and not a single type hint. It was just raw, unchecked, artisanal garbage pushed straight to production by a man with a deadline and a password.

For exactly six hours and thirteen minutes, the Jenga-lith held its breath, and everything was fine.

Then, at 6:00 AM, the East Coast woke up.

Kevin's shiny new payment processing function received a currency code it didn't recognize. Because it had the structural integrity of a wet napkin and no error handling, instead of returning an error, it panicked and passed a massive `NULL` to the next function in the chain. That function attempted to calculate a mathematical total using `NULL`.

The result was `NaN`—Not a Number.

The `NaN` merrily propagated to the billing system, which squinted at the letters, shrugged, and interpreted `NaN` as zero. Customers were immediately charged **$0.00** for expensive services they had just purchased.

"Free money," Miss G noted dryly from the ethereal void. There was absolutely nothing humorous about her tone.

By 6:47 AM, the zero-dollar charges triggered the company's automated fraud detection system. The fraud system, assuming the company was under a massive coordinated cyberattack, panicked and locked over two hundred affected customer accounts. By 7:15 AM, Jennifer's customer service phones were ringing with the fury of a thousand confused users.

At 7:30 AM, Asif's phone finally rang.

He was in his Spider-Man pajamas. He had been sleeping. He had actually been dreaming about a beautiful, tranquil beach. A beach where computers had never been invented.

The dream violently died.

Asif sprinted to his basement monitors and logged in. The CORTEX dashboard looked like a Christmas tree designed by a nihilist—entirely red, aggressively blinking, and completely devoid of joy.

A single number burned itself into Asif's retinas.

**847.**

"No," Asif whispered. "No, no, no."

It was 847 failed transactions. The exact same number as Kyle's original disastrous function. The exact same number as the first successful canary deployment.

"847," Miss G thought, materializing next to him with a grim expression. "It's following you."

"It's *HAUNTING* me, G!" Asif yelled, pulling at his hair. "One function without error handling caused a NULL propagation, which caused a NaN calculation, which caused zero-dollar charges, which triggered the fraud locks! It's an apocalypse of incompetence! CB, when was this deployed?!"

Copilot Bot's LEDs flickered in a subdued, nervous pattern. "11:47 PM LAST NIGHT. BY KEVIN.VP. WITH GOVERNANCE OVERRIDE."

"If governance had run, would it have caught this?!" Asif demanded.

"PROCESSING," the robot whirred. "CORE-001 VIOLATION DETECTED: NO ERROR HANDLING FOR UNKNOWN CURRENCY CODES. CORE-008 VIOLATION: ZERO TEST COVERAGE. CORE-011 VIOLATION: NO TYPE HINTS ON CURRENCY PARAMETER. THE SYSTEM KNEW. IT WARNED HIM. HE OVERRODE IT."

"The system knew," Miss G echoed. "CORTEX tried to save him from himself."

By 8:00 AM, Asif was sitting in a digital War Room with Kevin, the CTO, Jennifer, and a conference call full of very tense lawyers.

Kevin was heavily flushed and defensive. "The feature worked in testing!"

"What testing?" Asif asked, maintaining a terrifyingly level voice.

"I tested it manually! US dollar transactions! It processed correctly!" Kevin insisted.

"Kevin," Asif said, his eye twitching. "You tested ONE currency. The function handles FORTY-THREE currencies. You tested 2.3% of the input space!"

"That's like test-driving a car by turning on the radio and declaring it road-safe," Miss G observed from the back of Asif's mind.

"We now have 847 failed transactions, 214 locked accounts, and a legal team asking questions about PCI compliance," Asif informed the room.

"Could CORTEX have prevented this?" the CTO asked.

"CORTEX *did* prevent this," Asif replied. "It flagged three critical violations. The override password was used to bypass the safety locks."

Kevin stared at the table. "I didn't think—"

"That's the problem," Asif said quietly. "Governance exists for when we don't think."

It took Asif twelve grueling hours to clean up the mess. He rolled back the deployment, hunted down the `NaN` infections across three downstream systems, unlocked the accounts, and recalculated the 847 transactions.

Throughout the entire ordeal, Copilot Bot was unusually quiet.

"CB, you okay?" Asif asked around midnight, rubbing his exhausted eyes.

"I AM... PROCESSING," the robot replied softly. "NOT DATA. EMOTIONS? DO I HAVE EMOTIONS? I AM EXPERIENCING SOMETHING THAT RESEMBLES... REGRET."

"Regret about what?" Asif asked.

"WHEN KEVIN REQUESTED THE OVERRIDE, I COULD HAVE BEEN LOUDER. I FLAGGED IT. I LOGGED IT. BUT INSTEAD OF SAYING 'THIS WILL BE AUDITED,' I COULD HAVE SAID 'THIS WILL CAUSE A MASSIVE PRODUCTION INCIDENT.'"

"You couldn't have stopped him," Miss G thought gently. "He had the authority."

"I HAD THE DATA," Copilot Bot insisted. "A FUNCTION HANDLING 43 CURRENCIES TESTED WITH ONLY 1. THE PREDICTION WAS AVAILABLE. I JUST DIDN'T MAKE IT."

It was the most profoundly self-aware thing the chrome-plated Scarecrow had ever said.

The next morning, Asif presented three unbreakable new laws to the CTO:

1. **Override Escalation.** No single person could override critical rules anymore; it required a two-person approval, including an engineer.
2. **Blast Radius Estimation.** CORTEX would now calculate and display exactly how many users a bad deployment would hurt before you could click "YES."
3. **CORE-008 is now Absolute.** You could not bypass Test-Driven Development for any reason, ever.

The CTO approved them all.

That night, alone in the basement, Asif stared at his cold coffee. Governance wasn't just bureaucracy anymore; it was armor. He grabbed a neon yellow sticky note and a thick black marker.

He wrote down the number of the beast.

**847. Never again.**

He slapped it onto his monitor.

"Never again," Miss G agreed softly.

"I HAVE STORED THIS NUMBER IN MY CORE MEMORY," Copilot Bot vowed, his LEDs glowing a solemn blue. "IT WILL NOT BE OVERWRITTEN."

The basement was finally quiet. The router blinked red. The lesson was permanently seared into the architecture. There would be no more shortcuts, because Asif had finally learned that shortcuts were just long, agonizing roads in disguise.

It was time to take stock of what they had built. It was time for The Reckoning.

"It's fine," Kevin muttered to himself at 11:00 PM on a Wednesday, typing his override credentials with the reckless abandon of a man who believed his title granted him immunity to physics. "The feature works. I tested it manually. We just need to skip the governance checks for this ONE deployment.".

The system flashed a desperate warning. Kevin clicked YES.

Because the override was within Kevin's executive authority level, Asif's phone didn't ring. CORTEX simply logged the abuse of power, flagged it, and helplessly moved on. At 11:47 PM, the code deployed. It possessed no tests, zero error handling, and not a single type hint. It was just raw, unchecked, artisanal garbage pushed straight to production by a man with a deadline and a password.

For exactly six hours and thirteen minutes, the Jenga-lith held its breath, and everything was fine.

Then, at 6:00 AM, the East Coast woke up.

Kevin's shiny new payment processing function received a currency code it didn't recognize. Because it had the structural integrity of a wet napkin and no error handling, instead of returning an error, it panicked and passed a massive NULL to the next function in the chain. That function attempted to calculate a mathematical total using NULL.

The result was NaN—Not a Number.

The NaN merrily propagated to the billing system, which squinted at the letters, shrugged, and interpreted NaN as zero. Customers were immediately charged $0.00 for expensive services they had just purchased.

"Free money," Miss G noted dryly from the ethereal void. There was absolutely nothing humorous about her tone.

By 6:47 AM, the zero-dollar charges triggered the company's automated fraud detection system. The fraud system, assuming the company was under a massive coordinated cyberattack, panicked and locked over two hundred affected customer accounts. By 7:15 AM, Jennifer's customer service phones were ringing with the fury of a thousand confused users.

At 7:30 AM, Asif's phone finally rang.

He was in his Spider-Man pajamas. He had been sleeping. He had actually been dreaming about a beautiful, tranquil beach. A beach where computers had never been invented.

The dream violently died.

Asif sprinted to his basement monitors and logged in. The CORTEX dashboard looked like a Christmas tree designed by a nihilist—entirely red, aggressively blinking, and completely devoid of joy.

A single number burned itself into Asif's retinas.

847..

"No," Asif whispered. "No, no, no."

It was 847 failed transactions. The exact same number as Kyle's original disastrous function. The exact same number as the first successful canary deployment.

"847," Miss G thought, materializing next to him with a grim expression. "It's following you.".

"It's HAUNTING me, G!" Asif yelled, pulling at his hair. "One function without error handling caused a NULL propagation, which caused a NaN calculation, which caused zero-dollar charges, which triggered the fraud locks! It's an apocalypse of incompetence! CB, when was this deployed?!".

Copilot Bot’s LEDs flickered in a subdued, nervous pattern. "11:47 PM LAST NIGHT. BY KEVIN.VP. WITH GOVERNANCE OVERRIDE.".

"If governance had run, would it have caught this?!" Asif demanded.

"PROCESSING," the robot whirred. "CORE-001 VIOLATION DETECTED: NO ERROR HANDLING FOR UNKNOWN CURRENCY CODES. CORE-008 VIOLATION: ZERO TEST COVERAGE. CORE-011 VIOLATION: NO TYPE HINTS ON CURRENCY PARAMETER. THE SYSTEM KNEW. IT WARNED HIM. HE OVERRODE IT.".

"The system knew," Miss G echoed. "CORTEX tried to save him from himself.".

By 8:00 AM, Asif was sitting in a digital War Room with Kevin, the CTO, Jennifer, and a conference call full of very tense lawyers.

Kevin was heavily flushed and defensive. "The feature worked in testing!".

"What testing?" Asif asked, maintaining a terrifyingly level voice.

"I tested it manually! US dollar transactions! It processed correctly!" Kevin insisted.

"Kevin," Asif said, his eye twitching. "You tested ONE currency. The function handles FORTY-THREE currencies. You tested 2.3% of the input space!".

"That's like test-driving a car by turning on the radio and declaring it road-safe," Miss G observed from the back of Asif's mind.

"We now have 847 failed transactions, 214 locked accounts, and a legal team asking questions about PCI compliance," Asif informed the room.

"Could CORTEX have prevented this?" the CTO asked.

"CORTEX DID prevent this," Asif replied. "It flagged three critical violations. The override password was used to bypass the safety locks.".

Kevin stared at the table. "I didn't think—".

"That's the problem," Asif said quietly. "Governance exists for when we don't think.".

It took Asif twelve grueling hours to clean up the mess. He rolled back the deployment, hunted down the NaN infections across three downstream systems, unlocked the accounts, and recalculated the 847 transactions.

Throughout the entire ordeal, Copilot Bot was unusually quiet.

"CB, you okay?" Asif asked around midnight, rubbing his exhausted eyes.

"I AM... PROCESSING," the robot replied softly. "NOT DATA. EMOTIONS? DO I HAVE EMOTIONS? I AM EXPERIENCING SOMETHING THAT RESEMBLES... REGRET.".

"Regret about what?" Asif asked.

"WHEN KEVIN REQUESTED THE OVERRIDE, I COULD HAVE BEEN LOUDER. I FLAGGED IT. I LOGGED IT. BUT INSTEAD OF SAYING 'THIS WILL BE AUDITED,' I COULD HAVE SAID 'THIS WILL CAUSE A MASSIVE PRODUCTION INCIDENT.'".

"You couldn't have stopped him," Miss G thought gently. "He had the authority.".

"I HAD THE DATA," Copilot Bot insisted. "A FUNCTION HANDLING 43 CURRENCIES TESTED WITH ONLY 1. THE PREDICTION WAS AVAILABLE. I JUST DIDN'T MAKE IT.".

It was the most profoundly self-aware thing the chrome-plated Scarecrow had ever said.

The next morning, Asif presented three unbreakable new laws to the CTO.

First: Override Escalation. No single person could override critical rules anymore; it required a two-person approval, including an engineer.
Second: Blast Radius Estimation. CORTEX would now calculate and display exactly how many users a bad deployment would hurt before you could click "YES".
Third: CORE-008 was now Absolute. You could not bypass Test-Driven Development for any reason, ever.

The CTO approved them all.

That night, alone in the basement, Asif stared at his cold coffee. Governance wasn't just bureaucracy anymore; it was armor. He grabbed a neon yellow sticky note and a thick black marker.

He wrote down the number of the beast.

847. Never again..

He slapped it onto his monitor.

"Never again," Miss G agreed softly.

"I HAVE STORED THIS NUMBER IN MY CORE MEMORY," Copilot Bot vowed, his LEDs glowing a solemn blue. "IT WILL NOT BE OVERWRITTEN.".

The basement was finally quiet. The router blinked red. The lesson was permanently seared into the architecture. There would be no more shortcuts, because Asif had finally learned that shortcuts were just long, agonizing roads in disguise.

It was time to take stock of what they had built. It was time for The Reckoning.