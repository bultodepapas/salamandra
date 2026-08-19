# Salamandra — How to Publish a New Release

**Status:** Maintainer procedure
**Applies to:** repository releases, CAD baselines and documentation packages

This procedure turns an integrated, reviewed repository state into an immutable Salamandra
release. It does not authorize technical changes. All engineering changes must already be
reviewed, documented and merged before the release candidate is frozen.

> **Release rule:** publish from a clean, fully integrated commit on `main`. Never create
> a release from one developer's partial working tree, from uncommitted files or while
> required upstream work is still changing.

---

## 1. Understand the independent versions

Salamandra uses three related but independent identifiers.

| Identifier | Example | Meaning | Owner |
|---|---|---|---|
| Repository release | `v0.6.0` | Immutable integration point and Git tag | Release document and annotated Git tag |
| Design Guide version | `0.24` | Revision of the released aircraft/CAD specification | Both Design Guides |
| Documentation-site package | `0.6.0` | Wiki package metadata | `wiki/package.json` and lockfile |

Do not force the Design Guide version to equal the repository release. Bump the guide
only when its controlled content changes. A release may package an unchanged guide, but
the release document must state that explicitly.

### 1.1 Recommended release numbering before 1.0

| Change | Release increment | Example |
|---|---|---|
| Breaking CAD baseline, new architecture or major verified capability | Minor | `v0.5.0` → `v0.6.0` |
| Corrections or documentation that do not change the released CAD baseline | Patch | `v0.5.0` → `v0.5.1` |
| First prototype baseline or declared stable public contract | Project decision | Normally `v1.0.0` after the required physical gates close |

The release reviewer may choose a higher increment when migration risk warrants it. The
release document must explain the choice.

---

## 2. Freeze scope before editing release metadata

Create a short release scope with:

- proposed tag and release title;
- exact integration commit or PR set;
- technical values that changed;
- CAD or manufacturing migration required;
- corrections added to `CHANGELOG.md`;
- gates closed, reopened or still open;
- generated artifacts that must be refreshed;
- explicit exclusions.

Do not begin packaging while contributors are still changing files inside the release
scope. Integrate their work first, then create a dedicated release branch from the latest
`main`.

```bash
git switch main
git pull --ff-only
git status --short
git switch -c release/vX.Y.Z
```

`git status --short` must be empty before creating the branch. If it is not empty, stop
and identify the owner of every change. Do not discard, overwrite or absorb another
developer's work into the release commit.

---

## 3. Create the release document

Create the next numbered document in `docs/`, following the current release structure:

```text
docs/NN-release-vX.Y.md
```

Use the latest release document as a structural reference, not as text to copy blindly.
The new document must contain:

1. release title, date, exact tag and status;
2. controlling concise and Advanced Design Guide versions;
3. authority order and migration rule;
4. exact technical and documentation delta;
5. values that did not change;
6. CAD impact and obsolete artifacts;
7. closed and still-open physical gates;
8. released-package inventory;
9. reproducible verification commands and results;
10. known limitations and explicit non-claims.

Use `Status: RELEASE CANDIDATE` in the PR. Change it to `RELEASED` only in the final
release commit after every required check passes.

The documentation-site generator discovers the current release by reading release files,
extracting their `Tag:` field and selecting the highest semantic version. Therefore:

- every release document must contain exactly one tag such as `**Tag:** \`v0.6.0\``;
- the tag must match the intended Git tag exactly;
- historical release documents must remain unchanged;
- never change an old release document to make it look current.

---

## 4. Update the canonical documentation

Review every row; update only what the release actually changes.

| File | Required review |
|---|---|
| `README.md` | Current release label, date/revision, summary and current release link |
| Concise Design Guide | Version/date/status, CAD values, provisional markers and handoff checklist |
| Advanced Design Guide | Same technical baseline, detailed migration, calculations and revision history |
| Design Guide Justification | Evidence or rationale affected by changed requirements |
| Design Guide Open Points | Gates closed, reopened, added or renumbered |
| `CHANGELOG.md` | Release entry and every correction that invalidates a previous claim |
| `docs/README.md` | Add the new release document and mark the former one historical |
| ADRs and research | Status, downstream consequences and reversal triggers |
| `CONTRIBUTING.md` | Only when the contribution or release process itself changes |

The concise and Advanced Design Guides must describe the same released values. The
concise guide remains the primary CAD execution document; the Advanced Guide retains the
full engineering context. If they disagree, the release is blocked.

### 4.1 Update the wiki package version

From `wiki/`, update `package.json` and `package-lock.json` together without creating a
Git tag:

```bash
npm version X.Y.Z --no-git-tag-version
```

