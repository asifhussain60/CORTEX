/CORTEX Does CORTEX depend on vscode cache? If not, can we include this before starting every phase of the plan to maximize vscode throughput?

Question: in vscode Github Copilot, when it starts Summarizing Conversation after every third item, is there a way to fix it by cleaning vscode cache or other files?

ANSWER:
 The “Summarizing conversation…” message every few turns is Copilot Chat pruning context to stay within its active token budget. It’s a feature of Copilot Chat’s context handling, not a corrupted cache. Cleaning VS Code’s cache won’t stop it from summarizing, but resetting Copilot’s local state can reduce noisy behavior temporarily.

Here’s what actually helps:

Open Command Palette → Developer: Reload Window to reset the extension host (soft restart).

Open Command Palette → Clear Editor History and Chat: Clear All Chat Sessions if available (this nukes Copilot Chat’s local conversation context).

Close VS Code, then delete the Copilot Chat storage folder for a clean slate:

%APPDATA%\Code\User\globalStorage\github.copilot-chat


Reopen VS Code → Command Palette → GitHub Copilot Chat: Reset Context (if your version exposes it).

If you want to go further, also clear VS Code’s general extension cache:

%APPDATA%\Code\CachedExtensionVSIXs
%APPDATA%\Code\Cache
%APPDATA%\Code\CachedData


(optional, but harmless)

What won’t fix it:

“Clean cache to stop summarizing” (doesn’t work because summarizing is server-side token trimming).

Reinstalling Copilot (only helps if the extension is truly broken, which yours isn’t).

Long-term real fix (the nerd truth):
You can’t disable summarization, but you can delay it by feeding Copilot less fluff and more structured context—exactly the stuff you build into CORTEX. When Copilot hits its context ceiling, it summarizes. That’s the limit of its working memory, not your IDE.

If you want, I can generate a small CORTEX-style system prompt you can pin at the top of Copilot Chat to make it hold context more efficiently and summarize less often.