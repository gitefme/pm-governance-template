# Durable Plans

Allowed statuses:

- `draft`: incomplete.
- `pending`: awaiting approval.
- `confirmed`: approved.
- `implemented`: completed.
- `superseded`: replaced.

## Three-Gate Rule

Formulation, approval, and activation are distinct.

Lightweight tasks record Plan Type: Lightweight and Resume When if parked. Detailed tasks record Plan Type: Detailed and Blocked By if blocked. Pending and confirmed detailed plans include a non-empty Design Basis.