Do not manually edit generated pages under `wiki/src/content/docs/`. They are rebuilt
from canonical repository documents.

---

## 5. Refresh generated artifacts only when their sources changed

Generated drawings are part of the release package. If calculations, geometry, equipment
placement or drawing manifests changed, the responsible technical owner must regenerate
and review them before the release freeze:

```bash
python calculations/generate_blueprints.py
```

Commit the generated SVGs, manifest and published documentation blocks together with
their authoritative source change. A documentation-only release that does not change a
drawing source must not regenerate drawings merely to change timestamps or formatting.

Every generated sheet must retain `DRAFT — NOT FOR MANUFACTURE` until its physical and
CAD gates are closed.

---

## 6. Run the release gates

Run these commands from the frozen release branch. They mirror the mandatory GitHub
Actions checks. A release cannot proceed with an unexplained failure.

### 6.1 Engineering and drawing contracts

From the repository root:

```bash
python calculations/verify_calculations.py
python calculations/contract_lint.py
python calculations/mutation_test.py
python calculations/generate_blueprints.py --check
python calculations/drawing_index.py --check
```

These commands verify the release; they are not permission to modify calculations during
release packaging. A failure returns to the owning developer for correction and review.
Do not weaken, skip or rewrite a gate to make the release pass.

### 6.2 Documentation and website gates

From `wiki/`:

```bash
npm ci
npm run check:refs
npm run lint
node scripts/gen-site.mjs --strict
npm run build
npm run check:site
```

Then return to the repository root:

```bash
git diff --check
git status --short
```

Review every remaining file in `git status --short`. The release branch may contain only
intentional release changes. Generated caches, temporary review files and another
developer's work are not release artifacts.

---

## 7. Review the release candidate

Open a dedicated release PR. Its description must provide:

- proposed tag and Design Guide version;
- link to the release document;
- exact list of included PRs or commits;
- CAD migration summary;
- changed technical values and their confidence tags;
- gates that remain open;
- output of every command in §6;
- confirmation that generated drawings were visually reviewed when changed;
- confirmation that no unrelated working-tree changes were included.

At least one reviewer must compare the release document against the actual diff. For a
CAD-baseline change, the reviewer must also compare the concise guide, Advanced Guide,
numerical owners and drawings. Approval of an earlier technical PR does not replace the
release-package review.

Merge only with all required CI jobs green. Use the repository's normal protected-branch
and PR policy; do not bypass it for a release.

---

## 8. Create the immutable tag

After the release PR is merged, update local `main` and confirm the exact merge commit:

```bash
git switch main
git pull --ff-only
git status --short
git log -1 --oneline
```

The worktree must be clean and the displayed commit must be the reviewed release commit.
Create and push an annotated tag:

```bash
git tag -a vX.Y.Z -m "Salamandra vX.Y.Z — RELEASE TITLE"
git show --stat vX.Y.Z
git push origin vX.Y.Z
```

Push the branch through the normal PR workflow before pushing the tag. Never tag an
unmerged release branch or move an existing public tag to another commit.

### 8.1 Optional GitHub Release page

If GitHub CLI is installed, the canonical release document can seed the public release
page:

```bash
gh release create vX.Y.Z --title "Salamandra vX.Y.Z — RELEASE TITLE" --notes-file docs/NN-release-vX.Y.md
```

Review the rendered notes before publishing. The GitHub Release page supplements the
repository release document; it does not replace it.

---

## 9. Post-release verification

After pushing the tag:

- confirm the tag resolves to the reviewed merge commit;
- confirm the calculation and documentation workflows are green on `main`;
- confirm the documentation site shows the new release and correct Design Guide version;
- open the concise guide, Advanced Guide, release notes and drawing index from the site;
- verify internal links and downloadable artifacts;
- announce the release with the explicit open gates and non-claims intact.

Record any packaging error as a correction. Do not silently edit history or move the tag.
If a published release is wrong, mark the problem clearly and issue a new patch release.

---

## 10. Release definition of done

- [ ] Scope is frozen and all included technical work is merged.
- [ ] Release number, guide version and wiki package version are deliberate and consistent.
- [ ] New release document is complete and marked `RELEASED`.
- [ ] README and documentation indexes identify the new current release.
- [ ] Concise and Advanced Design Guides agree.
- [ ] Justification, open points, ADRs and CHANGELOG reflect the release delta.
- [ ] Generated artifacts are current and visually reviewed when their sources changed.
- [ ] All engineering, drawing, documentation and website gates pass.
- [ ] Release PR is approved and merged to `main`.
- [ ] Annotated tag points to the reviewed merge commit.
- [ ] Documentation site and public release artifacts are verified.
- [ ] Remaining physical gates and limitations are stated publicly.
