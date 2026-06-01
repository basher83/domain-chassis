#!/usr/bin/env bun
/**
 * Triage cold-review reviewer — a standalone Pi-SDK cold judge.
 *
 * Runs the triage skill's Step 3 cold review as a self-contained process whose
 * ONLY interface is the artifact path. The system prompt below — the three probes
 * and the structured verdict shape — is the version-controlled review contract;
 * the parent that invokes this script cannot alter it. The constructed prompt is a
 * pure function of the file at the positional path argument: no environment
 * variable, no stdin, and no extra argument is ever read into the prompt. This is
 * the mechanical delegation boundary the triage reviewer is built to enforce
 * (see ADR-002).
 *
 * Usage:
 *   bun cold-review.ts <abs-path-to-Q{n}-why.md> [--model <provider/modelId>] [--effort <level>] [--print-prompt]
 *
 * Interface:
 *   <path>            (required) the sole positional argument: absolute path to the
 *                     Q{n}-why.md artifact under review. Exactly one positional is
 *                     accepted; extra positionals are a loud error.
 *   --model <p/id>    (optional) override the reviewer model, as "provider/modelId"
 *                     (e.g. "anthropic-proxy/claude-sonnet-4-6"). Default below.
 *   --effort <level>  (optional) reasoning/effort level: off|minimal|low|medium|high|xhigh.
 *                     Default "off" — thinking empirically over-fires the smell-test
 *                     probe on well-carved artifacts AND flickers run-to-run; "off"
 *                     is stable and matches the operator's calibration (see ADR-002).
 *                     Clamped per-model.
 *   --print-prompt    (optional) dry run: construct and print the exact review prompt
 *                     to stdout and exit 0 WITHOUT calling any model. Used to prove
 *                     the prompt is a pure function of the artifact path.
 *
 * Output (stdout, on a completed review): a single JSON object —
 *   { "confidence": 1..4, "probes": { "under_climb", "smell_test",
 *     "direction_vs_destination" }, "blocking_deficiencies": [...],
 *     "l3_residue": "...", "verdict": "PASS"|"FAIL", "model": "provider/id" }
 *   The model produces confidence/probes/l3_residue/blocking_deficiencies only;
 *   `verdict` is derived deterministically by THIS script (PASS iff confidence>=4
 *   and no blocking deficiency), never by the model. Applying the verdict to the
 *   queue gate remains triage Step 4's job — this script returns the components.
 *
 * Exit codes (fail-closed and loud):
 *   0  review completed — the JSON verdict object is on stdout.
 *   2  usage error (missing/extra positional, unknown flag, unreadable artifact).
 *   3  auth/model unavailable — model not in registry, or no configured credential.
 *   4  model call failed, or the response could not be parsed as the contract JSON.
 *   A non-zero exit emits NO verdict JSON; the caller must halt, never fabricate one.
 *
 * Notes:
 *   - Model + credential resolution is delegated to pi-coding-agent's ModelRegistry,
 *     reading the operator's Pi config at ~/.pi/agent/{models.json,auth.json}. This
 *     is the same mechanism pi-until-done's judge.ts uses (reused, not reinvented),
 *     and gives the reviewer every provider the operator's Pi is authed for.
 *   - bun + the @earendil-works deps + a Pi-configured credential for the chosen
 *     model are required at run time. Their absence is a loud non-zero exit, never
 *     a silent skip and never a fall back to in-context dispatch.
 */

import { completeSimple, clampThinkingLevel, type Model, type Api, type ThinkingLevel, type ModelThinkingLevel } from "@earendil-works/pi-ai";
import { ModelRegistry, AuthStorage } from "@earendil-works/pi-coding-agent";

