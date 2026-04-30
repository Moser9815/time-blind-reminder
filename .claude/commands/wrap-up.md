---
description: End-of-session wrap-up — runs review agents, updates HANDOFF/BUGS/PRD, verifies tracking is current
---

End the current session cleanly. Updates tracking files and runs review agents.

1. **Run review agents in parallel** — `developer-review`, `embedded-reviewer` (only if firmware changed), `ui-renderer-reviewer` (only if `ui/` changed). Address any blocking findings before continuing.
2. **Update `.claude/HANDOFF.md`**:
   - **Last Session**: 1-3 bullets of what got done
   - **Open Bugs**: cross-reference `BUGS.md` for anything still open
   - **What's Next**: most logical next step
   - **Parking Lot**: carry forward any "later" ideas mentioned
3. **Update `BUGS.md`** — log any new bugs found, mark fixed bugs as resolved with the file:line of the fix.
4. **Update `PRD.md`** if the user gave product direction this session — invoke the `product-owner` agent.
5. **Check `.claude/PLAN.md`** — if it exists, either tick off completed steps or delete the file if the work is done.
6. **Git status** — call out uncommitted changes. Don't commit unless the user asks.
7. Report a 2-3 line summary of session outcome.
