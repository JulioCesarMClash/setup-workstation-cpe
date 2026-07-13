---
name: using-git-worktrees
description: >
  Isolated parallel development using git worktrees. Use when working on
  multiple branches simultaneously without stash/checkout friction, or when
  you need FS-level isolation between feature branches. Adapted for
  CORE_DAILY_TASKS_POLICY: worktree paths always outside any git repo tree.
---

Use git worktrees for branch isolation. Never create a worktree inside an
existing git repo directory — put it in ~/Developer/worktrees/<name>.

## When to use

- Working on two features at the same time without losing context
- Running tests on branch A while coding on branch B
- Preparing a hotfix while mid-feature
- Pre-Odysseus: parallel agent tasks that need FS isolation

## Steps

1. **Create worktree** outside any git repo:
   ```bash
   git worktree add ~/Developer/worktrees/<branch-name> <branch>
   # New branch:
   git worktree add ~/Developer/worktrees/<branch-name> -b <branch>
   ```

2. **Work in isolation** — each worktree has its own working tree, index,
   and HEAD. Changes don't bleed between worktrees.

3. **List active worktrees:**
   ```bash
   git worktree list
   ```

4. **Remove when done:**
   ```bash
   git worktree remove ~/Developer/worktrees/<branch-name>
   ```

## Constraints (CORE_DAILY_TASKS_POLICY)

- Worktree path: `~/Developer/worktrees/<name>` — never inside a git repo
- No ad-hoc scripts created inside worktree dirs
- Worktrees for the same repo share `.git` — do not delete `.git` in main

## Triggers

- "trabajo en paralelo", "dos branches a la vez", "no quiero hacer stash"
- "aísla esto", "worktree", "isolation"
- Odysseus parallel tasks that need separate working trees