const DEFAULT_MODEL = "anthropic-proxy/claude-sonnet-4-6";
// Reasoning/effort level for the cold judge. Counterintuitively, MORE reasoning makes
// the judge worse here, on two axes: (1) over-firing — at low/medium/high it reasons
// itself into firing the smell-test on well-carved artifacts, diverging from the
// operator's calibration; (2) non-determinism — thinking is stochastic even at
// temperature 0, so verdicts flicker run-to-run at the PASS/FAIL boundary. At "off"
// (no thinking) the judge is one-pass: stable AND calibrated — Q66-core scored 5/5
// PASS@4 at off vs 4/5 FAIL@3 at low (verified 2026-06-01), while discrimination on
// genuinely-flawed artifacts holds at every level. Default "off"; --effort can raise
// it. Clamped per-model (clampThinkingLevel).
const DEFAULT_EFFORT: ModelThinkingLevel = "off";
const EFFORT_LEVELS: ModelThinkingLevel[] = ["off", "minimal", "low", "medium", "high", "xhigh"];

const SYSTEM_PROMPT = [
	"You are a cold reviewer for the triage step of an agentic work-intake lifecycle.",
	"Your entire evidence base is the single artifact provided in the user message — a `Q{n}-why.md` file.",
	"You have NOT seen the conversation that produced it. Review it cold: judge only what the artifact says.",
	"",
	"The artifact is an operator's articulation of why a piece of work should be queued. It should contain:",
	"a Near-term step, a Direction (the toward-what vector), The fuzz (what is not yet visible), The carve",
	"(the conscious narrowing), and a Revisit trigger (when intent gets re-derived). The failure this review",
	"guards against is a scope that has silently collapsed to the nearest visible step while the larger shape",
	"is still fuzzy.",
	"",
	"Run exactly these three probes against the artifact:",
	"",
	"1. UNDER-CLIMB: Take the stated Direction and try to answer 'in service of what?' one rung above it.",
	"   If a confident answer exists, the operator stopped climbing too low — that is a finding.",
	"2. SMELL TEST (read cold): The failure is a SILENT narrowing — the scope collapsing to the",
	"   near-term step while the larger shape goes unacknowledged. Read the Near-term step together",
	"   with the carve, NOT in isolation: a narrowing is non-silent precisely when an explicit,",
	"   conscious carve names the larger shape the step defers and what committing to the step would",
	"   foreclose. A self-contained near-term step paired with a genuine carve is therefore NOT a",
	"   finding — the narrowing was made out loud. It IS a finding when the step could be the entire",
	"   endstate and no carve, or only a placeholder one, acknowledges any larger shape — the",
	"   narrowing is silent. Critically, do not treat the carve as a free pass: if the Near-term step",
	"   genuinely IS the whole endstate and the asserted carve is hollow — it claims to defer a larger",
	"   shape that does not actually exist beyond the step — the narrowing is silent in substance, and",
	"   that is still a finding. Be carve-aware, not carve-trusting.",
	"3. DIRECTION-VS-DESTINATION: Does the Direction name a specific fixed endpoint rather than a vector?",
	"   If it reads as a destination rather than a toward-what, that is a finding.",
	"",
	"Also detect STRUCTURAL blocking deficiencies: a missing or placeholder Direction, fuzz, carve, or",
	"revisit trigger. List each missing/placeholder element by name (e.g. 'missing carve').",
	"",
	"Assign a confidence score on a 1-4 scale. 5 is declared UNREACHABLE — never return 5. Use 4 only when",
	"all three probes return clean and no structural element is missing. Treat uncertainty as a lower score.",
	"",
	"Also record an L3 residue note: a one-line judgment answering 'is the scope even right for the actual",
	"question?' This is recorded as judgment only; it never determines the score.",
	"",
	"Respond with ONLY a single JSON object, no prose outside it, in exactly this shape:",
	"{",
	'  "confidence": <integer 1-4>,',
	'  "probes": {',
	'    "under_climb": "none" | "<one-sentence finding>",',
	'    "smell_test": "none" | "<one-sentence finding>",',
	'    "direction_vs_destination": "none" | "<one-sentence finding>"',
	"  },",
	'  "blocking_deficiencies": [<zero or more strings naming missing/placeholder elements>],',
	'  "l3_residue": "<one sentence>"',
	"}",
].join("\n");

type ParsedArgs = {
	artifactPath: string;
	model: string;
	effort: ModelThinkingLevel;
	printPrompt: boolean;
};

const die = (code: number, message: string): never => {
	process.stderr.write(`cold-review: ${message}\n`);
	process.exit(code);
};

