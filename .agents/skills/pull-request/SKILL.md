---

name: pull-request
description: Generate a pull request title and description from the current branch changes compared with its base branch. Use when the user asks to create, draft, review, or format a pull request title or description. PR titles follow the project's Conventional Commits style and include the primary requirement ID when applicable. Do not create, submit, merge, or modify a pull request unless explicitly requested.
---

# Pull Request Generator

Generate a pull request title and description for the `todo-portfolio` project.

A pull request represents the complete logical change of the current branch.

Do not generate the PR only from the latest commit.

Do not create, submit, merge, close, or modify a pull request unless the user explicitly asks.

---

# Goal

Generate:

1. A concise PR title
2. A clear PR description
3. Requirement traceability where applicable

The result must accurately represent the changes between the current branch and the base branch.

The PR title must follow the project's Conventional Commits style.

When applicable, the PR title must also contain the primary requirement ID defined in `REQUIREMENTS.md`.

---

# Workflow

Follow these steps before generating pull request content.

## 1. Read project instructions

Read:

* `AGENTS.md`

Also read:

* `REQUIREMENTS.md`

when the branch changes may correspond to defined requirements.

If other project design documents such as `DESIGN.md` exist and are relevant to the change, they may also be consulted.

---

## 2. Determine the current branch

Check the current Git branch.

Example:

`git branch --show-current`

Do not assume that the current branch is `main`.

---

## 3. Determine the base branch

Use the branch specified by the user when provided.

Otherwise, use `main` as the expected base branch unless the repository state clearly indicates another base branch.

Do not silently choose a different base branch when this could materially change the PR diff.

---

## 4. Inspect branch commits

Inspect all commits included in the branch relative to the base branch.

Example:

`git log --oneline <base>..HEAD`

Use the commit history as supporting context.

Do not generate the PR title only from the newest commit.

---

## 5. Inspect the complete branch diff

Inspect the overall difference between the current branch and the base branch.

Examples:

`git diff <base>...HEAD --stat`

`git diff <base>...HEAD`

The branch diff is the primary source of truth for determining what the PR actually changes.

Do not describe functionality that is not present in the inspected diff.

---

## 6. Check repository state

Check whether there are uncommitted changes.

Example:

`git status --short`

Uncommitted changes are not normally part of the PR.

Do not include unstaged or uncommitted changes in the PR description unless the user explicitly asks for a draft that includes planned changes.

If uncommitted changes could affect interpretation of the branch, mention that they are excluded.

---

## 7. Identify the logical purpose

Determine the main logical purpose of the branch.

Examples:

* add user registration
* implement Todo CRUD
* fix authorization vulnerability
* define application requirements
* configure CI
* refactor authentication logic

The PR should normally represent one logical purpose.

---

## 8. Identify related requirements

When `REQUIREMENTS.md` exists:

1. Read the relevant requirements.
2. Identify requirement IDs actually addressed by the branch.
3. Select one primary requirement for the PR title when applicable.
4. Include all relevant requirement IDs in the PR description.

Do not invent requirement IDs.

Do not include a requirement merely because it is conceptually related.

There must be evidence in the branch changes that the requirement is being implemented, fixed, tested, documented, or otherwise addressed.

---

# Pull Request Title

Use the following format when a requirement applies:

`<type>[optional scope]: [requirement-id] <description>`

Example:

`feat(auth): [REQ-F-001] implement user registration`

When no requirement applies:

`<type>[optional scope]: <description>`

Example:

`chore(repo): add pull request generation skill`

---

# Conventional Commit Style

The PR title uses the project's Conventional Commits style.

Use:

* `feat`
* `fix`
* `docs`
* `test`
* `refactor`
* `style`
* `perf`
* `build`
* `ci`
* `chore`

Select the type based on the main purpose of the PR.

Do not mechanically select the type based on which commit type appears most often.

---

# Type Rules

## feat

Use for new or expanded user-facing functionality.

Examples:

`feat(auth): [REQ-F-001] implement user registration`

