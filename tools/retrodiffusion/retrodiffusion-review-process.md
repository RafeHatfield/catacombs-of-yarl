# Your custom style runs on RD Pro, the label is wrong

**The `'model': 'rd_fast'` you see in responses for `user__oryx_16_bit_fantasy_style_d970121a` is a misleading label — your custom style is definitively running on RD Pro under the hood.** The $0.18 flat per-image charge is the single unambiguous fingerprint of an RD Pro inference; no other tier in Retro Diffusion's pricing schedule produces that number at any resolution. The official `Retro-Diffusion/api-examples` README states flatly that `POST /v1/styles` *"currently supports only the RD Pro user template. All non-template fields are rejected."* So both of your calls — the `user__*` one and the `rd_pro__fantasy` one — are the same model class being billed the same way; only the response's `model` string disagrees, and that field is not authoritative. The practical consequence: you're paying RD Pro prices, getting RD Pro capabilities, and the field you've been using to distinguish them is essentially cosmetic.

This matters because a lot of downstream decisions — quality expectations, cost budgeting, and whether to keep the custom style at all — hinge on understanding what's really executing. Below is what the docs, pricing math, and architecture actually say.

## The pricing math only fits one model

Retro Diffusion publishes three distinct cost formulas in the official README, and $0.18 matches exactly one of them:

| Model | Formula | Cost at 64×64 | Cost at 256×256 |
|---|---|---|---|
| `rd_fast` | `max(0.015, ((w·h)+100000)/6,000,000)` | **$0.017** | $0.028 |
| `rd_plus` | `max(0.025, ((w·h)+50000)/2,000,000)` | $0.027 | $0.058 |
| `rd_pro` | **Flat `$0.18 × num_images`** | **$0.18** | **$0.18** |

A real `rd_fast` call at 64×64 would cost you **$0.017**, not $0.18 — roughly a 10× discrepancy. **The fact that both your `user__oryx_16_bit_fantasy_style_d970121a` and `rd_pro__fantasy` calls billed identically at $0.18 is proof they ran on the same model.** The charge against USD balance rather than free credits is also unrelated to model choice: Astropulse announced the full credits-to-USD migration in November 2025 on X, and all tiers now bill from the same USD balance with signup credits auto-converted.

## The `model` response field is a label, not a routing truth

The README never formally defines what the `model` field means, but its own examples give the game away. When you pass `check_cost: true`, responses return `"model": "check_cost"` — a value that is obviously not a real neural network. That alone proves **the field is a server-side tag, not a guaranteed identifier of which model actually ran.** The `img2img.py` example in the same repo even references an undefined `model` variable in its payload construction, suggesting the parameter is partially legacy plumbing left over from an earlier API era.

A further hint: the unofficial `@superbuilders/retrodiffusion` TypeScript SDK on npm types the field as only `'rd_fast' | 'rd_plus'` — it predates RD Pro entirely. The backend likely inherited similar legacy categorization code paths, so `user__*` styles created against newer infrastructure can surface with whatever historical label the routing layer attaches, regardless of actual execution. **For programmatic decisions, trust `balance_cost` and the `prompt_style` prefix, not the `model` string.**

## What `/v1/styles` actually creates

Every field the endpoint accepts is shaped for RD Pro specifically: `reference_images` (max 1), `reference_caption`, `apply_prompt_fixer`, `llm_instructions`, `expanded_llm_instructions`, `user_prompt_template`, `force_palette`, `force_bg_removal`, and a `min_width`/`min_height` range of **96–256**. That size range is RD Pro's native range verbatim. None of these parameters exist for RD Fast or RD Plus — they have no LLM prompt expansion, no stored reference conditioning, and no prompt-fixer pipeline.

Mechanically, a user style is **not a LoRA fine-tune.** Style creation is instant because the backend just stores a conditioning template: your reference image + your prompt template + palette/background flags + LLM instructions. At inference time, that template is spliced into an RD Pro run. This is closer to an IP-Adapter-style reference conditioning than a trained model. True LoRA training exists only in Astropulse's older locally-runnable Aseprite extension, not in the cloud API.

## The quality question: custom style vs `rd_pro__fantasy` for Oryx-style sprites

