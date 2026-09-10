# Record an exception

A framework may deviate from one control for a while, never silently.

1. Write a decision record under `docs/decisions/NNNN-slug.md` stating the deviation, why it is
   needed and what closes it. List it in `docs/decisions/index.md`.
2. Add the exception to `estatuto.toml`, naming the control, the decision and a sunset date:

```toml
[[exception]]
control = "E-3.1"
decision = "docs/decisions/0002-reference-pages-later.md"
sunset = 2027-01-31
reason = "Reference pages arrive with the first real capability."
```

3. Run the gate. The control shows as waived (`~`) with its sunset; the gate passes. After the
   sunset the control fails again and the expired exception is itself a finding (E-8.1).