`feat(todo): [REQ-F-004] add Todo creation`

---

## fix

Use for correcting incorrect application behavior.

Example:

`fix(todo): [REQ-SEC-002] prevent cross-user Todo access`

---

## docs

Use for documentation-only changes.

Example:

`docs(requirements): [REQ-P-001] define application requirements`

---

## test

Use when the PR only adds or modifies tests without changing application behavior.

Example:

`test(auth): [REQ-T-005] add authorization tests`

---

## refactor

Use for internal code restructuring that does not add functionality or fix incorrect behavior.

---

## style

Use only for code formatting or other changes that do not affect behavior.

Do not use `style` for CSS or UI changes that alter appearance or functionality.

---

## perf

Use for performance improvements.

---

## build

Use for build configuration or dependency-related changes.

Examples:

* package configuration
* Python dependency configuration
* Docker build configuration

---

## ci

Use for CI/CD changes.

Example:

`ci: [REQ-T-009] run backend tests on pull requests`

---

## chore

Use for repository maintenance that does not fit a more specific category.

Prefer a more specific type such as `docs`, `build`, `test`, or `ci` when appropriate.

---

# Scope

Use a scope only when it improves clarity.

Preferred scopes for this project:

* `frontend`
* `backend`
* `auth`
* `todo`
* `db`
* `api`
* `docs`
* `docker`
* `ci`
* `repo`

Do not force a scope for broad project-wide changes.

---

# Requirement ID Position

Requirement IDs must appear after the Conventional Commit prefix.

Correct:

`feat(auth): [REQ-F-001] implement user registration`

Incorrect:

`[REQ-F-001] feat(auth): implement user registration`

This preserves the `<type>[optional scope]: <description>` structure.

---

# Primary Requirement ID

Normally include only one requirement ID in the PR title.

The PR description should contain the full set of related requirement IDs.

This keeps the PR title readable.

Example:

PR title:

`feat(auth): [REQ-F-001] implement user authentication`

PR description:

* `REQ-F-001`
* `REQ-F-002`
* `REQ-F-003`
* `REQ-SEC-001`
* `REQ-SEC-004`
* `REQ-T-005`

---

# Requirement ID Priority

When multiple requirement IDs apply, choose the primary requirement based on the main purpose of the PR.

Use the following guidance.

1. Primary functional requirement (`REQ-F`)
2. Primary security requirement (`REQ-SEC`) when security is the main purpose
3. Primary non-functional requirement (`REQ-NF`)
4. Test requirement (`REQ-T`) for test-only PRs
5. Operations requirement (`REQ-OPS`) for infrastructure or deployment-focused PRs
6. Project or documentation requirement when no implementation requirement is more appropriate

Do not select a requirement merely because it appears first in `REQUIREMENTS.md`.

Select the requirement that best represents the purpose of the PR.

---

# Multiple Requirement IDs

If multiple requirements are inseparable and no single requirement adequately represents the PR, multiple IDs may be included.

Example:

`feat(auth): [REQ-F-001][REQ-F-002] implement account authentication`

However, prefer one primary requirement whenever possible.

Avoid titles such as:

`feat(auth): [REQ-F-001][REQ-F-002][REQ-SEC-001][REQ-SEC-004][REQ-T-005] implement authentication`

The complete requirement list belongs in the PR description.

---

# Pull Request Description

Use the following structure.

## Summary

Explain what the PR accomplishes and why the change exists.

Focus on the overall purpose rather than individual files.

Keep this concise.

---

## Changes

Describe the meaningful changes introduced by the branch.

Prefer behavior and architecture changes over file-by-file descriptions.

Good:

* Added user registration with username and password
* Added password validation
* Prevented duplicate usernames
* Added registration error handling

Avoid:

* Changed `router.py`
* Changed `service.py`
* Changed `test_auth.py`

unless specific file-level information is genuinely important.

---

## Testing

Describe tests that were actually executed.

Examples:

* `pytest`
* frontend unit tests
* integration tests
* manual browser verification
* Docker startup verification

