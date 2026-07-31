# One Layer vs Two Layers: Claude Skill Structure

## Architecture Difference

The two repos implement a **one-layer vs two-layer** design.

---

### geek-chow-skills (one layer)
[source code](https://github.com/geekchow/geek-chow-skills.git)
```
skills/review-pr/SKILL.md    ← trigger + description + full workflow, all in one file
```

**directory structure**

```bash
     ├── CLAUDE.MD
     ├── LICENSE
     ├── plan.md
     ├── prompt.md
     ├── readme-test.pdf
     ├── README.md
     ├── skills
     │   ├── bilibili-uploader
     │   │   ├── scripts
     │   │   │   ├── download_playlist.py
     │   │   │   ├── enrich_subs.py
     │   │   │   └── update_video.py
     │   │   └── SKILL.md
     │   ├── commit-and-pr
     │   │   └── SKILL.md
     │   ├── mac-notes-exporter
     │   │   ├── scripts
     │   │   │   ├── export_notes.py
     │   │   │   └── notes_exporter.scpt
     │   │   └── SKILL.md
     │   ├── markdown-to-pdf
     │   │   ├── scripts
     │   │   │   └── convert.py
     │   │   └── SKILL.md
     │   ├── merge-cleanup
     │   │   └── SKILL.md
     │   ├── narration-generator
     │   │   ├── narration_en.txt
     │   │   ├── narration_zh.txt
     │   │   ├── scripts
     │   │   │   └── generate_narration.py
     │   │   └── SKILL.md
     │   ├── review-pr
     │   │   └── SKILL.md
     │   ├── study-assistant
     │   │   ├── scripts
     │   │   │   ├── pdf_reader.py
     │   │   │   ├── study_processor.py
     │   │   │   ├── web_fetcher.py
     │   │   │   └── youtube_handler.py
     │   │   └── SKILL.md
     │   └── video-transcriber
     │       ├── scripts
     │       │   └── transcribe_video.py
     │       └── SKILL.md

```

### obsidian-skills (two layers)
[source code](https://github.com/geekchow/obsidian-skills.git)
```
commands/clip-media.md       ← trigger + tool list + step-by-step orchestration
skills/clip-media/
  SKILL-Media-Localiser.md   ← domain knowledge: URL patterns, rules, formats
```

**directory structure**
```bash
     ├── CLAUDE.md
     ├── commands
     │   ├── clip-media.md
     │   ├── create-concept.md
     │   └── distil-aichat.md
     ├── install.sh
     ├── plugin.json
     ├── skills
     │   ├── clip-media
     │   │   └── SKILL-Media-Localiser.md
     │   └── distil-aichat
     │       └── SKILL-Distil-AI-Conversation.md
     └── templates
         └── NewObConceptTemplate.md
```

The command file is the **orchestrator** — it reads the SKILL file as the first step, then drives the workflow. The SKILL file is a pure **reference document**: detection patterns, naming conventions, domain rules.

---

### Pros/Cons

| | geek-chow-skills (1 layer) | obsidian-skills (2 layers) |
|---|---|---|
| **Simplicity** | ✅ One file to maintain | ❌ Two files per skill |
| **Context usage** | ✅ Claude loads only what's needed | ✅ Command is small; skill loaded on-demand |
| **Separation of concerns** | ❌ Workflow + domain rules tangled together | ✅ Orchestration vs knowledge are distinct |
| **Reusability** | ❌ Can't reuse domain rules across commands | ✅ Multiple commands can reference one SKILL |
| **Domain knowledge clarity** | ❌ Rules buried in procedural instructions | ✅ Rules are isolated, easy to audit/update |
| **Appropriate for** | Script-driven skills (logic lives in `.py`) | Knowledge-heavy skills (rules live in Claude's head) |

---

### Why it makes sense for obsidian-skills

`clip-media` has no Python script — all the logic runs in Claude's head. The SKILL file is a *rulebook* (50+ URL patterns, naming rules, rewrite formats). Separating it from the orchestration step means:
- You can update the rulebook without touching the workflow
- The command stays readable (it's an outline, not a wall of rules)
- A second command (e.g., `audit-media.md`) could reuse the same SKILL file

For geek-chow-skills, most skills delegate to Python scripts, so the SKILL.md mainly says "run this script with these args" — a second layer would add complexity without benefit.

**Bottom line**: the two-layer pattern pays off when the domain knowledge is substantial and lives in Claude's context rather than in code. When complexity lives in scripts, the single-layer approach is cleaner.
