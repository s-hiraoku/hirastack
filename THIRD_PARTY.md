# Sources and license notices

The creation and maintenance skill workflows adapt ideas and structure from pstack's create-verification-skill and maintain-verification-skill: interview the repository, launch/doctor/drive/evidence/cleanup, feature maps, read-only source waves and live re-proof. pstack is MIT licensed, copyright (c) 2026 Lauren Tan. The complete notice is retained in [third_party/pstack-LICENSE](third_party/pstack-LICENSE).

Upstream inspected through GitHub API at repository commit `bb68f2365eceafa0cb2d253112f675acf5f144cc`:

- [create-verification-skill](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/create-verification-skill/SKILL.md), blob `140d033a001e8d27acd14b06004506c43053b199`.
- [maintain-verification-skill](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/maintain-verification-skill/SKILL.md), blob `a2680b91fead45a0b4963d8c367a854956bea59d`.
- [license](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/LICENSE).

The installed open-pstack skill package version `1.16.0` was also read. It adds runtime portability guidance and differs from the inspected Cursor upstream; these are not assumed identical release numbers. No global skill or plugin configuration was changed.

hirastack adds design-document inventory, source/excerpt hashes, purpose/rationale/invariant ledgers, explicit ambiguity, a dependency-free runner, conservative outcome aggregation and the new verify-design coordinator. Upstream's maintenance workflow is not treated as authorization to create commits, PRs or deployments. verify-design is a new coordinator, not a claim that pstack already provides a generic execution skill.

HAB source remains in its own repository. Project documents here are original review summaries with commit-pinned links. Helpers call the HAB APIs and existing synthetic verification scaffold; they do not vendor the HAB implementation or claim its license. A2A/NATS/product documentation links retained in HAB are source context; this task did not independently revalidate every external standard or real product version.
