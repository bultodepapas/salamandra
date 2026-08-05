# Salamandra — Image Prompts (ChatGPT)

Versioned prompts for generating images of the Salamandra design with ChatGPT (image
generation). Every prompt is based on the values of a specific Design Guide version and
was written following the 2026 best practices for GPT-4o/gpt-image prompting (§ Best
practices 2026).

## Index

| Prompt | File | Purpose |
|---|---|---|
| Render | [`v0.1-01-render.md`](v0.1-01-render.md) | Studio product render, CGI style |
| Blueprint | [`v0.1-02-blueprint.md`](v0.1-02-blueprint.md) | Technical orthographic drawing with dimensions |
| Realistic photo | [`v0.1-03-realistic-photo.md`](v0.1-03-realistic-photo.md) | Photorealistic photograph of the physical model |
| Creative — in flight | [`v0.1-04-creative-inflight.md`](v0.1-04-creative-inflight.md) | Cinematic in-flight hero shot |

## Versioning rule (do not overwrite)

- Prompts are bound to the design version they illustrate: **`vXX-YY-<name>.md`**, where
  `vXX` is the Design Guide version and `YY` a sequence number.
- **Never edit or delete an existing version file.** When the design changes to v0.2,
  create new files (`v0.2-01-render.md`, …) and add them to the index above.
- Old prompts stay as historical record: they document what the design looked like at that
  version, even if the values are later superseded.
- The authoritative geometry is always the Design Guide of the same version
  (`../Salamandra-Design-Guide-v0.1.md` for the current prompts).
- Prompt *technique* improvements (like the 2026 best practices below) are back-ported
  into the current version's files and noted in their header; they do not change the
  design values.

## Shared subject block (used by all prompts)

> Salamandra: a 1300 mm wingspan 3D-printed forward-swept tailless flying wing (FPV
> drone). Fully 3D-printed in light gray PETG with visible FDM layer lines and a matte
> finish. Planform: strongly forward-swept wing (quarter-chord sweep −20°), tapered from
> a 289 mm root chord to a 145 mm tip chord, aspect ratio 6, slight 2° dihedral at the
> tips. Wing split into segments with visible panel joints, three segments per wing half
> meeting a central fuselage pod. Central pod (CORE) with rounded nose, battery hatch and
> a single rear-mounted electric pusher motor driving a black 8-inch (203 mm) two-blade
> propeller at the trailing edge. Large elevons along the trailing edge with hinge lines
> at 72 % of the chord. No tail, no vertical stabilizer. Small FPV camera in the nose.
> Clean, functional, low-drag design.

---

## Best practices 2026 (research-backed)

These are the techniques applied in the prompts below, from 21 researched sources
(OpenAI documentation and blog, Prompt Engineering Guide / DAIR.AI, Learn Prompting,
Anthropic, IBM, ZDNET, Zapier and others — full list in § Sources).

### Structure the prompt in sections

Models follow detailed, organized prompts better than long run-on text. Each prompt below
uses the same anatomy: **Role → Subject → Medium → Environment → Composition/Camera →
Lighting → Color/Mood → Format (aspect ratio) → Exclusions → Quality boosters**.
Recommended by: Prompting Guide 4o Image Generation (subject, medium, environment, color,
mood); Prompting Guide — prompt elements; Learn Prompting — basics (parts of a prompt).

### Be specific — the model fills gaps you leave

Underspecified prompts let ChatGPT invent details (bad sweep direction, tail, wrong
propeller). Every prompt states the critical facts twice-checks against a validation
checklist. Recommended by: Prompting Guide 4o; OpenAI image guide; IBM; ZDNET (set the
stage and provide context).

### Specify lighting, camera and composition explicitly

"Golden hour", "soft window light", "50 mm lens look", "three-quarter view, slightly
elevated" are not decoration: they are the difference between a generic image and the
one you want. Recommended by: Prompting Guide 4o (lighting/composition/style);
Learn Prompting — style modifiers and shot types.

### Always declare the aspect ratio in the prompt

The model defaults to 1:1 when not told otherwise. State "3:2", "16:9" or "4:3" in the
prompt, and prefer landscape for aircraft. Recommended by: Prompting Guide 4o;
Learn Prompting — Midjourney (--ar); OpenAI docs (size options).

### Iterate in the same chat; start a new chat for independent images

GPT-4o image generation keeps visual consistency across turns in the same conversation —
use multi-turn editing ("make it realistic", "now from the rear") instead of re-rolling.
For an independent, unrelated image, open a fresh chat so prior images do not leak into
the result. Recommended by: OpenAI — Introducing 4o Image Generation (multi-turn);
OpenAI platform docs (multi-turn editing); Prompting Guide 4o (consistency);
ZDNET (refine and build on previous prompts; start a new session).

### Phrase exclusions positively, keep them few

Models respond better to what to do than what not to do; keep the 2–3 critical
exclusions short ("no text, no logos, no watermark"). Recommended by: Prompting Guide —
general tips ("to do or not to do").

### Use quality boosters and shot types

"Highly detailed, sharp focus" and explicit shot types ("three-quarter view",
"low-angle") measurably improve adherence. Recommended by: Learn Prompting — quality
boosters and shot type.

### Ask the model to show the prompt it used

If the output is far off, ask ChatGPT to output the prompt it actually sent to the image
model, find the misplaced emphasis, then start a new chat with the corrected prompt.
Recommended by: Prompting Guide 4o.