Both approaches run on the same RD Pro backbone, so the **quality difference is entirely about conditioning strength, not model capacity.** Your custom `user__oryx_16_bit_fantasy_style_d970121a` bakes in one Oryx reference image plus any LLM instructions and prompt template you wrote — meaning every generation is biased toward that specific 16-bit Oryx palette, outline weight, and shading convention. `rd_pro__fantasy` uses Retro Diffusion's internal fantasy conditioning, described officially as *"bright colors, soft transitions, detailed textures, light dithering, and outlines"* — a more generic fantasy-pixel aesthetic that won't lock to the Oryx look.

**For matching a specific tileset style, the custom user style should produce noticeably more consistent Oryx-flavored output** — same palette tendencies, similar sprite silhouettes, comparable shading. `rd_pro__fantasy` will be more varied and less on-model. Neither is technically "better"; they're differently constrained.

However, there's a critical technical gotcha for your use case: **RD Pro (and therefore your custom style) cannot natively generate 16×16 or 24×24 images.** The `min_width`/`min_height` floor of 96 is enforced at style creation, and RD Pro's native range is 64×64–256×256. Any 16×16 or 24×24 output you're seeing is being downscaled server-side or post-processed from a larger canvas, which loses the per-pixel intentionality that gives Oryx sprites their readability at native resolution.

## What you should actually use for 16×16 and 24×24 Oryx sprites

If authentic low-resolution pixel art at native size is the goal, **RD Pro is the wrong tool** — including your custom style built on it. Retro Diffusion has dedicated low-resolution styles on the cheaper tiers:

- **`rd_plus__low_res`**, **`rd_plus__classic`**, **`rd_plus__mc_item`**, **`rd_plus__skill_icon`**, and **`rd_plus__topdown_item`** all natively generate down to 16×16 or 32×32. These use a special low-res pricing formula (~$0.02–0.03 per image) and were trained for sub-96px native output.
- **`rd_fast__low_res`**, **`rd_fast__mc_item`**, **`rd_fast__mc_texture`** also support 16×16–128×128 at the cheapest rate (~$0.017).

A pragmatic workflow: use `rd_plus__low_res` or `rd_plus__classic` at 24×24 or 32×32 with an Oryx sprite as `input_image` (img2img at moderate strength, say 0.6–0.7) and an Oryx palette via `input_palette`. You lose persistent style identity but gain native resolution fidelity at roughly **1/9th the cost per image.** For strict style-locking you can still A/B it against RD Pro renders at 128×128 that are then downscaled with nearest-neighbor — but expect the custom style to be better at 128px output than at 24px.

## How to definitively confirm which model ran

Since the `model` field is unreliable, use these signals instead, in order of confidence: **actual `balance_cost` charged** (the only unambiguous tell — $0.18 = RD Pro, $0.017–0.058 = Fast/Plus per the formulas above), the **`prompt_style` prefix** you sent (`rd_fast__*`, `rd_plus__*`, `rd_pro__*`, or `user__*` which maps to RD Pro per the endpoint contract), and the **capability surface** (if your request accepted `reference_images` arrays, LLM instructions, or ≤256px-only sizing, it was RD Pro). A controlled test you can run yourself: generate the same prompt at 64×64 through `user__oryx_...`, `rd_pro__fantasy`, and `rd_fast__default`. The first two will cost $0.18 and produce visibly similar detail/style-adherence characteristics; the third will cost $0.017 and produce noticeably different output. That cost gap is your ground truth.

## Conclusion

Your custom Oryx style and `rd_pro__fantasy` are the same underlying model with different conditioning; the `model` field disagreement is a legacy labeling artifact, not a routing difference. You're paying RD Pro prices correctly in both cases. **The real decision isn't "which model label is right" — it's whether RD Pro's minimum 96×96 native resolution is appropriate for 16×16/24×24 Oryx sprites at all.** For native low-res sprite work that matches a specific 16-bit tileset, the cheaper `rd_plus__low_res`/`rd_plus__classic` styles with palette and img2img conditioning will likely serve better and cost an order of magnitude less; reserve your custom RD Pro style for larger showcase renders or concept art that you'll downscale deliberately.