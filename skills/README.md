# skill-creator

A skill for creating, evaluating, and iteratively improving Claude Code skills. This is the domain-chassis version, distinct from the Anthropic-provided skill-creator that ships with Cowork/Claude.ai.

## What it does

The skill-creator operates in four modes: Create (interactive skill authoring), Eval (single eval testing), Improve (iterative optimization with blind A/B comparison), and Benchmark (standardized multi-run measurement with variance analysis). It uses composable building blocks — executor, grader, comparator, analyzer — that can run as independent subagents or inline sequentially.

The full workflow and mode details live in `SKILL.md`. This README covers the file inventory and the description optimizer, which is the piece most likely to be non-obvious when you come back to this later.


## File inventory

```text
skill-creator/
├── SKILL.md                        # Main skill prompt (coordinator instructions)
├── README.md                       # This file
├── LICENSE.txt
│
├── agents/                         # Subagent prompts (building blocks)
│   ├── executor.md                 # Runs a skill on an eval, produces transcript + outputs
│   ├── grader.md                   # Grades expectations against outputs
│   ├── comparator.md               # Blind A/B comparison between two outputs
│   └── analyzer.md                 # Post-hoc analysis of comparison results
│
├── references/                     # Extended documentation (progressive disclosure)
│   ├── eval-mode.md                # Eval mode workflow details
│   ├── benchmark-mode.md           # Benchmark mode workflow details
│   ├── mode-diagrams.md            # Visual workflow diagrams
│   └── schemas.md                  # JSON schemas for grading, history, comparison, etc.
│
├── assets/
│   └── eval_review.html            # Browser-based eval set editor for description optimization
│
└── scripts/
    ├── __init__.py                 # Enables cross-script imports (from scripts.x import y)
    ├── utils.py                    # Shared: parse_skill_md() frontmatter parser
    │
    │   # --- Core skill-creator scripts ---
    ├── init_skill.py               # Scaffold a new skill directory
    ├── init_json.py                # Initialize evals.json, history.json with correct schema
    ├── validate_json.py            # Validate JSON files against schemas
    ├── copy_skill.py               # Copy skill to versioned workspace directory
    ├── prepare_eval.py             # Prepare eval inputs for execution
    ├── quick_validate.py           # Quick validation of skill outputs
    ├── package_skill.py            # Package skill as .skill zip for distribution
    ├── aggregate_benchmark.py      # Aggregate benchmark results across runs
    │
    │   # --- Description optimizer (ported from Anthropic's skill-creator) ---
    ├── run_eval.py                 # Test whether a description triggers correctly
    ├── improve_description.py      # Use Claude + extended thinking to propose better descriptions
    ├── run_loop.py                 # Outer loop: eval → improve → re-eval → pick best
    └── generate_report.py          # HTML report generator for optimization runs
```


## Description optimizer

The description optimizer tests whether a skill's SKILL.md description causes Claude to invoke the skill for a set of queries, then iteratively rewrites the description to improve accuracy. It was ported from Anthropic's skill-creator, adapted to work standalone with PEP 723 metadata.

### How it works

The optimizer creates temporary command files in `.claude/commands/`, fires `claude -p` with `--stream-json --include-partial-messages`, and detects triggering by watching for `Skill` or `Read` tool_use events in the stream output. It uses `ProcessPoolExecutor` for parallel query evaluation and removes the `CLAUDECODE` env var to allow nesting `claude -p` inside an active Claude Code session.

Each iteration evaluates the current description against a train set (3 runs per query for reliability), passes failures to Claude with extended thinking to propose a rewrite, then re-evaluates. A held-out test set (40% by default, stratified by `should_trigger`) prevents overfitting — the best description is selected by test score, not train score. Descriptions exceeding 1024 characters are automatically shortened via a follow-up API call.

### Prerequisites

Requires `claude` CLI on PATH (Claude Code) and either `uv` or `pip install anthropic>=0.40`. The scripts have PEP 723 inline metadata so `uv run` handles the anthropic dependency automatically with no separate install step.

### Invocation

From the skill-creator directory (or anywhere with `scripts/` on the Python path):

```bash
python -m scripts.run_loop \
  --eval-set trigger-eval.json \
  --skill-path /path/to/your-skill \
  --model claude-sonnet-4-5-20250514 \
  --max-iterations 5 \
  --runs-per-query 3 \
  --holdout 0.4 \
  --verbose
```

This opens a live auto-refreshing HTML report showing each iteration's train/test results. When complete, it prints JSON with `best_description`, `best_score`, and full history.

### Key parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `--eval-set` | required | Path to JSON array of `{query, should_trigger}` objects |
| `--skill-path` | required | Path to skill directory containing SKILL.md |
| `--model` | required | Model ID for the improvement calls (not the eval model) |
| `--max-iterations` | 5 | Stop after N iterations even if not perfect |
| `--runs-per-query` | 3 | Runs per query per iteration (higher = more reliable, slower) |
| `--trigger-threshold` | 0.5 | Fraction of runs that must trigger for a "triggered" verdict |
| `--holdout` | 0.4 | Fraction held out for test (0 to disable train/test split) |
| `--report` | auto | HTML report path (auto = temp file, none = disable) |
| `--results-dir` | none | Save results.json + report.html + logs to timestamped subdir |
| `--num-workers` | 10 | Parallel `claude -p` processes |

### Eval set format

```json
[
  {"query": "create a skill for formatting markdown tables", "should_trigger": true},
  {"query": "what time is it in Tokyo", "should_trigger": false},
  {"query": "improve my pdf-generator skill's description", "should_trigger": true},
  {"query": "help me write a bash script to rename files", "should_trigger": false}
]
```

Queries should be realistic user prompts. The most valuable negative examples are near-misses that share keywords but need something different. The `assets/eval_review.html` template provides a browser UI for curating these — see the "Description Optimization" section in SKILL.md for the full workflow.

### Individual scripts

You can also run the components independently:

```bash
# Just evaluate (no improvement)
python -m scripts.run_eval \
  --eval-set trigger-eval.json \
  --skill-path /path/to/skill \
  --verbose

# Just improve (given eval results)
python -m scripts.improve_description \
  --eval-results eval-output.json \
  --skill-path /path/to/skill \
  --model claude-sonnet-4-5-20250514

# Just generate report (given loop output)
python -m scripts.generate_report results.json -o report.html
```


## Integration with the Range

The skill-creator's `evals.json` schema is the source format that the Range's promotion path consumes. The `promote_evals.py` script in `workshop/the-range/scripts/` converts skill-creator evals into Range scenarios, mapping assertions to anchors with inferred methods and weights. Flow is one-directional: skill-creator evals graduate to Range scenarios, not the other way around.

The Range's MCP server and Observer Dashboard handle eval viewing, trajectory inspection, and run comparison — the description optimizer's HTML report is a self-contained alternative for quick description-specific work that doesn't need the full Range stack.