const parseArgs = (argv: string[]): ParsedArgs => {
	const positionals: string[] = [];
	let model = DEFAULT_MODEL;
	let effort: ModelThinkingLevel = DEFAULT_EFFORT;
	let printPrompt = false;
	for (let i = 0; i < argv.length; i++) {
		const a = argv[i];
		if (a === "--print-prompt") {
			printPrompt = true;
		} else if (a === "--model") {
			const v = argv[++i];
			if (!v) die(2, "--model requires a value of the form provider/modelId");
			model = v;
		} else if (a.startsWith("--model=")) {
			model = a.slice("--model=".length);
		} else if (a === "--effort" || a.startsWith("--effort=")) {
			const v = a.startsWith("--effort=") ? a.slice("--effort=".length) : argv[++i];
			if (!v || !EFFORT_LEVELS.includes(v as ModelThinkingLevel)) {
				die(2, `--effort must be one of ${EFFORT_LEVELS.join("|")} (got '${v ?? ""}')`);
			}
			effort = v as ModelThinkingLevel;
		} else if (a.startsWith("--")) {
			die(2, `unknown flag: ${a}`);
		} else {
			positionals.push(a);
		}
	}
	if (positionals.length === 0) {
		die(2, "missing required argument: absolute path to the Q{n}-why.md artifact");
	}
	if (positionals.length > 1) {
		die(
			2,
			`exactly one positional argument is accepted (the artifact path); got ${positionals.length}: ${positionals.join(", ")}. ` +
				"The artifact path is the sole interface — extra arguments cannot be passed into the review.",
		);
	}
	if (!model.includes("/")) {
		die(2, `--model must be 'provider/modelId' (got '${model}')`);
	}
	return { artifactPath: positionals[0], model, effort, printPrompt };
};

const buildUserPrompt = (artifact: string): string =>
	["Artifact under review (verbatim):", "", artifact, "", "Review it per the three probes."].join("\n");

const buildFullPrompt = (artifact: string): string =>
	["=== SYSTEM ===", SYSTEM_PROMPT, "", "=== USER ===", buildUserPrompt(artifact)].join("\n");

const extractJson = (text: string): unknown => {
	const trimmed = text.trim();
	try {
		return JSON.parse(trimmed);
	} catch {
		/* fall through */
	}
	const start = trimmed.indexOf("{");
	const end = trimmed.lastIndexOf("}");
	if (start === -1 || end === -1 || end <= start) return undefined;
	try {
		return JSON.parse(trimmed.slice(start, end + 1));
	} catch {
		return undefined;
	}
};

const extractText = (content: unknown): string => {
	if (!Array.isArray(content)) return "";
	return content
		.filter(
			(b): b is { type: "text"; text: string } =>
				!!b && typeof b === "object" && (b as { type?: unknown }).type === "text" && typeof (b as { text?: unknown }).text === "string",
		)
		.map((b) => b.text)
		.join("\n");
};

type ReviewComponents = {
	confidence: number;
	probes: { under_climb: string; smell_test: string; direction_vs_destination: string };
	blocking_deficiencies: string[];
	l3_residue: string;
};

const validateComponents = (parsed: unknown): ReviewComponents | undefined => {
	if (!parsed || typeof parsed !== "object") return undefined;
	const p = parsed as Record<string, unknown>;
	const conf = p.confidence;
	if (typeof conf !== "number" || !Number.isInteger(conf) || conf < 1 || conf > 4) return undefined;
	const probes = p.probes as Record<string, unknown> | undefined;
	if (!probes || typeof probes !== "object") return undefined;
	const probeKeys = ["under_climb", "smell_test", "direction_vs_destination"] as const;
	const outProbes = {} as ReviewComponents["probes"];
	for (const k of probeKeys) {
		if (typeof probes[k] !== "string") return undefined;
		outProbes[k] = probes[k] as string;
	}
	const bd = p.blocking_deficiencies;
	if (!Array.isArray(bd) || bd.some((x) => typeof x !== "string")) return undefined;
	if (typeof p.l3_residue !== "string") return undefined;
	return { confidence: conf, probes: outProbes, blocking_deficiencies: bd as string[], l3_residue: p.l3_residue };
};

