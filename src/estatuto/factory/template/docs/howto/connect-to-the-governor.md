# Connect to the governor

The governing application (La Generala) discovers this employee from its manifest, negotiates
compatibility, admits a version through its administration plane and only then assigns work.

1. **Publish.** Ship a version; `manifest.json` is rendered from the declarations and vendored
   with the distribution.
2. **Negotiate.** The governor sends a `peg.compatibility-demand/1.0.0`; every material field
   must match a declared capability exactly. The decision is `accept` or `reject` before any
   assignment exists.
3. **Admit.** The governor certifies and admits the version per tenant; canary and rollback are
   its concern, not the employee's.
4. **Assign.** The governor posts `peg.assignment/1.0.0` to `/peg/v1/assignments` (or calls the
   in-process transport). The employee attests the same capsule digest, tenant, mission,
   obligation and generation in its `peg.result/1.0.0`.
5. **Accept.** The governor verifies and accepts or rejects. The employee never does.

The employee has no runtime dependency on the governor: it installs, tests and serves alone.
