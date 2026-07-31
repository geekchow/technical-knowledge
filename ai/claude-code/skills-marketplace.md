# Claude Skills Marketplace

The `.claude-plugin/` folder makes this repo publishable as a **Claude Code plugin** — it tells the plugin system what's in the repo and how to install it.

## The two files

**`plugin.json`** — the plugin manifest. It declares:
- Plugin identity (name, version, author)
- Which skill directories to register when someone installs this plugin
- This is what Claude Code reads when you run something like `claude plugin install`

**`marketplace.json`** — the marketplace listing. It's a richer version of the same info, structured for the [agentskills.io](https://agentskills.io) marketplace:
- One entry per skill with its own name and description
- `source: "./"` means the plugin is self-contained (no external repo to clone)
- `strict: false` means the skill instructions are flexible guidelines, not rigid scripts
- This is what the marketplace UI reads to show users what skills are available

## In short

| File               | Purpose                       | Audience                   |
| ------------------ | ----------------------------- | -------------------------- |
| `plugin.json`      | Plugin identity + skill paths | Claude Code CLI            |
| `marketplace.json` | Per-skill listing metadata    | agentskills.io marketplace |

Without these files, the repo is just a collection of `SKILL.md` files. With them, it becomes an installable plugin that other users can discover and add to their Claude Code setup with a single command.

**Note**: both files are slightly out of date — they don't list `rednote-promoter` in `plugin.json`'s skills array, and some descriptions differ from what the skills actually do now (e.g. narration-generator uses Kokoro locally, not OpenAI TTS).

Good catch — there's actually **no formal cross-reference** between the two files. They serve different consumers entirely:

```
plugin.json  ──► Claude Code CLI ──► reads SKILL.md frontmatter for identity
marketplace.json ──► agentskills.io ──► standalone listing, self-contained
```

**`plugin.json`** just says "load skills from these paths." Claude Code then reads each `SKILL.md` at those paths to get the skill's name, description, and trigger keywords from the frontmatter. The frontmatter **is** the skill identity.

**`marketplace.json`** is an independent catalog for the marketplace UI — it duplicates the name/description inline so the marketplace can render listings without cloning the repo. It also has its own `skills` array per entry.

The only implicit "mapping" is the **directory path** — e.g. `./skills/markdown-to-pdf` appears in both files, and the SKILL.md `name:` field should match the `marketplace.json` plugin `name` field. But there's no enforced link; they can drift (and the `markdown-to-pdf` description already has drifted, as I noted earlier).

In practice this means:
- If a skill path is in `plugin.json` but missing from `marketplace.json` → installable but not discoverable on the marketplace
- If a skill is in `marketplace.json` but missing from `plugin.json` → shows on marketplace but won't install

That's exactly the bug we just fixed with `video-transcriber`, `review-pr`, and `rednote-promoter`.

Honestly, you're right — it's redundant. The most likely reasons this split exists:

**Historical layering**: `plugin.json` was probably the original simple install manifest built first. When agentskills.io marketplace support was added later, a new file with a richer schema was introduced rather than evolving `plugin.json` — to avoid breaking existing CLI consumers.

**Schema mismatch**: `marketplace.json` uses a nested `plugins[].skills[]` structure (skills grouped under plugin entries) while `plugin.json` uses a flat `skills[]` array. The CLI was likely built against the simpler flat schema.

**Decoupling intent**: The design probably intended that a private/internal plugin repo could have `plugin.json` without opting into marketplace listing — i.e., you "publish" to the marketplace separately by having `marketplace.json`.

---

In practice though, for a repo like this where both files exist and must be kept in sync, the split creates exactly the drift we just fixed. A cleaner design would be either:

- CLI reads `marketplace.json` directly (single source of truth), or
- `plugin.json` gets dropped and the CLI adopts the marketplace schema

If you wanted to simplify, you could raise this as a spec issue with agentskills.io — or just treat `marketplace.json` as the authoritative file and have `plugin.json` be a thin generated artifact. But as long as the spec requires both, we're stuck maintaining them in parallel.

 marketplace
    └─ plugin (marketplace.json)
         └─ skill (plugin.json → SKILL.md)

  - Marketplace — the catalog users browse to discover and install things (agentskills.io)
  - Plugin — the installable unit; a versioned, authored package you install in one go
  - Skill — the executable unit; a single capability Claude can invoke

  In this repo, it happens to be a 1:1 plugin-to-repo relationship, but in principle one
  marketplace could list many plugins, and one plugin can bundle many skills.
