# ORDERS — Code — the viewer defect, REISSUED: `BF1` is answered, `BF2`–`BF4` have never been asked

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `3132674760dc1b88ce6eb1539d8d5f3817197cee3a43eed5b7f7af380a2747a1`
**bytes** = `4019`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **REISSUE of `ORDERS-Code-2026-08-19f-ADDENDUM-viewer-defect.md`, WHICH NEVER LANDED.** **The
> original does not exist in the repository and never did** — `F-047`, Planner. **Nothing in it was
> ever declined.**
>
> ⚠ Grounding `main @ ad1a8b7`, v100. **No GPU, no rental, no fold, no fit, no ingest.**

---

## §0 — The defect as observed, and it is the only copy of the text

**On 2026-08-18, `/census/A0AVI2` (FER1L5) rendered:**

```
Structure viewer unavailable (Failed to fetch dynamically imported module:
https://pharmfoldmdk.fly.dev/assets/3Dmol-C1c51mSE.js).
Confidence and provenance below still render.
```

⚠⚠ **This text survives only because it was pasted into a conversation. The order describing it was
never committed, so for five days the defect existed and the description of it did not.**

**⚠ Its fallback is a STAND-ASIDE**: the page returns `200`, reads complete, **and nothing goes red.**
**KEEL-1 V9 Principle 6: *if the answer is "it stands aside," it is not a guard.*** ⚠ **The fallback
is well-behaved, and that is exactly why it survived.**

---

## §1 — What `BF1` established, so it is not re-run

| probe | status | content-type |
|---|---|---|
| `/assets/3Dmol-MBA9E7yK.js` | **200** | `application/javascript`, 588,119 B |
| `/assets/index-…js` (control) | 200 | `application/javascript` |
| ⚠⚠ `/assets/does-not-exist-xyz.js` (control) | **404** | **`application/json`** |

⚠⚠ **The third probe is what earns the answer: a genuinely absent asset returns 404/JSON, NOT an SPA
fallback to `index.html`.** **So the server does no HTML fallback under `/assets/` at all, and the
classic cause — chunk served as `text/html`, dynamic import fails — is ruled out BY A CONTROL rather
than by inspection.**

⚠ **DELIVERY IS HEALTHY TODAY. That is not the same as *the defect is gone*** — **the hash in the
2026-08-18 error (`C1c51mSE`) is not today's (`MBA9E7yK`), so today's chunk is a different build.**

## §2 — ⚠⚠ Task UA — the question `BF1` cannot reach: was the fault EVER delivery?

**UA1 — ⚠ Does `/census/A0AVI2` render a working viewer at v100?** **Walk it.** ⚠⚠ **Report what the
page LOOKS like, not that a fetch returned 200** — *the whole defect was a `200` that meant a failure,
and a captured DOM is not a walk.*

**UA2 — ⚠ Is it `A0AVI2` alone, a subset, or every census page?** **Measured against the live surface,
not inferred from the route definition.** ⚠⚠ **Include one of `F-048`'s five-residue spans** — a
viewer failing on a 5-aa span may fail for a reason that has nothing to do with delivery.

**UA3 — Does the viewer mount on the cohort's `TargetView`?** ⚠⚠ **If it mounts there and not on
`/census/:id`, this was never an asset problem and `§1`'s whole table is the wrong table.**

**UA4 — ⚠ Can the 2026-08-18 build be identified at all?** **Did a deploy between 08-18 and v100
change the chunk hash from `C1c51mSE` to `MBA9E7yK`, and is there any record of what that deploy
contained?** ⚠⚠ **If the answer is *the defect was fixed incidentally by an unrelated deploy*, say so
plainly** — **that is a finding about how this project ships, not a resolution.**

## §3 — Task UB — the test, and it must be the discriminating one

⚠⚠ **A test asserting the viewer COMPONENT RENDERS will pass against this defect.** **The component
rendered; its dynamic import failed.** **Such a test tests the fallback.**

- **The assertion is that the MODULE RESOLVES**, not that a component mounted.
- ⚠ **Prove by revert: point the import at a nonexistent chunk and watch it redden.** **A test that
  stays green under that flip is testing nothing.**
- ⚠ **Check WHERE the red fires** — *an error-red and a failure-red are different objects.*

## §4 — ⚠ Not ordered

⚠⚠ **DO NOT FIX ANYTHING UNTIL `UA` REPORTS.** **If the fault was never delivery, every remedy in the
original table is the wrong remedy** — **and applying one removes the evidence that would identify
the right one.**
**No rental, no fold, no climb, no census scoring.**

## §5 — Report

⚠ **`UA1` and `UA3` first — between them they decide whether this is an asset problem at all.**
Then `UA2`'s scope · `UA4`'s deploy history · branch and tip · both invariants with their keys · the
gate without `.env`.
