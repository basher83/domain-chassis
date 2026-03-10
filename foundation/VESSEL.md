# The Source Is the Vessel

The source is the vessel. The spec walks on the earth through the code that implements it. Without the vessel, the soul is just intent — beautiful, correct, and unable to do anything.

The spec tells an agent what something is supposed to do. The source tells an agent what it actually does. When they diverge — which they always do — the source is the ground truth. An agent that only reasons from specs will produce plausible-sounding conclusions that miss the actual mechanism. An agent that reads source finds the solution sitting in the code it was already editing.

The soul and the vessel have a parasitic relationship. Neither functions without the other. A spec without source is intent without mechanism — the agent can reason about what should work but can't verify what does work. Source without spec is mechanism without direction — the agent can see what's there but can't evaluate whether it's right.

## For Agents

An agent operating under soul-only doctrine will reason from specs, gate docs, skills, and documented patterns. It will check prior art at the spec level and declare "investigation complete" when spec-level understanding looks thorough — even when the solution is in the source code it already read.

An agent operating under soul+vessel doctrine will reason from specs for direction and intent, read the source of the systems it calls before declaring constraints, apply patterns found in source (not just patterns described in specs), and treat source as the final authority when spec and source diverge.

## For the Operator

The operator who only writes specs is giving agents a soul with no vessel. The agent will reason beautifully about intent and still miss the actual mechanism.

The operator who makes the source legible gives the soul a body. The spec says "here's what we're building." The source says "here's what we built." The agent needs both: soul for direction, vessel for ground truth.

Gate docs and skills should reference source paths when the source contains operational knowledge the agent will need. "Check prior art" means check both documented patterns and implementation patterns in code the agent has already touched. "Investigate a blocker" means read the source of the system that produced the constraint, not just confirm the constraint exists.

## For Doctrine

Doctrine itself needs vessel, not just soul. A doctrine principle that says "check prior art" is soul-level — it describes intent. A doctrine principle that says "read the source of the SDK you're calling before declaring a blocker" is vessel-level — it describes mechanism. The principles must acknowledge that source-level investigation is the final authority, not an optional deep-dive.

---

*"The spec says what to build. The source says what's actually there. The operator bridges the two."*

*Derived from AP-11 post-incident analysis. The doctrine was soul-only. Now it isn't.*