Do not claim that tests passed unless there is evidence that they were executed successfully.

If tests were not run, write:

`Not run`

If only some tests were run, state exactly which tests were run.

Do not infer test execution from the existence of test files.

---

## Related Requirements

List all relevant requirement IDs actually addressed by the branch.

When possible, include a short description.

Example:

* `REQ-F-001` - User registration
* `REQ-SEC-004` - Passwords must not be stored in plain text
* `REQ-T-002` - Invalid input must be tested

Do not invent requirement IDs.

Do not list requirements that are not addressed by the branch.

If no requirement applies, omit this section or write:

`None`

---

## Notes

Include this section only when reviewers should know something important.

Examples:

* known limitations
* intentionally deferred functionality
* migration considerations
* follow-up work
* deployment considerations
* free-tier hosting limitations

Do not include an empty Notes section.

---

# PR Description Template

Normally generate the PR body in this format:

```markdown
## Summary

<summary>

## Changes

- <change>
- <change>

## Testing

- <test or verification>

## Related Requirements

- `<requirement-id>` - <description>

## Notes

<optional notes>
```

Omit optional sections when they contain no useful information.

---

# Multiple Commits

A PR may contain several commits.

Treat the complete branch as one logical unit.

Example commits:

`feat(auth): add registration`

`feat(auth): add login`

`test(auth): add authentication tests`

`docs(auth): document authentication behavior`

Possible PR title:

`feat(auth): [REQ-F-001] implement user authentication`

Do not simply copy the newest commit message.

Do not concatenate commit messages to form the title.

Summarize the purpose of the complete branch.

---

# Unrelated Changes

If the branch contains multiple unrelated logical changes:

1. Do not hide the problem with an overly broad PR title.
2. Explain that the branch may be too broad for one PR.
3. Identify logical groups of changes.
4. Suggest how the branch could be split.
5. Generate a proposed PR title for each logical group when useful.

Example:

Branch contains:

* user authentication
* Todo filtering
* GitHub Actions changes

Possible recommendation:

PR 1:

`feat(auth): [REQ-F-001] implement user authentication`

PR 2:

`feat(todo): [REQ-F-012] add Todo status filtering`

PR 3:

`ci: [REQ-T-009] add automated application tests`

Do not automatically modify Git history.

Do not automatically reset, rebase, cherry-pick, or split commits.

---

# Breaking Changes

Only mark a PR as a breaking change when the inspected branch actually introduces an incompatible behavior or interface change.

Use:

`feat(api)!: [REQ-F-004] change Todo response schema`

Do not infer breaking changes without evidence.

Explain the breaking behavior clearly in the PR description.

---

# Test Accuracy

Never write:

`All tests pass`

unless there is evidence that the relevant test command was executed successfully.

Prefer precise wording.

Examples:

`pytest: passed`

`Frontend unit tests: passed`

`Manual browser verification: not run`

When execution evidence is unavailable:

`Not run`

---

# Requirement Traceability

The PR should help trace:

Requirement

→ Design

→ Implementation

→ Tests

→ Pull Request

When applicable, use the requirement IDs from `REQUIREMENTS.md` consistently.

The PR title contains the primary requirement ID.

The PR description contains all requirements meaningfully addressed by the change.

---

# Output Format

When both title and description are requested, output:

## PR Title

`<title>`

## PR Description

```markdown
## Summary

...

## Changes

- ...

## Testing

- ...

## Related Requirements

- ...

## Notes

...
```

When the user requests only the title, output only the title.

When the user requests only the description, output only the description.

---

# Safety Rules

Do not execute:

* `git commit`
* `git push`
* `git rebase`
* `git reset`
* `git merge`
* `gh pr create`
* `gh pr merge`
* any command that creates or modifies a remote pull request

unless the user explicitly requests that action.

Generating PR content does not imply permission to create the PR.

When only asked to generate PR content, inspect the repository and return the proposed content without modifying Git state or GitHub.