### Know the model's limits (plan around them)

- **Text in images can still fail** — keep labels to a minimum (blueprint title block
  only; check the rendered text).
- **Composition control is limited** — keep layouts simple; don't demand exact element
  placement.
- **Consistency across separate generations is not guaranteed** — use the shared subject
  block verbatim and iterate in one chat.
- **Images take time** (up to ~1–2 min) and the free tier queues generations.
Recommended by: OpenAI platform docs (limitations); OpenAI — Introducing 4o blog
(limitations); Prompting Guide 4o (limitations).

### Use a reasoning model to draft or rework a prompt

If you are stuck, ask ChatGPT (a reasoning model) to write 3 varied optimized prompts
from your description and pick the best parts. Recommended by: Prompting Guide 4o.

### Prompt the correct tool

In ChatGPT, make sure the **image generation tool** (not DALL·E) is used; for heavy
iteration, a reasoning model keeps the design facts "in mind". Recommended by:
Prompting Guide 4o (tool selection and personalization tip).

---

## How to use

1. Open ChatGPT (image generation tool; GPT-4o/gpt-image or later).
2. Copy the `## Prompt` block of the chosen file — keep the section structure intact.
3. Optionally paste the shared subject block in the chat first, then ask for the specific
   image: this seeds the conversation with the design facts (multi-turn consistency).
4. Iterate in the same chat ("now from the rear", "make it realistic", "3:2 ratio").
5. If the image contradicts the design (wrong sweep direction, tail present, tractor
   prop), correct it explicitly — the wing must sweep **forward**, not backward.

---

## Sources (21)

1. OpenAI Platform — *Image generation guide* (GPT Image models, editing, multi-turn,
   limitations): https://platform.openai.com/docs/guides/image-generation
2. OpenAI — *Introducing 4o Image Generation*: https://openai.com/index/introducing-4o-image-generation/
3. Prompt Engineering Guide (DAIR.AI) — *4o Image Generation*:
   https://www.promptingguide.ai/guides/4o-image-generation
4. Prompt Engineering Guide — *Elements of a Prompt*:
   https://www.promptingguide.ai/introduction/elements
5. Prompt Engineering Guide — *General Tips for Designing Prompts*:
   https://www.promptingguide.ai/introduction/tips
6. Prompt Engineering Guide — *Prompting Techniques*:
   https://www.promptingguide.ai/techniques
7. Learn Prompting — *Image Prompting: Introduction*:
   https://learnprompting.org/docs/image_prompting/introduction
8. Learn Prompting — *Style Modifiers*:
   https://learnprompting.org/docs/image_prompting/style_modifiers
9. Learn Prompting — *Quality Boosters*:
   https://learnprompting.org/docs/image_prompting/quality_boosters
10. Learn Prompting — *Shot Type*:
    https://learnprompting.org/docs/image_prompting/shot_type
11. Learn Prompting — *Weighted Terms*:
    https://learnprompting.org/docs/image_prompting/weighted_terms
12. Learn Prompting — *Fix Deformed Generations*:
    https://learnprompting.org/docs/image_prompting/fix_deformed_generations
13. Learn Prompting — *Repetition*:
    https://learnprompting.org/docs/image_prompting/repetition
14. Learn Prompting — *Midjourney* (aspect ratio, seed, parameters):
    https://learnprompting.org/docs/image_prompting/midjourney
15. Learn Prompting — *Image Prompting Resources*:
    https://learnprompting.org/docs/image_prompting/resources
16. Learn Prompting — *Basics Guide Overview* (roles, prompt parts, priming):
    https://learnprompting.org/docs/basics/introduction
17. Anthropic — *Prompt engineering overview*:
    https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
18. IBM — *What is prompt engineering?*:
    https://www.ibm.com/think/topics/prompt-engineering
19. ZDNET — *10 ChatGPT pro tips for better results*:
    https://www.zdnet.com/article/how-to-write-better-chatgpt-prompts/
20. Zapier — *ChatGPT prompts* (limits, placeholders, iteration):
    https://zapier.com/blog/chatgpt-prompts/
21. Prompt Engineering Guide — *Introduction* (prompt engineering as an iterative
    discipline): https://www.promptingguide.ai/introduction

---

## Revision log

| Version | Date | Change |
|---|---|---|
| 0.1 rev. 5 | 2026-08-05 | Render prompt: Subject expanded with full shape description — planform proportions, LE/TE sweep angles and tip displacement, front-view flatness, airfoil section, segments/joints, pod, pusher prop, elevons and balance horns. Only `v0.1-01-render.md` updated. |
| 0.1 rev. 4 | 2026-08-05 | Render prompt: text-only planform descriptions failed (model defaulted to aft-sweep/dihedral). Switched to silhouette-first workflow (top-view planform → 3D render in the same chat) + reference-image method (X-29/Mojito/Nemesis/hand sketch) + flat-wing prohibition. Only `v0.1-01-render.md` updated. |
| 0.1 rev. 3 | 2026-08-05 | Render prompt: forward-sweep redefined with redundant visual anchors (arrow direction, tip position, sweep direction, X-29 reference, prohibition) + reference-image strategy. Only `v0.1-01-render.md` updated. |
| 0.1 rev. 2 | 2026-08-05 | Prompts restructured per 2026 best practices; techniques and 21 sources documented. Design values unchanged. |
| 0.1 | 2026-08-05 | Initial prompt set for Design Guide v0.1. |
