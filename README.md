# snowflower

**An independent accessibility-input-tech channel and content engine.**
**눈꽃 — 손 없이 사는 사람들을 위한 입력 기술 리뷰.**

> Coverage of hands-free, eyes-free, and assistive input technology — MouthPad, Tobii, Quha, Glassouse, AssistiveTouch, and adjacent.
> Independent. Editorial. Fair-coverage. Not affiliated with any covered brand.

---

## Two outputs

| | What it is | Why it exists |
|---|---|---|
| **The engine** | A flat-folder Python content pipeline that takes one source asset and fans it out to YouTube / LinkedIn / Bluesky / Threads / TikTok / Instagram / Naver Blog / Reddit / newsletter | Sellable IP — eventually licensable to accessibility-tech vendors |
| **The channel** | snowflower — a real publishing brand running on the engine | Proof. Demonstrates the engine works in market before any pitch |

**Pitch arc:** Run snowflower for 90 days. Reach 5–15k followers across the stack. Pitch the proof to augmental.tech (and, if they pass, Tobii / Quha / Glassouse) as anchor sponsor or content lead.

See `pitch_deck.md`.

---

## Editorial scope

snowflower covers **hands-free and assistive input devices**, broadly:

- **Worn:** MouthPad^, Quha Zono, Glassouse, head-mouse arrays
- **Optical:** Tobii Eye Tracker 5, gaze-input research
- **Software:** Apple AssistiveTouch + Voice Control, Windows Eye Control, Android Switch Access, Talon Voice
- **Adjacent:** AirPods Live Speech, BCIs (Neuralink-class research), foot pedals, sip-and-puff

Coverage rule: **no exclusive promotion of any single brand**. Every episode covers multiple options or includes a comparison footer pointing to alternatives.

---

## Stack

| Tier | Platform | Role |
|---|---|---|
| 1 | YouTube long-form + Shorts | Hero (demos, mini-docs) |
| 1 | LinkedIn | B2B (schools, VA, Medicaid, OT/PT, insurers) |
| 1 | Bluesky | Tech-leaning audience, accessibility researchers |
| 2 | Threads | Cheap mirror |
| 2 | Instagram Reels | Visual mirror (post Meta App Review 1–4 wk) |
| 2 | TikTok | #DisabilityTikTok discovery (post audit 5–10 days) |
| 2 | X (Twitter) | AI/research-side reach (pay-per-use ~$5–17/mo) |
| 3 | Substack/Beehiiv | Owned newsletter |
| 3 | Reddit | r/disability, r/als, r/SCI, r/MultipleSclerosis, ... — **manual** |
| 3 | HN | Quarterly when SDK / OSS artifact ships — **manual** |
| KR-1 | YouTube KR | Korean voiceover + 자막 |
| KR-1 | LinkedIn KR | KEAD / 보건복지부 / 보조공학연구소 reach |
| KR-2 | Stibee newsletter | Korean OT/PT/특수교육 list |
| KR-2 | Naver Blog | Korean SEO (cron = 정지 risk → **manual**) |

Budget: $30 floor / $90 ceiling per month.

---

## Layout

Flat. All Python files at root. No package structure.

```
PROMOTION/
├── README.md, DISCLOSURE.md, pitch_deck.md
├── pytest.ini, requirements.txt, .gitignore, .env.example
├── snowflower.py            # CLI entry point
├── models.py                # Episode / Post / PublishResult
├── base_connector.py        # ABC
├── connectors_registry.py   # name → class map
├── measure.py               # metrics aggregator
├── connector_*.py           # 10 platform connectors
├── transformer_*.py         # 5 source-asset transformers
├── auth_*.py                # 3 OAuth/login helpers
├── ep001_episode.yaml       # source content for episode 001
├── template_*.md            # title formulas, disclosure footers
└── test_connectors.py       # smoke tests
```

---

## Quick start

```bash
# 1. Install deps into a venv
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt

# 2. Mint OAuth tokens (interactive, opens browser)
.venv/Scripts/python.exe auth_youtube.py
.venv/Scripts/python.exe auth_linkedin.py
.venv/Scripts/python.exe auth_bluesky.py

# 3. Run smoke tests
.venv/Scripts/python.exe -m pytest

# 4. Health-check all connectors
.venv/Scripts/python.exe snowflower.py health-check

# 5. Dry-run an episode (no API calls)
.venv/Scripts/python.exe snowflower.py publish --episode ep001_episode.yaml --dry-run

# 6. Live publish to selected platforms
.venv/Scripts/python.exe snowflower.py publish --episode ep001_episode.yaml --live --platforms youtube,linkedin,bluesky
```

---

## Status

Sprint 0 complete — scaffold + connectors + dry-run verified end-to-end.

**Account creation:** see `accounts_setup.md` for the work-along checklist with handle choices, bio templates, and per-platform OAuth instructions.

**Working with real API code:** Bluesky, YouTube, LinkedIn, Threads, Stibee.
**Stub-with-real-shape:** X (deferred to Sprint 2 once paid tier provisioned), TikTok (post-audit), Instagram (post-App-Review).
**Manual-only by design:** Reddit, Naver Blog.

Next: Sprint 1 — first real publish. Recommended source: `ep001_episode.yaml` (Apple AssistiveTouch primer; free, no hardware purchase).

See `DISCLOSURE.md` for legal disclosure templates (US FTC + Korea 표시·광고법).
