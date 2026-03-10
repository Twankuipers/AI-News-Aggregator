# Workspace Instructions

## Git Commits — Conventional Commits

Always use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for every commit message and push to GitHub.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type       | When to use                                                         |
|------------|---------------------------------------------------------------------|
| `feat`     | A new feature                                                       |
| `fix`      | A bug fix                                                           |
| `docs`     | Documentation-only changes                                          |
| `style`    | Formatting, missing semicolons, etc. — no logic change              |
| `refactor` | Code change that neither fixes a bug nor adds a feature             |
| `perf`     | A code change that improves performance                             |
| `test`     | Adding or correcting tests                                          |
| `build`    | Changes to build system or external dependencies                    |
| `ci`       | Changes to CI/CD configuration files and scripts                    |
| `chore`    | Other changes that don't modify src or test files                   |
| `revert`   | Reverts a previous commit                                           |

### Rules

- The **description** must be lowercase, imperative mood, and not end with a period.
- The **body** (if present) must be separated from the description by a blank line.
- **Breaking changes** must include `BREAKING CHANGE:` in the footer, or append `!` after the type/scope (e.g., `feat!: drop support for Python 3.8`).
- Scope is optional but encouraged when the change is limited to a specific module or file (e.g., `fix(scheduler): correct cron expression`).

### Examples

```
feat(agent): add RSS feed source support

fix(config): handle missing api_key gracefully

docs: update README with scheduler setup instructions

chore: add seen_items.json to .gitignore

feat!: replace output format from txt to html only

BREAKING CHANGE: txt digest files are no longer generated
```

### What NOT to do

- Do not use vague messages like `fix stuff`, `update`, `wip`, or `changes`.
- Do not mix unrelated changes in a single commit — keep commits focused and atomic.
- Do not use past tense (`fixed`, `added`) — use imperative (`fix`, `add`).
