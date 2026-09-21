---
name: conventional-commit
description: Generate a Conventional Commits 1.0.0 compliant Git commit message from the current repository changes. Use when the user asks to create, suggest, review, or format a commit message. Do not create the commit unless the user explicitly asks to commit.
---

# Conventional Commit Message Generator

Generate a Git commit message that follows Conventional Commits 1.0.0.

This skill is intended for the todo-portfolio project.

## Goal

Inspect the changes that are going to be committed and generate a concise,
accurate Conventional Commit message.

Do not execute `git commit` unless the user explicitly asks you to commit.

## Workflow

1. Read `AGENTS.md` before generating the message.
2. Check the current Git state with:

   `git status --short`

3. Prefer staged changes as the source of truth.

   Inspect staged changes with:

   `git diff --cached --stat`
   `git diff --cached`

4. If staged changes exist, generate the commit message only from staged changes.

5. If no changes are staged:
   - inspect `git diff --stat` and `git diff`;
   - clearly state that the proposed message is based on unstaged changes;
   - do not stage files automatically unless explicitly requested.

6. Determine the main purpose of the change.

7. Select the most appropriate Conventional Commit type.

8. Add a scope only when it provides useful context.

9. Generate the final commit message.

10. Do not include changes that are not actually present in the inspected diff.

## Commit format

Use:

`<type>[optional scope]: <description>`

Optional body:

`<type>[optional scope]: <description>`

`<blank line>`

`<body>`

Optional footer:

`BREAKING CHANGE: <description>`

For a breaking change, `!` may also be used:

`<type>[optional scope]!: <description>`

## Allowed types

Use the following types for this project.

### feat

Use when adding new user-facing functionality.

Examples:
- user authentication
- Todo creation
- Todo filtering
- responsive UI feature

### fix

Use when fixing incorrect behavior or a bug.

Examples:
- authentication failure
- incorrect Todo status
- broken validation

### docs

Use when changing only documentation.

Examples:
- README
- REQUIREMENTS.md
- DESIGN.md
- documentation comments that do not affect behavior

### test

Use when adding or changing tests without changing application behavior.

### refactor

Use for internal code changes that do not add a feature or fix a bug.

### style

Use only for formatting changes that do not affect behavior.

Examples:
- whitespace
- code formatting

Do not use `style` for CSS or visual UI changes that alter appearance or behavior.
Use `feat`, `fix`, or `refactor` when appropriate instead.

### perf

Use for performance improvements.

### build

Use for changes to the build system or dependencies.

Examples:
- package dependencies
- Python dependencies
- Docker build configuration

### ci

Use for CI/CD configuration.

Examples:
- GitHub Actions workflows
- CI test configuration

### chore

Use for repository maintenance that does not fit another type.

Examples:
- repository configuration
- development tooling
- miscellaneous maintenance

Prefer a more specific type such as `docs`, `build`, `ci`, or `test`
instead of `chore` when one applies.

## Recommended scopes

Use a scope only when it makes the message clearer.

Preferred scopes for this project:

- `frontend`
- `backend`
- `auth`
- `todo`
- `db`
- `api`
- `docs`
- `docker`
- `ci`
- `repo`

Examples:

`feat(todo): add Todo creation form`

`fix(auth): reject invalid login credentials`

`docs(requirements): define MVP requirements`

`test(api): add Todo authorization tests`

`ci: run backend tests on pull requests`

Scope is optional. Do not force a scope when the change affects the project broadly.

## Description rules

The description must:

- be written in English;
- summarize the primary purpose of the commit;
- be concise;
- use lowercase immediately after the colon where natural;
- use the imperative style where practical;
- not end with a period;
- avoid vague phrases such as:
  - update files
  - miscellaneous changes
  - fix stuff
  - changes
  - modify code

Prefer:

`docs(requirements): define MVP requirements`

instead of:

`docs: update files`

## Multiple changes

A single commit should represent one logical purpose.

If the staged changes contain multiple unrelated purposes:

1. Do not create a misleading combined message.
2. Explain that the changes should preferably be split into separate commits.
3. Suggest how to group the files.
4. Generate a proposed Conventional Commit message for each group.

If the changes are closely related to one purpose, use one message describing
the primary purpose.

## Breaking changes

Only mark a commit as a breaking change when the inspected changes actually
introduce an incompatible behavior or interface change.

Use either:

`feat(api)!: change Todo response format`

or a footer:

`BREAKING CHANGE: Todo API responses now use a different schema.`

Never infer a breaking change without evidence.

## Output format

Normally output:

### Recommended

`<commit message>`

### Reason

Briefly explain why the selected type and scope match the changes.

If useful, provide at most two alternatives.

Do not execute `git commit`.

If the user explicitly asks for only the commit message, output only the
commit message with no explanation.