# Writing Checks for review_docs

This guide covers everything you need to add a new check to the
documentation review tool. It focuses on the interfaces and data
structures available to check authors.

## Quick start

1. Choose a scope (see [Scopes](#scopes)).
2. Write a function with the matching signature.
3. Decorate it with `@register_check(name, severity, scope)`.
4. Place it in the appropriate module under `checks/`.
5. If the module is new, import it in `checks/__init__.py`.
6. Add a commented-out entry to `.review-docs.conf`.

That is all. The engine discovers checks automatically at import time
through the decorator — no wiring, no manual registration.

---

## The `@register_check` decorator

```python
from ..registry import register_check
from ..config import Config
from ..models import FileResult, ParseState

@register_check("my-check", "warning", "prose")
def check_something(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None:
    ...
```

**Parameters:**

| Parameter  | Type   | Description |
|------------|--------|-------------|
| `name`     | `str`  | Unique identifier, kebab-case (e.g. `"my-new-check"`). Used in CLI flags, config file, and findings output. |
| `severity` | `str`  | Default severity: `"error"` or `"warning"`. Users can override this in `.review-docs.conf` or via `--disable`. |
| `scope`    | `str`  | Determines when the engine calls your function. One of: `"prose"`, `"code_block_line"`, `"code_block_boundary"`, `"code_block_complete"`, `"structural"`. |

The decorator validates your function's parameter names against the
expected signature for the given scope. If they don't match, a
`TypeError` is raised at import time — you'll see it immediately.

---

## Scopes

Each scope corresponds to a different point in the engine's line-by-line
state machine. Choose the scope that matches what your check needs to
inspect.

### `prose`

**When it runs:** On every line that is outside a code block, outside a
block delimiter, and not a comment (`//`).

**Signature:**

```python
def check_name(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None
```

Most checks are prose checks. Use this scope for anything that examines
documentation text: style, formatting, terminology, heading structure.

### `code_block_line`

**When it runs:** On every line *inside* a `----`-delimited code block
(not including the delimiter lines themselves).

**Signature:** Same as `prose`.

The `state.code_block_lang` attribute tells you the language from the
`[source,lang]` specifier. Use it to limit your check to specific
languages:

```python
@register_check("yaml-something", "warning", "code_block_line")
def check_yaml_something(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None:
    if state.code_block_lang != "yaml":
        return
    # ... inspect line ...
```

Use this scope for checks that need to examine individual lines (e.g.,
detecting specific patterns, validating line-level syntax).

### `code_block_boundary`

**When it runs:** Once each time a `----` delimiter is encountered
(both opening and closing).

**Signature:** Same as `prose`.

Use `state.boundary_direction` to distinguish:

- `"open"` — the `----` that starts a code block
- `"close"` — the `----` that ends a code block

On open, `state.prev_line` contains the line immediately before the
delimiter — typically the `[source,lang]` attribute, which you can
inspect.

### `code_block_complete`

**When it runs:** Once per code block, when the closing `----` delimiter
is encountered. Receives the accumulated block content and following
annotation lines.

**Signature:**

```python
def check_name(
    block_content: list[str],
    block_lang: str,
    block_start_line: int,
    block_end_line: int,
    following_annotations: list[str],
    block_attrs: dict[str, str],
    cfg: Config,
    file_result: FileResult,
) -> None
```

**Parameters:**

| Parameter               | Type              | Description |
|-------------------------|-------------------|-------------|
| `block_content`         | `list[str]`       | All lines inside the code block (excluding the `----` delimiters). |
| `block_lang`            | `str`             | Language from `[source,lang]`, or `""` if none. |
| `block_start_line`      | `int`             | Line number of the opening `----`. |
| `block_end_line`        | `int`             | Line number of the closing `----`. |
| `following_annotations` | `list[str]`       | Annotation lines immediately after the block (lines matching `^<(\d+|\.)>\s`). Engine stops at the first blank line or non-annotation line after the block. |
| `block_attrs`           | `dict[str, str]`  | Named attributes parsed from the block-open attribute list, e.g. `[source,yaml,allow-duplicate-callouts]` → `{"source": "", "yaml": "", "allow-duplicate-callouts": ""}`. Bare attributes and `key=value` pairs are both captured; bare attributes get an empty-string value. |
| `cfg`                   | `Config`          | Configuration object. |
| `file_result`           | `FileResult`      | Result accumulator. |

Use this scope for checks that need:
- The complete block content (e.g., YAML validation, shell syntax)
- To validate callouts against annotations
- To analyze patterns across multiple lines in a block

**Example:**

```python
@register_check("yaml-validation", "error", "code_block_complete")
def check_yaml_validation(
    block_content: list[str],
    block_lang: str,
    block_start_line: int,
    block_end_line: int,
    following_annotations: list[str],
    block_attrs: dict[str, str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Validate YAML syntax in code blocks."""
    if block_lang != "yaml":
        return
    
    import yaml
    yaml_content = "\n".join(block_content)
    
    try:
        yaml.safe_load(yaml_content)
    except Exception:
        file_result.add_finding(
            cfg,
            "yaml-validation",
            block_start_line,
            f"line {block_start_line}: Invalid YAML syntax in code block",
        )
```

### `structural`

**When it runs:** Once per file, after all line-by-line processing is
complete. Receives the full file content.

**Signature:**

```python
def check_name(filepath: str, lines: list[str], cfg: Config, file_result: FileResult) -> None
```

Use this for checks that need the whole file: validating required
sections exist, cross-referencing with the filesystem, parsing
multi-line constructs that span the entire document.

---

## Choosing between code block scopes

There are three scopes for code block checks. Here's when to use each:

| Scope | Use when... | Example checks |
|-------|-------------|----------------|
| `code_block_line` | You need to examine individual lines inside code blocks | `callout-format`, `yaml-null-timestamps`, `yaml-flow-syntax` |
| `code_block_boundary` | You need to validate the opening or closing delimiter | `code-block-language` (checks for `[source,lang]` attribute) |
| `code_block_complete` | You need the full block content or following annotations | `yaml-validation`, `callout-count`, JSON/shell syntax validation |

**Rule of thumb:**
- If your check can fire on a single line → `code_block_line`
- If your check needs to validate the whole block → `code_block_complete`
- If your check validates the `[source,lang]` attribute → `code_block_boundary`

The engine handles all the code block parsing for you — accumulating
content, detecting language, capturing annotations. You just pick the
right scope and receive pre-parsed data.

---

## Data structures

### `ParseState`

The engine maintains a single `ParseState` instance per file and passes
it to every line-level check. It carries the parser's current position
and context.

**Attributes you can read:**

| Attribute              | Type         | Description |
|------------------------|--------------|-------------|
| `prev_line`            | `str`        | The previous line's text. Set by the engine at the end of each iteration. |
| `in_code_block`        | `bool`       | Whether we are currently inside a `----` code block. Convenience property — equivalent to `in_block("code_block")`. |
| `code_block_lang`      | `str`        | Language from `[source,lang]`, or `""` if none. Only meaningful when `in_code_block` is `True`. |
| `code_block_start_line`| `int`        | Line number of the opening `----`. |
| `boundary_direction`   | `str`        | `"open"` or `"close"` — only meaningful inside `code_block_boundary` checks. |
| `heading_levels`       | `list[int]`  | Stack of heading levels seen so far (1 = `=`, 2 = `==`, etc.). |
| `first_heading_found`  | `bool`       | Whether any heading has been encountered yet. |
| `h1_count`             | `int`        | Number of H1 (`=`) headings seen. |
| `in_list`              | `bool`       | Whether we are currently in a list context. |
| `block_stack`          | `list[str]`  | Stack of currently open block types (see below). |

**Block stack:** The engine tracks all block delimiters — including code
blocks — as they open and close. The recognized block types are:

| Delimiter | Block type      |
|-----------|-----------------|
| `----`    | `"code_block"`  |
| `\|===`   | `"table"`       |
| `====`    | `"admonition"`  |
| `****`    | `"sidebar"`     |
| `++++`    | `"passthrough"` |
| `....`    | `"literal"`     |
| `--`      | `"open"`        |

You can query block context with:

```python
if state.in_block("table"):
    return  # skip this check inside tables

if state.in_code_block:  # equivalent to state.in_block("code_block")
    ...

if state.block_stack:  # we're inside some kind of block (including code blocks)
    ...
```

**Per-check private state:** If your check needs to track state across
lines (counters, flags, accumulators), use `state.check_state(name)`
to get a private dict scoped to your check:

```python
@register_check("my-check", "warning", "prose")
def check_something(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None:
    my_state = state.check_state("my-check")

    if "counter" not in my_state:
        my_state["counter"] = 0

    my_state["counter"] += 1
    # ...
```

This avoids polluting shared `ParseState` attributes. Each check gets
its own namespace; the dict is created lazily on first access.

### `Config`

The merged configuration from config file + CLI overrides. Check authors
typically use two methods:

| Method                      | Returns  | Description |
|-----------------------------|----------|-------------|
| `cfg.is_enabled(check_name)`| `bool`   | Whether the check is active. You rarely need this — the engine already skips disabled checks. |
| `cfg.severity(check_name)`  | `str`    | The effective severity (`"error"`, `"warning"`, or `"disable"`). Used internally by `add_finding`. |

For checks that use configurable term lists:

| Attribute        | Type            | Description |
|------------------|-----------------|-------------|
| `cfg.product_names` | `dict[str, str]` | Maps incorrect product names to their correct forms. |
| `cfg.banned_terms`  | `dict[str, str]` | Maps banned terms to suggested replacements. |

### `FileResult`

Accumulates findings for a single file. The primary method you'll use:

```python
file_result.add_finding(cfg, "my-check", line_num, "Description of the problem")
```

**Parameters:**

| Parameter    | Type          | Description |
|--------------|---------------|-------------|
| `cfg`        | `Config`      | Passed through to determine effective severity. |
| `check_name` | `str`         | Must match the name in your `@register_check`. |
| `line_num`   | `int \| None` | Line number (1-indexed), or `None` for file-level findings. |
| `message`    | `str`         | Human-readable description of the issue. |

You don't need to construct `Finding` objects directly — `add_finding`
handles that.

---

## Writing a check: step by step

### Example: a prose check

Suppose you want to warn when a line contains a TODO comment in the
rendered text (outside code blocks).

```python
# checks/prose.py

import re
from ..config import Config
from ..models import FileResult, ParseState
from ..registry import register_check


@register_check("todo-comments", "warning", "prose")
def check_todo_comments(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None:
    """Flag TODO/FIXME markers in prose text."""
    if re.search(r"\bTODO\b|\bFIXME\b", line, re.IGNORECASE):
        file_result.add_finding(
            cfg,
            "todo-comments",
            line_num,
            f"line {line_num}: TODO/FIXME marker found in prose",
        )
```

That's it. The decorator registers it, the engine calls it on every
prose line, and findings appear in the output automatically.

### Example: a structural check

Suppose you want to verify that every page file has a top-level heading.

```python
# checks/structural.py

import re
from typing import List
from ..config import Config
from ..models import FileResult
from ..registry import register_check


@register_check("require-title", "error", "structural")
def check_require_title(filepath: str, lines: List[str], cfg: Config, file_result: FileResult) -> None:
    """Ensure every .adoc file has a document title (= heading)."""
    for line in lines:
        if re.match(r"^= \S", line):
            return  # found a title
    file_result.add_finding(
        cfg,
        "require-title",
        None,
        "File has no document title (= heading)",
    )
```

Structural checks receive `filepath` as a string and `lines` as a
`list[str]` (already split, no trailing newlines).

### Example: using per-check state

A check that counts consecutive blank lines and warns if there are more
than two:

```python
@register_check("excessive-blank-lines", "warning", "prose")
def check_excessive_blank_lines(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None:
    """Warn on 3+ consecutive blank lines."""
    my = state.check_state("excessive-blank-lines")

    if not line.strip():
        my["count"] = my.get("count", 0) + 1
    else:
        if my.get("count", 0) >= 3:
            file_result.add_finding(
                cfg,
                "excessive-blank-lines",
                line_num - 1,
                f"line {line_num - 1}: {my['count']} consecutive blank lines",
            )
        my["count"] = 0
```

### Example: using block context

A check that only applies outside of tables:

```python
@register_check("no-bare-emphasis", "warning", "prose")
def check_no_bare_emphasis(line: str, line_num: int, state: ParseState, cfg: Config, file_result: FileResult) -> None:
    """Flag bare emphasis markers that may not render correctly."""
    if state.in_block("table"):
        return  # table cells have different formatting rules

    if re.search(r"(?<!\w)_[^_]+_(?!\w)", line):
        file_result.add_finding(
            cfg,
            "no-bare-emphasis",
            line_num,
            f"line {line_num}: Possible bare emphasis (use *bold* or `mono` for clarity)",
        )
```

---

## Adding a check to a new module

If your check doesn't belong in `prose.py`, `code_blocks.py`, or
`structural.py`, create a new module:

```
checks/
  __init__.py
  prose.py
  code_blocks.py
  structural.py
  my_checks.py          <-- new file
```

Then add the import to `checks/__init__.py`:

```python
from . import code_blocks  # noqa: F401
from . import prose  # noqa: F401
from . import structural  # noqa: F401
from . import my_checks  # noqa: F401
```

The import triggers `@register_check` at package load time, which is
all that's needed.

---

## Updating `.review-docs.conf`

Add a commented-out entry for your new check in the appropriate section
of `.review-docs.conf` at the repo root. This documents the check's
existence and its default severity:

```ini
[checks]
# ── Prose checks (run on lines outside code blocks) ──
# ...existing entries...
# todo-comments = warning
```

---

## Severity guidelines

| Severity    | Use when |
|-------------|----------|
| `"error"`   | The issue will cause incorrect rendering, broken links, or content that misleads readers. The CI pipeline fails on errors. |
| `"warning"` | The issue is a style or quality concern that should be fixed but doesn't break anything. Warnings alone never cause CI failure. |

Prefer `"warning"` as the default unless the check detects something
that is unambiguously broken. Users can promote any warning to an error
in their config file.

---

## Message format conventions

Findings messages should be concise and actionable. For line-level
checks, prefix the message with `line {line_num}:` for consistent
output:

```python
f"line {line_num}: Trailing whitespace"
f"line {line_num}: '{wrong}' should be '{correct}'"
f"line {line_num}: Code block delimiter without [source,language] specifier"
```

For structural (file-level) checks where `line_num` is `None`, omit
the prefix:

```python
"File does not end with a newline character"
"Tutorial page missing '== Prerequisites' section"
```

---

## Signature validation

The decorator validates your function's parameter **names** at import
time. If you misspell a parameter or use the wrong signature for your
scope, you'll get an immediate `TypeError`:

```
TypeError: Check 'my-check' (scope=prose) has signature
('line', 'num', 'state', 'cfg', 'file_result') but expected
('line', 'line_num', 'state', 'cfg', 'file_result') matching
LineCheck(line, line_num, state, cfg, file_result)
```

The expected signatures per scope:

| Scope                  | Parameters |
|------------------------|------------|
| `prose`                | `(line, line_num, state, cfg, file_result)` |
| `code_block_line`      | `(line, line_num, state, cfg, file_result)` |
| `code_block_boundary`  | `(line, line_num, state, cfg, file_result)` |
| `code_block_complete`  | `(block_content, block_lang, block_start_line, block_end_line, following_annotations, block_attrs, cfg, file_result)` |
| `structural`           | `(filepath, lines, cfg, file_result)` |

---

## Testing your check

Run against a single file:

```bash
python3 scripts/review-docs.py path/to/file.adoc --only=my-check
```

Run against all files:

```bash
python3 scripts/review-docs.py --all --only=my-check
```

Get JSON output for inspection:

```bash
python3 scripts/review-docs.py --all --only=my-check --format json
```

List all registered checks (confirm yours appears):

```bash
python3 scripts/review-docs.py --list-checks
```

---

## Checklist

- [ ] Function decorated with `@register_check(name, severity, scope)`
- [ ] Parameter names match the expected signature for your scope
- [ ] `check_name` in `add_finding()` matches the `name` in the decorator
- [ ] Module imported in `checks/__init__.py` (if new module)
- [ ] Entry added to `.review-docs.conf` (commented out)
- [ ] Tested with `--only=my-check` against representative files
- [ ] No false positives on `--all`
