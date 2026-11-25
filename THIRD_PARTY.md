# Sources and license notices

The creation and maintenance skill workflows adapt ideas and structure from pstack's create-verification-skill and maintain-verification-skill: interview the repository, launch/doctor/drive/evidence/cleanup, feature maps, read-only source waves and live re-proof. pstack is MIT licensed, copyright (c) 2026 Lauren Tan. The complete notice is retained in [third_party/pstack-LICENSE](third_party/pstack-LICENSE).

Upstream inspected through GitHub API at repository commit `bb68f2365eceafa0cb2d253112f675acf5f144cc`:

- [create-verification-skill](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/create-verification-skill/SKILL.md), blob `140d033a001e8d27acd14b06004506c43053b199`.
- [maintain-verification-skill](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/skills/maintain-verification-skill/SKILL.md), blob `a2680b91fead45a0b4963d8c367a854956bea59d`.
- [license](https://github.com/cursor/plugins/blob/bb68f2365eceafa0cb2d253112f675acf5f144cc/pstack/LICENSE).

The installed open-pstack skill package version `1.16.0` was also read. It adds runtime portability guidance and differs from the inspected Cursor upstream; these are not assumed identical release numbers. No global skill or plugin configuration was changed.

The open-verified-pr skill is a new workflow that hands off to pstack's formal verification skills by role and copies none of their commands. Its rules on keeping a model true to the code, reader-word chart labels, bug-path replay and stale passes follow these files, inspected at repository commit `b96ec1e24c3acac8cb5a454d4f4e3c0d75c69c74`:

- [statechart](https://github.com/cursor/plugins/blob/b96ec1e24c3acac8cb5a454d4f4e3c0d75c69c74/pstack/skills/statechart/SKILL.md), blob `18d653a810dfbb3ea35a6ed88bcfe8cb84f0a893`.
- [create-formal-verification-skill](https://github.com/cursor/plugins/blob/b96ec1e24c3acac8cb5a454d4f4e3c0d75c69c74/pstack/skills/create-formal-verification-skill/SKILL.md), blob `92f7aa4fa966b857dd7fcc994b3c59650767c878`.
- [maintain-formal-verification-skill](https://github.com/cursor/plugins/blob/b96ec1e24c3acac8cb5a454d4f4e3c0d75c69c74/pstack/skills/maintain-formal-verification-skill/SKILL.md), blob `5d2f7f2228a3b771ca5b03124fc265ddfc53c5fc`.

The skill's own authorization is limited to pushing the work branch and opening one PR when the user asked for that PR; it never merges.

hirastack adds design-document inventory, source/excerpt hashes, purpose/rationale/invariant ledgers, explicit ambiguity, a dependency-free runner, conservative outcome aggregation and the new verify-design coordinator. Upstream's maintenance workflow is not treated as authorization to create commits, PRs or deployments. verify-design is a new coordinator, not a claim that pstack already provides a generic execution skill.

