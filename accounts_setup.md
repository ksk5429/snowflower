# snowflower — accounts setup checklist

Work-along guide. Each section is self-contained: do the steps, paste the result into `.env`, check the box.

**Identity stance:** brand-only everywhere except LinkedIn personal profile (which is skipped — Company Page only).

**Bio template (paste verbatim, EN):**
> snowflower · independent editorial on hands-free & assistive input tech · MouthPad · Tobii · Quha · Glassouse · AssistiveTouch · disclosure: snowflower.tech/about

**Bio template (KR):**
> snowflower(눈꽃) · 손 없이 쓰는 입력 기술 독립 리뷰 · MouthPad · Tobii · Quha · Glassouse · AssistiveTouch · 광고·협찬 정책: snowflower.tech/about

---

## Pre-flight (do these first)

### [ ] 0.1 — Domain `snowflower.tech` (~$15/year)

- Go to **porkbun.com** or **namecheap.com**
- Search `snowflower.tech` — confirm available
- Register with the dedicated email below (after you create it)
- Enable WHOIS privacy (free at Porkbun, ~$5/yr at Namecheap)
- Skip if taken — pick `.io`, `.co`, `.app`, or `.dev` instead

### [ ] 0.2 — Gmail account `snowflower.editorial@gmail.com`

- accounts.google.com/signup
- First name: `snowflower`  ·  Last name: `editorial`
- Birthday: any plausible adult date (legal: must be 13+)
- Phone: skip if possible at signup; add later if needed
- After login: Settings → "Less secure app access" — leave OFF (we use OAuth, not passwords)

### [ ] 0.3 — Google Voice number (free, US)

