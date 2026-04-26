# snowflower test methodology

**Version 0.1 · 2026-04-26 · DRAFT — open for community review**

> snowflower's reviews are only as trustworthy as the methodology underneath them. This page defines exactly how we measure hands-free input devices, what we deliberately don't measure, and what conflicts of interest we hold. Open to revision via GitHub Issues. Every published review carries a footer linking back to the methodology version it was tested against.

---

## Why this exists

Most tech reviews of accessibility devices stop at "I tried it, here's how it felt." That fails clinicians, who need repeatable numbers to justify procurement to insurance, schools, VA, or KEAD. It fails buyers with progressive conditions, who need to know how a device performs after 30 minutes of fatigue — not just out of the box.

snowflower's methodology is derived from established human-computer interaction (HCI) standards and adapted for accessibility-input devices. It is **published openly** so anyone — vendor, clinician, researcher, competitor — can reproduce, dispute, or improve it.

---

## Test categories (six)

| # | Category | Purpose | Primary metric |
|---|---|---|---|
| 1 | Performance | Throughput a competent user achieves under steady-state | bits/sec (Fitts's law) + WPM (text entry) |
| 2 | Setup | Time and friction to first usable cursor | Minutes from unboxing to verified click |
| 3 | Sustainability | Performance decay over realistic use session | Throughput retention % at 30 min |
| 4 | Compatibility | Where the device works without workarounds | Verified OS × app matrix |
| 5 | Funding & access | Real cost to a real buyer | Out-of-pocket $ by funding path |
| 6 | Practical | Daily-use reality (battery, charging, public-comfort) | Hours of continuous use |

---

## 1 · Performance

### 1.1 Pointing throughput (ISO 9241-411 Fitts's law)

We use the multi-directional tapping task from ISO 9241-411:2012, Annex B. The user clicks alternating targets of width *W* and amplitude *A*. The Index of Difficulty is `ID = log₂(A/W + 1)`. **Throughput** is `TP = ID / MT`, in bits/second, where MT is mean movement time. We use four difficulty levels (ID = 2, 3, 4, 5 bits) and five trials per level after a 20-trial warmup.

**Apparatus.** Custom Python harness using `pygame` running on a fixed reference machine (M3 MacBook Air, macOS 26.x, 13.6" display, 60Hz, brightness 50%). Cursor input untouched between input device and OS event queue. Raw event log recorded.

**Reporting.** Mean throughput ± 1 SD across the full session. Per-difficulty breakdown plotted.

**Limit.** Throughput depends on user motor capability. Our reference users are non-disabled testers; we report this number as a *device performance ceiling*, not a clinical benchmark. See Section 7 on user-driven testing.

### 1.2 Text entry rate (WPM, error-corrected)

Standard MacKenzie/Soukoreff phrase set (40 short phrases). User transcribes each phrase using only the device under test plus the OS's accessibility text-entry method (dwell-click keyboard, Switch Control scanning, AssistiveTouch typing, Apple Voice Control dictation, etc.).

**Reporting.** Adjusted Words-Per-Minute (Soukoreff & MacKenzie 2003) and total error rate %. Per-input-mode breakdown when device exposes multiple modes.

### 1.3 End-to-end latency

Time from physical input to on-screen cursor movement. Measured by filming a 240fps camera pointed at both the user's input action and the screen, then frame-counting. Reported as median of 30 trials.

**Why this matters.** Latency above ~80ms is perceptible; above 150ms degrades fine pointing measurably. Vendors rarely publish this honestly.

---

## 2 · Setup

### 2.1 First-use calibration time

Stopwatch from unboxing to first verified successful click in the OS. Includes hardware setup, app/driver install, OS permissions dialogs, account registration, and any required calibration routine. Measured by a tester following only the official documentation.

**Reporting.** Minutes:seconds + a per-step breakdown so failure points are visible.

### 2.2 Recurring calibration time

Time required at the start of a typical day-2 session. Some devices require recalibration after every wear; others persist.

### 2.3 Required ancillary purchases

Mounts, cables, app subscriptions, dental fittings, prescription requirements. Included in real cost (Section 5).

---

## 3 · Sustainability (the fatigue test)

### 3.1 Throughput retention at 30 minutes

Run the ISO 9241-411 task three times: at minute 1, minute 15, and minute 30 of continuous use. Report **throughput retention %** = TP(30 min) / TP(1 min). A device that holds 90%+ retention is sustainable for clinical/work use; anything below 70% is a short-session-only device regardless of peak performance.

### 3.2 Subjective workload (NASA-TLX)

Standard 6-dimension NASA-TLX questionnaire administered immediately after the 30-min session. Reported as raw weighted score and per-dimension breakdown (mental, physical, temporal, performance, effort, frustration).

### 3.3 Perceived exertion (Borg CR10)

User rates physical exertion on the Borg CR10 scale at minute 1, 15, and 30. For oral devices we additionally ask about jaw / tongue / palate-specific discomfort; for head-mouse devices, neck-specific.

### 3.4 Wear-time tolerance (worn devices only)

For devices worn on the body (MouthPad, Glassouse, Quha headband): how many continuous hours before the user reports they want to remove it. Measured by 4-hour test session with check-ins every 30 min.

---

## 4 · Compatibility

### 4.1 OS × app matrix

We verify each device on:
- **OS:** macOS 26, iOS 26, iPadOS 26, Windows 11/12, Android 16, ChromeOS
- **App:** Safari, Chrome, MS Office, Google Workspace, Slack, Zoom, VS Code, Adobe Creative Cloud, generic File Manager, generic Settings panel
- **Accessibility framework integration:** Apple Switch Control, Apple AssistiveTouch, Windows Eye Control / Narrator, Android Switch Access, ChromeVox

**Reporting.** Pass / partial / fail for each cell, with notes on what "partial" means.

### 4.2 Custom-mapping support

Whether the user can rebind gestures, dwell timings, scan rates. Some devices are locked; some are wide-open. Documented in a per-device feature matrix.

---

## 5 · Funding & access

### 5.1 Out-of-pocket cost by funding path

For each device, we publish the actual out-of-pocket cost a buyer faces under each path:

- US: cash sale · private insurance · Medicaid · Medicare Part B (DME) · VA · K-12 IEP · State VR · Section 503/508 · State AT Lending Library
- KR: 자비 · 건강보험 급여 · 의료급여 · KEAD 보조공학기기 지원 · KNAT 장애인보조기기 교부 · 산재보험 · 보훈
- UK: cash sale · NHS AT services · Access to Work
- EU: where vendor sells

Where coverage is unavailable or denial is common, we say so explicitly. Where dedicated funding-navigation teams exist (e.g. Tobii Dynavox Funding Services), we describe how to engage them.

### 5.2 Required clinician documentation

What documents the buyer's funding path requires (LMN, SLP eval, OT eval, CMN, IEP attachment) and what those typically include for *this* device class.

---

## 6 · Practical

| Metric | Measured how |
|---|---|
| Battery life (continuous use) | Stopwatch from full charge to shutdown under steady cursor activity |
| Charging time | Stopwatch, full discharge to full charge |
| Weight / size | Digital scale, calipers |
| Bluetooth connection reliability | Disconnect events per 4-hour session |
| Public-use comfort | Subjective per disabled co-host; documented as a stated quote, not a number |
| Maintenance / cleaning | Vendor instructions + tester notes |

---

## 7 · User-driven testing (the most important section)

### 7.1 Why non-disabled benchmark numbers are insufficient

A non-disabled tester driving a MouthPad scores a particular throughput; a person with C2 SCI scores something different. Both numbers are real, but only the second matters to the buying decision.

**Every published snowflower review includes at least one disabled co-host as the primary tester** for the headline performance numbers. Their performance, not the non-disabled benchmark, is what we lead with. Non-disabled numbers are reported as a *device-performance ceiling* in an appendix.

### 7.2 Co-host compensation and editorial control

- Disabled co-hosts are paid at or above the prevailing rate for editorial work in their region (snowflower starts at $200/episode and scales with audience).
- Co-hosts review the script before recording.
- Co-hosts have a final-cut veto on any scene depicting them, no questions asked.
- This is not negotiable. snowflower will publish without a non-disabled tester before it publishes without a disabled one.

### 7.3 Sample-size honesty

We test with whoever we can, and we name them. We do not extrapolate "MouthPad is great for SCI" from one C5-tetraplegic tester. We say "Maria, C5 incomplete, achieved X bits/sec after 90 min of practice."

---

## 8 · What we deliberately don't measure

| | Why |
|---|---|
| Subjective "joy of use" or "feel" without anchor | Unreproducible; vendors weaponize positive vibes |
| Whether a device "improves quality of life" | Not measurable in a 30-day editorial review; requires longitudinal clinical study |
| Comparisons to non-comparable devices (e.g. MouthPad vs Tobii eye tracker) without an explicit task framing | Apples-to-oranges absent a task; we instead set a *task* and benchmark every device that can plausibly do that task |
| Future versions / unreleased features | We review what ships, on the date we tested |

---

## 9 · Conflicts of interest

Updated per review. As of 2026-04-26:

- snowflower is **unaffiliated** with Augmental, Tobii, Quha, Glassouse, Microsoft, Apple, Google, or any other vendor named in this methodology.
- snowflower's eventual goal includes pitching a sponsorship or content-partnership relationship to Augmental at the 90-day mark. This is disclosed transparently. If the relationship begins, future reviews of MouthPad will carry a sponsored-disclosure footer per `DISCLOSURE.md`, and the methodology applied will be unchanged.
- snowflower receives no compensation from any device vendor as of this methodology version.

---

## 10 · Open data

Every published review will include:

- Raw Fitts's law trial logs (CSV)
- NASA-TLX and Borg responses
- The exact apparatus version and software versions used
- Any vendor firmware version under test

Hosted at `github.com/ksk5429/snowflower/tree/main/data/<episode_id>/` once first review ships.

---

## 11 · Methodology versioning

This document is versioned. Every review references the methodology version it used. When we update methodology, we re-test prior devices against the new version where feasible.

| Version | Date | Notes |
|---|---|---|
| 0.1 | 2026-04-26 | Initial draft. Open for community review via GitHub Issues. |

## 12 · How to dispute

Open an Issue at `github.com/ksk5429/snowflower/issues` with the tag `methodology`. Vendors with concerns about a specific test apparatus or scoring rubric are explicitly welcomed. We will respond publicly, on the issue thread, and update methodology where the dispute is well-founded. Methodology change history is a permanent appendix to this page.