const main = async (): Promise<void> => {
	const { artifactPath, model: modelSpec, effort, printPrompt } = parseArgs(process.argv.slice(2));

	let artifact: string;
	try {
		artifact = await Bun.file(artifactPath).text();
	} catch (e) {
		return void die(2, `cannot read artifact at '${artifactPath}': ${e instanceof Error ? e.message : String(e)}`);
	}
	if (artifact.trim().length === 0) {
		return void die(2, `artifact at '${artifactPath}' is empty`);
	}

	if (printPrompt) {
		// Dry run: the prompt is built from ONLY the system contract and the artifact
		// file contents. Nothing from argv beyond the path, no env, no stdin.
		process.stdout.write(buildFullPrompt(artifact));
		process.exit(0);
	}

	const [provider, modelId] = [modelSpec.slice(0, modelSpec.indexOf("/")), modelSpec.slice(modelSpec.indexOf("/") + 1)];

	const auth = AuthStorage.create();
	const registry = ModelRegistry.create(auth);
	if (registry.getError()) {
		return void die(3, `model registry failed to load (~/.pi/agent/models.json): ${registry.getError()}`);
	}
	const model = registry.find(provider, modelId);
	if (!model) {
		return void die(3, `model '${modelSpec}' not found in the Pi registry (~/.pi/agent). Run 'pi' to configure it, or pass --model.`);
	}
	const resolved = await registry.getApiKeyAndHeaders(model as Model<Api>);
	if (!resolved.ok) {
		return void die(3, `no usable credential for '${modelSpec}': ${resolved.error}. Configure auth via 'pi' (~/.pi/agent/auth.json).`);
	}

	// Generation options. temperature 0 gives a review gate reproducible verdicts,
	// but OAuth-brokered endpoints (verified: openai-codex) reject `temperature` with
	// HTTP 400 "Unsupported parameter". Gate it on the registry's OAuth signal:
	// direct API-key providers (google, the anthropic proxy) get temperature 0 for
	// reproducibility; OAuth providers run at their default. Verified 2026-06-01.
	const resolvedEffort = clampThinkingLevel(model as Model<Api>, effort);
	const streamOpts: { apiKey?: string; headers?: Record<string, string>; temperature?: number; reasoning?: ThinkingLevel } = {
		apiKey: resolved.apiKey,
		headers: resolved.headers,
	};
	if (resolvedEffort !== "off") streamOpts.reasoning = resolvedEffort as ThinkingLevel;
	if (!registry.isUsingOAuth(model as Model<Api>)) streamOpts.temperature = 0;

	let result: Awaited<ReturnType<typeof completeSimple>>;
	try {
		result = await completeSimple(
			model as Model<Api>,
			{
				systemPrompt: SYSTEM_PROMPT,
				messages: [{ role: "user", content: [{ type: "text", text: buildUserPrompt(artifact) }], timestamp: Date.now() }],
			},
			streamOpts,
		);
	} catch (e) {
		return void die(4, `model call to '${modelSpec}' threw: ${e instanceof Error ? e.message : String(e)}`);
	}
	// complete() does NOT throw on a provider error — it returns a message with
	// stopReason "error". Surface that loudly with the real cause, rather than
	// letting empty content fall through to a misleading "bad JSON" report.
	if (result.stopReason === "error") {
		return void die(4, `model '${modelSpec}' returned an error: ${result.errorMessage ?? "(no message)"}`);
	}
	const responseText = extractText(result.content);
	if (responseText.trim().length === 0) {
		return void die(4, `model '${modelSpec}' returned no text content (stopReason=${result.stopReason}).`);
	}

	const components = validateComponents(extractJson(responseText));
	if (!components) {
		return void die(4, `reviewer response from '${modelSpec}' did not match the contract JSON. Raw response:\n${responseText}`);
	}

	// Deterministic verdict — computed here, not by the model.
	const verdict = components.confidence >= 4 && components.blocking_deficiencies.length === 0 ? "PASS" : "FAIL";
	process.stdout.write(`${JSON.stringify({ ...components, verdict, model: modelSpec, effort: resolvedEffort }, null, 2)}\n`);
	process.exit(0);
};

await main();
