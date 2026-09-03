# Separate Cross-Module Identifier Domains

## Context

Legacy systems often pass several small numeric or character codes through one workflow. A source module may create its own voucher, call a cross-module conversion procedure, and then open a target-module editor. The values can look related while belonging to different domains.

## Problem

Treating all nearby codes as one enum silently changes semantics. Typical examples include:

- a source business discriminator such as `A/C/D/Z/V`;
- an integration mode identifying the originating subsystem;
- a procedure parameter describing a conversion variant;
- a target UI document type used only to open an editor.

Numerical coincidence, proximity in a call chain, or a shared variable name is not evidence that these codes are aliases.

## Pattern

Model every code at its owning boundary:

1. Record the exact caller, callee, parameter name and raw value.
2. Give each domain a separate field and vocabulary.
3. Preserve the complete mapping chain: source record ID -> interface call -> target origin relation -> target UI identifier.
4. State unknown mappings as `partial` instead of normalizing them.
5. Add a regression test that asserts the values independently, especially when two values are easy to conflate.

Example representation:

```json
{
  "source_type": "Z",
  "interface": {
    "procedure": "P_TargetInterface",
    "origin_mode": 2,
    "conversion_type": 0
  },
  "target_display_type": 125,
  "origin_relation": "TargetHeader.OriginCode = SourceHeader.Code AND OriginMode = 2"
}
```

## Evidence standard

For each value, cite the smallest authoritative location:

- source discriminator: the branch or caller assigning it;
- interface parameters: the actual procedure invocation;
- origin relation: target table query or procedure predicate;
- display type: the editor-opening call.

Do not derive one value from another unless the source contains an explicit mapping.

## Validation

On a disposable database clone:

1. create one source transaction per source discriminator;
2. capture source IDs and aggregate fingerprints;
3. follow the interface-created target record through its origin relation;
4. open the target UI and record the display type separately;
5. reverse the transaction and confirm the clone returns to baseline.

## Anti-pattern

Avoid a generic field such as `voucher_type` that stores whichever code is available at a given step. It makes documentation appear complete while erasing which subsystem owns the value and how the cross-module mapping actually works.