- voice.google.com  →  sign in with `snowflower.editorial@gmail.com`
- Pick any US area code with available numbers (try Boston 617, NYC 212, SF 415)
- Verify with **your existing US number** (Google Voice needs a real phone for first-time activation; after that, it's standalone)
- Save the number to a password manager — every other platform's SMS verification will use this

### [ ] 0.4 — Profile picture (upload to all platforms)

- Generate at fal.ai (Flux/Nano Banana) with prompt: `minimalist snowflake mark, single 6-fold geometric snowflake, soft white on midnight blue, no text, vector style, square 1024x1024`
- OR commission $10 on Fiverr if you want hand-made
- Save as `profile_512.png` and `profile_1024.png`
- Gitignore'd; lives next to `.env`

---

## Tier 1 — Cron-publishable (do first, lowest friction)

### [ ] 1.1 — Bluesky (~2 min)

- bsky.app  →  sign up with `snowflower.editorial@gmail.com`
- Handle: `snowflower.bsky.social` (or `snowflower.tech` later via custom domain)
- Display name: `snowflower`
- Bio: paste EN template above
- Add profile picture
- **Settings → App passwords → Generate new** (label: "snowflower-engine")
- Paste into `.env`:
  ```
  BLUESKY_HANDLE=snowflower.bsky.social
  BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
  ```
- Verify: `python auth_bluesky.py`

### [ ] 1.2 — YouTube Brand Account (~10 min)

- youtube.com  →  signed in as `snowflower.editorial@gmail.com`
- Create channel  →  **"Use a custom name"** (NOT personal Google name)  →  `snowflower`
- This creates a **Brand Account** managed by your Google account but presented as snowflower (no person attached)
- Channel handle: `@snowflower` (claim if free; else `@snowflower-editorial`)
- About section: paste EN bio
- Upload profile picture + a 2560×1440 banner (placeholder OK for now)
- **Cloud setup (for API access):**
  - console.cloud.google.com  →  create project `snowflower-engine`
  - APIs & Services  →  Library  →  enable **YouTube Data API v3**
  - Credentials  →  Create OAuth 2.0 Client ID  →  **Desktop app**  →  download JSON
  - Save as `youtube_client_secret.json` next to `snowflower.py`
- Verify: `python auth_youtube.py`  (opens browser; sign in with snowflower.editorial@gmail.com; pick the snowflower brand channel)
- After success, paste channel ID into `.env`:
  ```
  YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxx
  ```

### [ ] 1.3 — LinkedIn Company Page (~20 min) — NO personal profile

- linkedin.com  →  Work icon (top right)  →  Create a Company Page
- Page name: `snowflower`
- LinkedIn URL: `linkedin.com/company/snowflower`
- Industry: **Media Production** (or **Online Media**)
- Company size: 1
- Type: Self-employed / Privately held
- Tagline (~120 chars): `Independent editorial on hands-free & assistive input tech.`
- About: paste long-form EN bio
- Upload logo + cover image (use profile_512 + a 1128×191 banner)
- **Verify ownership** (LinkedIn requires a personal account behind every Company Page admin) — this means:
  - You DO need a real LinkedIn personal account, but it acts as admin only and never publishes
  - Use your existing personal LinkedIn (or create one with your real name if you don't have one)
  - Add yourself as Page admin
- **Dev app for API:**
  - linkedin.com/developers  →  Create app  →  associate with snowflower Company Page
  - Products tab  →  request **"Share on LinkedIn"** + **"Sign In with LinkedIn using OpenID Connect"** + **"Marketing Developer Platform"** (last one needed for org posts; takes 1–2 weeks for review)
  - Auth tab  →  add redirect URI: `http://localhost:8765/callback`
- Paste into `.env`:
  ```
  LINKEDIN_CLIENT_ID=xxx
  LINKEDIN_CLIENT_SECRET=xxx
  ```
- Verify: `python auth_linkedin.py` (will save token + author URN; for Company Page posting, manually edit `LINKEDIN_AUTHOR_URN=urn:li:organization:<page_id>` in `.env`)
- **NOTE:** the `connector_linkedin.py` currently uses `w_member_social` scope. After Marketing Developer Platform is approved (~2 weeks), tell me and I'll patch it to `w_organization_social` for Company Page posting.

### [ ] 1.4 — Threads (~5 min, comes with Instagram)

- Skip until 1.5 (Instagram) is done — Threads piggybacks on the IG account
- After IG: threads.net  →  sign in with IG  →  port profile
- developers.facebook.com  →  Threads API  →  generate access token
- Paste into `.env`:
  ```
  THREADS_USER_ID=xxx
  THREADS_ACCESS_TOKEN=xxx
  ```

### [ ] 1.5 — Instagram Creator Account (~10 min sign-up; +1–4 weeks for App Review)

- instagram.com  →  sign up with `snowflower.editorial@gmail.com`
- Username: `snowflower` (likely taken; try `snowflower.editorial`, `snowflowerHQ`, `joinsnowflower`)
- Phone verification → Google Voice number from step 0.3
- Add bio + profile pic
- Settings → Account → **Switch to Professional**  →  **Creator** (not Business — Creator gives Insights API without forcing FB Page link)
- Category: Digital Creator
- For API:
  - developers.facebook.com  →  Create App  →  Type: **Business**
  - Add **Instagram Graph API** product
  - **Submit for App Review** for `instagram_content_publish` permission (1–4 weeks; provide a screencast of intended use)
- During wait, Instagram works manually-only. After approval, paste into `.env`:
  ```
  META_APP_ID=xxx
  META_APP_SECRET=xxx
  INSTAGRAM_BUSINESS_ACCOUNT_ID=xxx
  INSTAGRAM_ACCESS_TOKEN=xxx
  ```

### [ ] 1.6 — Beehiiv newsletter (~10 min) — **PRIMARY OWNED-AUDIENCE PLATFORM**

Per `research_findings.md`: Beehiiv beats Substack (0% take vs 10% forever) and Kit (no 23.5% sponsor-network cut). Auto-fill ad network covers tooling cost by ~1,200 subs.

- app.beehiiv.com  →  sign up with `snowflower.editorial@gmail.com`
- Publication name: `snowflower`
- Custom URL: `snowflower.beehiiv.com` (or `snowflower.tech` once domain points DNS)
- Logo + cover (use profile_512 + 1200×600 cover)
- Description: paste EN bio
- Settings → Customize → enable: Recommendations Network, Boosts, Ad Network (auto-fill)
- Settings → Integrations → API → generate key (label: "snowflower-engine")
- Find publication ID under Settings → Account → Publication ID
- Paste into `.env`:
  ```
  BEEHIIV_API_KEY=xxx
  BEEHIIV_PUBLICATION_ID=pub_xxxxxxxx
  ```
- Verify: `python snowflower.py health-check` should show `beehiiv: ready=OK`
- Test publish (creates a draft, NOT live): `python snowflower.py publish --episode ep001_episode.yaml --live --platforms beehiiv` — review draft in Beehiiv UI before clicking Send.

### [ ] 1.7 — X / Twitter (~5 min sign-up; defer paid API tier)

- x.com  →  sign up with `snowflower.editorial@gmail.com`
- Handle: `@snowflower` (likely taken; try `@snowflowerHQ`, `@snowflower_a11y`)
- Bio + pic + banner
- For posting via API, you need Basic tier ($200/mo) — **defer until ready**
- Sign-up only for now; manual posting works free

---

## Tier 2 — High-friction, do after Tier 1 is rolling

### [ ] 2.1 — TikTok (~10 min sign-up + 5–10 days API audit)

- tiktok.com  →  sign up with `snowflower.editorial@gmail.com`  →  Google Voice number
- Username: `snowflower` (try variants if taken)
- Switch to **Business Account**  →  Category: Education
- developers.tiktok.com  →  Create app  →  request **Content Posting API** scope
- Submit audit (privacy policy URL + demo video required) — **5–10 business days; can stretch 2 weeks**
- During wait, all API-posted content forced to private — manual posting only
- After audit pass:
  ```
  TIKTOK_CLIENT_KEY=xxx
  TIKTOK_CLIENT_SECRET=xxx
  TIKTOK_ACCESS_TOKEN=xxx
  ```

### [ ] 2.2 — Reddit (~5 min sign-up; 30–90 days warming)

- reddit.com  →  sign up with `snowflower.editorial@gmail.com`
- Username: `snowflower_editorial` (Reddit doesn't allow brand-only handles for new accounts that look spammy)
- Account needs **age + karma** before big subs let you post. Start commenting *thoughtfully* in r/disability, r/AssistiveTechnology now to warm.
- prefs/apps  →  Create script app  →  paste creds into `.env`:
  ```
  REDDIT_CLIENT_ID=xxx
  REDDIT_CLIENT_SECRET=xxx
  REDDIT_USERNAME=snowflower_editorial
  REDDIT_PASSWORD=xxx
  ```
- **Posting stays manual** (the engine refuses to auto-post Reddit by design — shadowban risk too high)

### [x] 2.3 — Newsletter platform decided: **Beehiiv** (moved to Tier 1.6)

Beehiiv chosen over Substack per `research_findings.md`. See section 1.6 above for setup.

---

## Tier 3 — Korean stack (defer until you have ≥1 month of EN content live)

### [ ] 3.1 — Stibee (Korean newsletter)

- stibee.com  →  sign in with `snowflower.editorial@gmail.com`
- Workspace name: snowflower
- Settings → API → generate AccessToken
- Create list (ID auto-assigned)
- Paste:
  ```
  STIBEE_API_KEY=xxx
  STIBEE_LIST_ID=xxx
  ```

### [ ] 3.2 — Naver Blog (manual posting only)

- naver.com  →  ID 가입 with `snowflower.editorial@gmail.com`
- 본인인증 needs Korean phone — defer if you don't have one
- Blog 개설  →  블로그명: `snowflower 눈꽃`
- developers.naver.com  →  Application 등록  →  request 블로그 글쓰기 권한
- Paste:
  ```
  NAVER_CLIENT_ID=xxx
  NAVER_CLIENT_SECRET=xxx
  ```
- **Posting stays manual** (cron = 정지)

### [ ] 3.3 — Maily (Korean newsletter alternative)

- maily.so  →  same flow as Stibee
- Either Stibee or Maily — both, only if you want A/B test

---

## Tier 4 — Defer indefinitely (or skip entirely)

| Platform | Status |
|---|---|
| KakaoStory | API dead since 2023-11 — skip |
| Tistory | API dead since 2024-02 — skip |
| Brunch | No API; manual only; defer until long-form library exists |
| Disquiet | No API; manual maker-log only |
| Mastodon | Free + works, but tiny audience for accessibility — skip unless you personally use it |
| Hacker News | Manual submission only; reserve for the 1–2 best pieces per quarter |

---

## Final state target

When all Tier 1 + chosen Tier 2 boxes are checked:

```bash
.venv/Scripts/python.exe snowflower.py health-check
```

Should show **green "OK" in the `ready` column** for: `bluesky`, `youtube`, `linkedin`, `threads`, plus whichever others you OAuth'd.

Then:

```bash
.venv/Scripts/python.exe snowflower.py publish --episode ep001_episode.yaml --live --platforms bluesky
```

…posts the first real artifact. Bluesky goes first because it's text-only (no video needed) and the lowest-stakes test of the live pipeline.
