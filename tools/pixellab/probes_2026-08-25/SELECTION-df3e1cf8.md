# SELECTION RECORD — review object `df3e1cf8`

**Recorded at selection time**, per `docs/PIXELLAB-VERIFIED.md` §5 and §4. This file exists
because the reasoning is the part that gets lost: Gemfall had its reasoning in full
(`batch1r/evidence/promote.txt`) and was still missing the API call and a machine-readable
record.

| | |
|---|---|
| review object | `df3e1cf8-cded-4e8c-82e8-98226f95b4eb` |
| created by | `POST /v2/create-1-direction-object`, `size: 32`, `view: "top-down"` |
| prompt | *"skeleton warrior with rusted iron sword and tattered cloak, chunky, minimal detail, bold shapes"* |
| candidates | **64** (`n_frames`, declared in the create response) |
| **selected** | **frame 42** → promoted object `4504566c-b99e-430c-bdb1-3b6b2fa732cc` (`completed`) |
| contact sheet | `obj_review_frames.png` |
| promoted sprite | `promoted_frame42.png` |

## Why frame 42

Judged against the register ruling in `PIXELLAB_CONVENTIONS.md` — *chunky, minimal detail,
bold shapes, thick outline* — at native 32px, not zoomed.

- Clearest skull read at size; the eye sockets survive as shapes rather than noise.
- Strong unbroken silhouette — reads as one figure, not a cluster.
- The rusted sword reads **as a sword**, not as a stray diagonal, which most of the
  sword-bearing candidates fail.
- Warm cloak holds value separation against the bone; light bone over dark cloth.
- Thick continuous outline, no fine interior detail.

## Why not the others

- **9, 14, 17, 22, 34, 44, 53, 58** — the cloak occludes the skeleton entirely. Wrong
  subject: these are hooded figures, not skeleton warriors.
- **2, 20, 26** — value too flat, reads grey-on-grey; fails at size.
- **7, 23, 39, 62** — green cast, off-register against the rest of the set.
- Every remaining sword-bearer — the blade reads as a diagonal artefact rather than a weapon.

## Disposition of the parent

⚠ **Promoting one frame does NOT clear the review state.** Measured: after promoting frame
42, the parent remained `status: review` with **63 frames** — corroborating
`PIXELLAB-VERIFIED.md` §1.5 as **[API]** on our own account.

The parent was then explicitly dismissed via `POST /objects/{id}/dismiss-review`; a
subsequent `GET` returns **404 Object not found**. **YARL leaves no review object behind.**

⚠ **This was a probe, so dismissal was correct here. It would be wrong on production work** —
the 63 passed-over candidates are evidence (§1.5), and once dismissed they are gone.

## Costs measured on this object

| call | cost |
|---|---|
| `POST /objects/{id}/select-frames` | **0** (settled over 40 s) |
| `POST /objects/{id}/dismiss-review` | **0** (settled over 40 s) — ⭐ a Gemfall unknown, now measured |

⚠ **Schema note, learned from a free rejection:** the REST field is **`indices`**, not
`frame_indices`. Sending `frame_indices` returns 422 with both `missing` and
`extra_forbidden` details — a precise, self-documenting error, and free.
