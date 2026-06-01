#!/usr/bin/env bash
# Ensure the triage cold-review reviewer's npm dependencies are installed in the
# plugin's PERSISTENT data dir (${CLAUDE_PLUGIN_DATA}), which survives plugin
# updates — unlike ${CLAUDE_PLUGIN_ROOT}, the read-only, per-version plugin cache.
#
# Invoked from a SessionStart hook (see hooks/hooks.json). Installs only when the
# bundled package.json differs from the copy in the data dir (a cheap diff in steady
# state; a one-time `bun install` on first run or after a dependency-manifest change).
# The reviewer (skills/triage/scripts/cold-review.ts) resolves these deps via
# NODE_PATH="${CLAUDE_PLUGIN_DATA}/node_modules". See ADR-002.
#
# Never blocks session start: always exits 0. If bun is absent, the env vars are
# unset, or the install fails, this no-ops (removing the cached manifest so the next
# session retries) and the reviewer itself fails closed and loud at invocation time.

set -u

# Outside a plugin runtime (no env vars) — nothing to do.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -n "${CLAUDE_PLUGIN_DATA:-}" ] || exit 0

SRC="${CLAUDE_PLUGIN_ROOT}/skills/triage/scripts"
DST="${CLAUDE_PLUGIN_DATA}"

[ -f "${SRC}/package.json" ] || exit 0
mkdir -p "${DST}" 2>/dev/null || exit 0

# Already in sync — nothing to install.
if diff -q "${SRC}/package.json" "${DST}/package.json" >/dev/null 2>&1; then
	exit 0
fi

# Manifest changed (or first run): (re)install into the data dir.
if command -v bun >/dev/null 2>&1 && cp "${SRC}/package.json" "${DST}/package.json" 2>/dev/null; then
	# Carry the lockfile for a reproducible install when present.
	[ -f "${SRC}/bun.lock" ] && cp "${SRC}/bun.lock" "${DST}/bun.lock" 2>/dev/null
	if ! (cd "${DST}" && bun install >/dev/null 2>&1); then
		# Install failed: drop the marker so the next session retries.
		rm -f "${DST}/package.json" 2>/dev/null
	fi
fi

exit 0
