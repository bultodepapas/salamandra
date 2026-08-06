---
title: Contributing
description: How to help — the order of value of contributions, the workflow, and the confidence rule that protects the record.
editUrl: https://github.com/bultodepapas/salmandra/edit/main/wiki/content/guide/05-contributing.md
---

# Contributing

This is a community project. Contributions of all kinds are welcome — not only research and structures, but also parts, variants, adapters and creative work. The full guide is in [CONTRIBUTING](../platform/contributing/); this page is the summary.

## Order of value

| Priority | Type | Example |
|---|---|---|
| **1** | **Measurements** | Convert an `[E]` or `[I]` into `[M]` with a published method |
| **2** | **Corrections** | A better source overturns an existing conclusion |
| **3** | **Replications** | Independent build with blackbox data |
| **4** | **Geometry & parts** | Wings, fuselages, mounts, adapters — based on the research |
| **5** | **Creative & decorative** | Visual improvements and other modifications |

The most valuable contributions raise the **confidence level** of the project: they turn estimates into measurements and reasoning into parts that fly.

## The one rule that protects the record

> Numbers without a source are not accepted in the technical record, even if they are correct.

If a new datum contradicts an existing claim, **do not silence it by editing the text**: fix it and add an entry to the [changelog](../platform/changelog/) with a correction number (C). The correction register is part of the product — there are 21 so far.

## Workflow

1. Open an issue describing what you want to add and which gap (G) or decision (ADR) it touches.
2. Work on the documents, parts, or both. A part submitted with its reasoning is better than one without.
3. Fill in the PR template — it asks for the affected decisions and gaps, and the confidence level of any new datum.
4. If you invalidate a previous claim, add a correction to the changelog.

## Writing a new ADR

Copy the [template](../decisions/overview/). One decision per file. A good ADR answers four questions:

- What forced the decision?
- What was discarded, and why?
- What does this decision require downstream?
- **What datum would make you reconsider it?**

## Submitting test data

Test data must declare the **complete configuration**: pack, motor, propeller, takeoff mass, material, perimeters, infill, firmware version. Without that, data from different builders are not comparable.

## Source quality

Order of preference: peer-reviewed → experimental databases (UIUC) → controlled test with declared method → manufacturer documentation → patents → own measurement on in-service articles.
