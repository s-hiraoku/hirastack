# hirastack work rules

- Generic code in `hirastack/` and skills must stay independent of any target product.
- Target-specific principles, citations, recipes and checks live with the target (its repository or a user-selected verification repo), never in this repository. `projects/` holds only hirastack's own self-contract.
- Read all non-excluded design documents; index exclusions with reasons. Inventory is not semantic review.
- Preserve uncertainty, explicit scope and source provenance. Never resolve authority by newest timestamp alone.
- Do not change product code from maintenance or verification tasks. Report a product regression separately.
- Run `python3 -m unittest discover -s tests -v` for runner changes. Exercise changed target helpers on an isolated target and retain failed attempts.
- Do not change frozen source pins, drop checks, replace manual with automatic pass, or narrow requirements to hide a regression.
- Commit/push/PR/merge/deploy follow the user's current authorization; skill invocation alone grants none of them.
- Evidence contains target output; inspect before sharing. Do not commit private stores or credentials.
