---
name: mcp-builder
description: >
  Design, configure, and debug MCP (Model Context Protocol) servers and their
  client configs. Use when adding or fixing an MCP server in
  `~/.codex/config.toml` or `~/.claude/mcp/*.json`, filtering exposed tools
  with `enabled_tools`, debugging a server that won't connect or exposes too
  many tools, or designing a new MCP server's tool surface. Trigger on "mcp",
  "add mcp server", "enabled_tools", "mcp config", "server won't connect",
  "tool filtering".
license: MIT
metadata:
  tier: CRITICAL
---

# mcp-builder

## 1. Canonical Config Shapes & Mapping

**Codex (`~/.codex/config.toml`)**
```toml
[mcp_servers.server_name]
command = "node"
args = ["/path/to/server.js"]
env = { API_KEY = "value" }
enabled_tools = ["tool_a", "tool_b"]
```

**Claude Code (`~/.claude/mcp/server_name.json`)**
```json
{
  "command": "node",
  "args": ["/path/to/server.js"],
  "env": { "API_KEY": "value" },
  "enabled_tools": ["tool_a", "tool_b"]
}
```

| Codex (TOML) | Claude Code (JSON) | Purpose |
|---|---|---|
| `[mcp_servers.id]` | filename `{id}.json` | server identifier |
| `command` | `command` | executable/runtime |
| `args` | `args` | CLI arguments array |
| `env` | `env` | environment variable map |
| `enabled_tools` | `enabled_tools` | tool allowlist filter |

## 2. enabled_tools filtering recipe

1. **Discover**: list every tool the server exposes (run verbose, or read its source/docs).
2. **Sieve**: identify the minimal set of tools the actual use case needs.
3. **Apply**: put only those names in `enabled_tools`.
4. **Verify**: confirm the agent can no longer see/call excluded tools.

Example — server `postgres-mcp` exposes 20 tools, use case is read-only reporting → allowlist `["query_read", "list_tables", "describe_table"]`.

## 3. Connection-failure triage ladder

Walk this in order, stop at the first hit:

1. **Binary path** — does `command` resolve in a plain shell? Use absolute paths if unsure.
2. **Args** — quoting/spacing correct for the runtime?
3. **CWD** — does the server need a specific working directory for relative imports?
4. **Env** — are all required env vars present and exported?
5. **Transport** — stdio/SSE behaving? Check the server's own stderr/logs for stray prints corrupting the stream.
6. **Permissions** — execute rights on the binary, read rights on the config file?

## 4. Tool-surface design rule (Ponytail applied to MCP)

Expose the fewest tools that satisfy the requirement. A larger toolset costs more prompt tokens and raises the odds the model picks the wrong tool. Don't expose a tool "in case it's useful later."

## 5. Federation sync checklist

When a server is shared by both Codex and Claude (e.g. Engram, Obsidian):

- [ ] Update `~/.codex/config.toml` AND `~/.claude/mcp/{id}.json` together — never just one.
- [ ] `env` values identical in both.
- [ ] `enabled_tools` allowlist identical in both, unless one agent genuinely needs a narrower set.
- [ ] Test connectivity in both after the change.

## 6. Hard rule — diff before write

Never silently overwrite a working config.

1. Read the existing config.
2. Draft the proposed change.
3. Show the diff (old vs new) to the user.
4. Only write after explicit confirmation.
