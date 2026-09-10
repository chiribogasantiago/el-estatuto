# Measure a repository

This tutorial measures an existing framework against the standard and reads the result.

## 1. Install the standard as a tool

```bash
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto --version
```

## 2. Declare the repository

At the framework's root, `estatuto.toml` states its name, slug, role, package and the standard
version it follows. Without it the gate refuses to guess:

```toml
[framework]
name = "El Corresponsal"
slug = "corresponsal"
role = "employee"
package = "corresponsal"
standard = "1.0.0"
```

## 3. Run the gate

```bash
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto gate . --output work/framework-standard-gate.json
```

The terminal lists every applicable control with `✓`, `✗` or `~` (waived) and the findings under
each failure. The JSON document is `estatuto.framework-standard-gate-result/1.0.0`; CI keeps it
as evidence.

## 4. Act on findings

Each finding names a file and a rule. Fix the file, or — when the deviation is deliberate and
bounded — record an exception (see [Record an exception](../howto/record-an-exception.md)).
