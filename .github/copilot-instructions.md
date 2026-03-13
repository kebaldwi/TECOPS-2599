# GitHub Copilot Instructions

## Shell / Terminal Guidelines

### Multi-line commit messages
**Never use heredocs (`<<'EOF' ... EOF`) for git commit messages.** The zsh terminal in this workspace mangles them.

**Always write multi-line messages to a temp file and use `git commit -F`:**
```bash
printf '%s\n' \
  'subject line' \
  '' \
  'Body paragraph one.' \
  '' \
  '- bullet one' \
  '- bullet two' \
  > /tmp/commit-msg.txt

git commit -F /tmp/commit-msg.txt
```

Or use `create_file` to write `/tmp/<name>-commit-msg.txt`, then:
```bash
git commit -F /tmp/<name>-commit-msg.txt
```

### Multi-line shell strings in general
Avoid any construct that opens an interactive continuation prompt (`dquote>`, `heredoc>`).
- For multi-line strings: write to a temp file with `create_file`, then read the file.
- For commit messages: always use `-F <file>`, never `-m` with embedded newlines.
- Never combine `-m` and `-F` flags on the same `git commit` invocation.

### Command chaining
Chain independent steps with `&&` on a single line. For complex sequences that require
multi-line messages, split into: (1) write temp file, (2) run command referencing the file.
