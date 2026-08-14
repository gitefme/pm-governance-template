# Product Design Specification

Durable cross-product UX and interaction contract for projects created from this template. It complements `DESIGN_BRIEF.md` and `ARCHITECTURE.md`; it does not replace their ownership.

## Ownership and Relationships

- `DESIGN_BRIEF.md`: product outcomes, principles, and user workflows.
- `PRODUCT_DESIGN.md`: cross-product information architecture, interaction patterns, UI states, responsive behavior, and accessibility conventions.
- `ARCHITECTURE.md`: system boundaries, data ownership, trust boundaries, and major technical decisions.

When a feature creates a reusable rule, record it in the document that owns that rule. Keep feature-only decisions in the feature plan's `Design Basis` unless later confirmed work promotes them to a cross-product rule. If the project adopts a narrower design document, such as a workspace or domain-specific specification, record its ownership here and in the workflow source map.

## Cross-Product Experience Contract

- Keep the user's current context visible and understandable across related workflows.
- Reuse an established control or interaction pattern before introducing a new one.
- Give loading, empty, unavailable, error, disabled, destructive, and successful states clear wording and accessible presentation when relevant.
- Preserve user work by default; destructive or irreversible actions require clear, explicit confirmation.
- Keep primary actions and the current task functional and discoverable on supported desktop and mobile layouts.
- Use accessible labels, keyboard operation, visible focus, and understandable status feedback for interactive controls.

## Complex-Plan Design Basis

Every `pending` or `confirmed` detailed plan includes a non-empty `Design Basis` section. When the task has no product-design effect, say so explicitly and do not invent design requirements. When design applies, include:

- only the durable design and architecture sources that apply;
- task-specific confirmed design decisions;
- open design decisions requiring user confirmation before implementation;
- expected loading, empty, error, disabled, destructive, and success states when relevant;
- accessibility and responsive implications.

Do not list irrelevant source documents merely to satisfy a template. A task plan does not authorize changing a durable product-design rule without the normal formulation-confirmation process.
