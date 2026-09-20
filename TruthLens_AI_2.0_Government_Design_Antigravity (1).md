# TruthLens AI 2.0 — Government-Grade Frontend Design System
## Antigravity IDE / Claude Sonnet Thinking — Visual Source of Truth

**Project:** TruthLens AI 2.0  
**Purpose:** Multimodal misinformation, deepfake, and document-forgery verification  
**Target:** SIH 2026 / national-level hackathon demonstration  
**Frontend direction:** Light, institutional, Government-of-India-aligned web application  
**Primary visual reference:** Supplied TruthLens AI 2.0 screenshot, transformed from dark cyber/SaaS to a white institutional interface  
**Implementation target:** Preserve the existing frontend architecture and functionality; use React + TypeScript where already applicable.

---

# 0. NON-NEGOTIABLE DESIGN DECISION

Transform the current dark-blue/neon/cyber/SaaS appearance into a **predominantly white, light-gray, institutional government-style interface**.

The final product should feel like:

> **A serious Indian public-sector AI verification and digital-forensics platform professionally modernised for 2026.**

It must NOT feel like:
- startup SaaS
- cyber-security gaming UI
- crypto dashboard
- neon AI console
- futuristic sci-fi UI
- generic Tailwind admin template
- copied government website
- fake official government service

This file is for **TruthLens AI 2.0 only**. Do not introduce HimDrishti, Antarctic navigation, NCPOR, POLARIS, route planning, or unrelated concepts.

---

# 1. SOURCE OF TRUTH

Use these sources in order:

1. **Existing TruthLens product/functionality** — preserve routes, features, terminology and working behaviour.
2. **TruthLens research documentation** — preserve the six-agent architecture, claim-level verification, RAG, forensic tracks, calibrated trust/risk and explanation traceability.
3. **Supplied TruthLens screenshot** — preserve the recognizable content hierarchy: Home, Detection, Forensics, Analytics, Dashboard, About, hero, System Status, Verification Dashboard, AI Agent Pipeline, Recent Analyses and capability metrics.
4. **This design.md** — final visual source of truth.

The research documentation defines the six-agent pipeline as Claim Extractor, Evidence Finder, Fact Checker, Risk Assessor, Explainability Agent and Final Judge, with each agent assigned a distinct responsibility. fileciteturn5file0L45-L52

The research also defines claim-level evidence retrieval and structured outputs that can be inspected stage by stage. fileciteturn4file9L461-L477

---

# 2. GOVERNMENT AUTHENTICITY RULE

TruthLens is an SIH prototype, not an official Government of India service.

Therefore:

### Required

Show a clear prototype marker:

```text
SIH 2026 · PS 26188 · Prototype
```

### Allowed visual direction

A Government-of-India-style utility bar and institutional information hierarchy may be used as **design inspiration**.

### Do NOT

- claim official Government of India ownership unless formally authorised
- invent ministry deployment
- invent government certification
- use the State Emblem in a way that falsely implies official ownership
- invent a fake government seal
- claim "official Government service"
- claim "Digital India Initiative" unless actually authorised

Government-style appearance is a visual direction, not an ownership claim.

---

# 3. VISUAL OBJECTIVE

Within five seconds the first viewport should communicate:

1. Indian institutional/public-sector context
2. TruthLens AI 2.0 identity
3. verification/misinformation purpose
4. multimodal forensic analysis
5. evidence-backed verification
6. six-agent pipeline
7. system status
8. clear Start Analyzing action
9. SIH prototype context
10. accessibility

The desired impression is:

**credible + clean + scientific + trustworthy + technically advanced**

---

# 4. FINAL VISUAL LANGUAGE

## Background

The interface must be predominantly white.

```text
Page background   #F7F9FC
Surface           #FFFFFF
Soft surface      #F4F7FA
Border            #D8E0EA
Divider           #E4E9F0
```

## Primary colours

```text
Government Navy  #0B2A5B
Deep Navy        #08224A
Indian Blue      #1455A0
Primary Blue     #1D63C8
Light Blue       #EAF2FF
```

## Status colours

```text
Success           #18864B
Success BG        #EAF7EF
Warning           #B7791F
Warning BG        #FFF7E6
Danger            #B42318
Danger BG         #FFF0EF
Info              #1455A0
```

## Text

```text
Primary           #172B4D
Secondary         #425466
Muted             #667085
Disabled          #98A2B3
```

### Colour ratio

Aim for approximately:

```text
White / neutral surfaces  70–80%
Navy / blue               12–18%
Status colours              3–6%
Other accents               <3%
```

**Blue is an accent, not the page background.**

---

# 5. REMOVE THE OLD DARK THEME

The following are prohibited in the default interface:

```text
black full-page background
neon cyan
purple gradients
glowing borders
blue glows
glassmorphism
particle backgrounds
cyber grids
holographic cards
animated stars
futuristic circuitry backgrounds
```

Do not retain dark cards simply because they existed in the old screenshot.

---

# 6. TYPOGRAPHY

Primary font:

**Noto Sans**

Fallback:

```text
system-ui,
-apple-system,
BlinkMacSystemFont,
"Segoe UI",
sans-serif
```

Scale:

```text
Display  32 / 40 / 700
H1       28 / 36 / 700
H2       22 / 30 / 700
H3       18 / 26 / 700
Body     15 / 22 / 400
Strong   15 / 22 / 600
Small    13 / 18 / 400
Micro    11 / 16 / 600
```

Do not use decorative futuristic fonts.

---

# 7. HEADER — FINAL GOVERNMENT-STYLE STRUCTURE

The header is the most important visual credibility element.

## 7.1 Top utility bar

Desktop height: **36–42px**.

Use a restrained institutional navy background.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🇮🇳 Government of India ↗       Skip to main content | A− A A+ | ♿ | 🌐 English ▼ │
└──────────────────────────────────────────────────────────────────────────────┘
```

Left:
- approved/contextual Indian flag mark
- Government of India
- small external-link icon

Right:
- Skip to main content
- A−
- A
- A+
- Accessibility
- English dropdown

All controls must be real interactive controls.

### Accessibility behaviour

- Skip link focuses `#main-content`.
- A− decreases text scale within safe limits.
- A restores default scale.
- A+ increases text scale within safe limits.
- Accessibility opens accessibility help/settings.
- English selector is architected for future localisation.

---

# 8. INSTITUTIONAL BRAND HEADER

Height: **78–92px**.

White background.

Recommended structure:

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ [shield logo]  TruthLens AI 2.0                              [Admin]        │
│                AI-Powered Verification & Forensic Analysis Platform         │
│                SIH 2026 · PS 26188 · Prototype                               │
└────────────────────────────────────────────────────────────────────────────┘
```

The TruthLens shield logo should be compact, simple and readable at 32–64px.

## Shield logo direction

Use:

- shield silhouette
- verification/check mark
- navy outline
- blue inner field
- white negative space
- minimal geometry

Do not over-detail the logo.

Do not place official Government emblems inside the TruthLens logo.

---

# 9. PRODUCT NAME

The product name must always be:

**TruthLens AI 2.0**

Exactly one `2.0` in the wordmark.

Never render:

```text
TruthLens AI 2.0 2.0
```

or duplicate the product version beside itself.

Recommended lockup:

```text
TruthLens AI 2.0
AI-Powered Verification & Forensic Analysis Platform
SIH 2026 · PS 26188 · Prototype
```

---

# 10. PRIMARY NAVIGATION

Use a clean horizontal navigation:

```text
Home | Detection | Forensics | Analytics | Dashboard | About
```

Height: **52–58px**.

White background with a subtle bottom border.

Active state:
- blue text
- blue icon
- 2–3px blue bottom indicator
- optional very light blue active surface

Do not use giant rounded blue pills.

---

# 11. SYSTEM INFORMATION STRIP

Immediately below navigation.

Height: **56–64px**.

Show compact operational context:

```text
Data Updated        21 May 2026, 10:30 IST
System Status       All Systems Operational
AI Agents           6/6 Active
Evidence            RAG Enabled
```

If values are demonstration values, label them as demo/sample data rather than pretending they are live production telemetry.

---

# 12. HOME PAGE — HERO

The old dark hero becomes a white institutional hero.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ● TRUTHLENS AI 2.0 — NEXT GENERATION VERIFICATION SYSTEM                    │
│                                                                             │
│ Verify The Truth                                                           │
│ At AI Scale                                                               │
│                                                                             │
│ TruthLens AI 2.0 is a multimodal verification and forensic analysis        │
│ platform for misinformation, deepfake and document-forgery analysis.       │
│                                                                             │
│ [ Start Analyzing ]   [ Watch Demo ]             [shield/India visual]     │
│                                                                             │
│                                      ┌──────────────────────────────────┐   │
│                                      │ System Status                    │   │
│                                      │ AI Agents       6/6 Active       │   │
│                                      │ Systems         Operational      │   │
│                                      │ Last Updated    ...              │   │
│                                      └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

Keep the existing headline:

**Verify The Truth At AI Scale**

---

# 13. HERO ART

Use a subtle shield/verification visual with an abstract India/world evidence context.

Preferred:
- shield
- check mark
- abstract India silhouette
- evidence/document motif
- light network lines
- very pale blue background illustration

Avoid:
- dark globe
- glowing shield
- neon circuitry
- robot
- cyberpunk background
- giant 3D objects

The artwork supports the content; it must not dominate it.

---

# 14. HERO ACTIONS

Primary:

```text
Start Analyzing
```

Secondary:

```text
Watch Demo
```

Primary button:
- blue fill
- white text
- 6px radius

Secondary:
- white fill
- blue border
- blue text

No gradients or glow.

---

# 15. SYSTEM STATUS CARD

White panel with thin border and minimal shadow.

```text
System Status
────────────────────────
AI Agents              6/6 Active
Systems                Operational
Last Updated           21 May 2026, 10:30 IST
Evidence Retrieval     RAG Enabled
```

Use text + icon + status, never colour alone.

---

# 16. VERIFICATION DASHBOARD

Below the hero, use three major sections:

```text
Verification Dashboard | AI Agent Pipeline | Recent Analyses
```

### Verification Dashboard

Show the existing product metrics where available:

```text
98.4%   Accuracy
3.2s    Avg. Time
5,418   Total Analyses
```

If these are demo values, clearly treat them as demonstration data.

Add:

```text
Agent Pipeline Confidence
████████████████████░░ 94%
```

Only show a confidence metric if the application actually produces it or the value is explicitly marked illustrative.

---

# 17. METRIC CARD DESIGN

```text
Background  #FFFFFF
Border      #D8E0EA
Radius      6–8px
Padding     16–20px
Shadow      minimal
```

Metric number:
- 26–30px
- bold
- navy/blue

Do not use huge glowing numbers.

---

# 18. SIX-AGENT PIPELINE

Display the six agents clearly and consistently:

```text
01  Claim Extractor          Active
02  Evidence Finder          Active
03  Fact Checker             Active
04  Risk Assessor            Active
05  Explainability Agent     Active
06  Final Judge              Active
```

Responsibilities:

```text
Claim Extractor       Finds verifiable claims
Evidence Finder       RAG over web + Wikipedia
Fact Checker           Claim vs evidence verdict
Risk Assessor          Calibrated fake score
Explainability Agent   Builds reasoning chain
Final Judge            Verdict + trust score
```

These responsibilities are directly supported by the TruthLens research documentation. fileciteturn5file6L323-L347

---

# 19. PIPELINE VISUAL

Optional desktop visual:

```text
Claim
  ↓
Evidence
  ↓
Fact Check
  ↓
Risk
  ↓
Explanation
  ↓
Final Verdict
```

Use thin blue connectors and restrained icons.

Do not animate the entire pipeline constantly.

---

# 20. RECENT ANALYSES

Example structure:

```text
Recent Analyses

Press Conference Video       Real          10:28 AM
Deepfake Detection

News Article Screenshot      Fake          10:21 AM
Forgery Detection

Social Media Post            Review        10:15 AM
Misinformation

Document - Notice.pdf        Real          10:10 AM
Document Forensics
```

Use compact rows, not giant cards.

Status must include text.

---

# 21. CAPABILITY SUMMARY

Retain the recognizable TruthLens capability strip:

```text
6
AI Agents
Specialized

12+
Forensic Signals
Multi-Modal

RAG
Evidence Retrieval

3
Detection Modes
Real-time
```

Only show figures supported by the actual application or clearly mark them as demo values.

---

# 22. DETECTION PAGE

Detection is the primary workflow.

Preferred upload interface:

```text
┌──────────────────────────────────────────────────────────┐
│ Analyse Content                                           │
│                                                          │
│ Upload supported content or paste text                  │
│                                                          │
│       ┌────────────────────────────────┐                 │
│       │        Drag & Drop             │                 │
│       │       Browse Files              │                 │
│       └────────────────────────────────┘                 │
│                                                          │
│ [ Paste Text ]       [ Upload File ]                     │
│                                                          │
│ [ Start Analysis ]                                       │
└──────────────────────────────────────────────────────────┘
```

Do not use neon upload zones.

---

# 23. ANALYSIS PROGRESS

Make the actual pipeline visible:

```text
Analysis in progress

✓ Input received
✓ Claims extracted
✓ Evidence retrieved
● Fact checking
○ Risk assessment
○ Explanation
○ Final judge
```

Use a subtle progress bar and accessible status updates.

---

# 24. CLAIM-LEVEL VERIFICATION

Do not reduce everything to one giant TRUE/FALSE card.

Show:

```text
Verification Summary

Claim 01     Supported
Claim 02     Contradicted
Claim 03     Unverified
Claim 04     Supported
```

The research design explicitly uses discrete factual assertions and per-claim evidence verification. fileciteturn5file0L23-L31

---

# 25. EVIDENCE / RAG PANEL

For each claim:

```text
Claim #1
────────────────────────────
Claim:
[claim text]

Evidence:
[retrieved passage]

Source:
Wikipedia / Web

Verification:
Supported

[View Source]
```

The research documentation states that Evidence Finder retrieves evidence from Wikipedia and open web search, ranks passages and passes provenance metadata to Fact Checker. fileciteturn4file9L478-L489

Do not invent citations.

---

# 26. FINAL VERDICT

Use a strong but restrained result panel:

```text
FINAL VERDICT

LIKELY MISLEADING

Trust Score
0.31

Confidence
High

Risk Level
High
```

The exact values must come from the real application or be clearly marked demo data.

Keep these concepts distinct:

```text
Verdict
Trust Score
Fake Score
Confidence
Risk Level
```

Do not collapse everything into one arbitrary percentage.

---

# 27. EXPLAINABILITY

This is a major TruthLens differentiator.

Heading:

**Why did TruthLens reach this verdict?**

Show an expandable structured chain:

```text
1. Claims identified
2. Evidence retrieved
3. Claims compared against evidence
4. Forensic signals assessed
5. Risk score calculated
6. Final verdict produced
```

The Explainability Agent should be visually connected to the structured intermediate pipeline outputs, not presented as an unrelated chatbot response. The research explicitly describes the explanation chain as grounded in Claim Extractor, Evidence Finder, Fact Checker and Risk Assessor outputs. fileciteturn5file0L23-L31

---

# 28. FORENSICS PAGE

Show the actual forensic tracks.

### Text Forensics

```text
VADER
TextStat
spaCy
```

### Image Forensics

```text
ELA
EXIF Metadata
Noise Pattern Analysis
```

These are the research-defined text/image forensic components feeding the Risk Assessor. fileciteturn5file0L25-L31

Do not invent additional forensic engines.

---

# 29. IMAGE FORENSICS UI

Use a professional inspection layout:

```text
Original Image
      │
      ├── ELA View
      ├── EXIF Metadata
      └── Noise Pattern Analysis
```

Use side-by-side comparisons where useful.

No decorative charts without analytical meaning.

---

# 30. TEXT FORENSICS UI

Show actual supported outputs such as:

```text
Linguistic Signals

Sentiment
Readability
Linguistic patterns
Entity analysis
Stylistic anomalies
```

Map these to actual VADER/TextStat/spaCy outputs. Do not invent percentages.

---

# 31. ANALYTICS PAGE

Do not create a generic chart wall.

Use meaningful sections only:

```text
Verification Outcomes
Risk Distribution
Evidence Retrieval
Agent Performance
Forensic Signal Summary
```

Charts should explain system behaviour.

---

# 32. DASHBOARD PAGE

Operational overview:

```text
Total Analyses
Real
Fake
Unverified
High Risk

Agent Pipeline
Recent Analyses
Evidence Retrieval Status
System Health
```

Keep the page clean and information-dense.

---

# 33. ABOUT PAGE

Formal sections:

```text
About TruthLens AI 2.0
How It Works
Six-Agent Architecture
Forensic Analysis
Evidence Retrieval
Explainability
Research Foundation
```

No startup-style marketing wall.

---

# 34. TRUST / RISK / CONFIDENCE

Never use:

```text
AI Confidence: 98%
```

unless backed by a defined application metric.

Prefer:

```text
Trust Score: 0.72
Risk Level: Moderate
Confidence: 0.84

Evidence coverage: High
```

The research architecture specifically describes a calibrated fake score/risk level and a final confidence rating. fileciteturn5file0L28-L31

---

# 35. UNVERIFIED STATE

TruthLens must be comfortable saying that evidence is insufficient.

```text
UNVERIFIED

Available evidence is insufficient to confidently
classify this claim.

Evidence coverage: Limited

Recommendation: Manual review
```

Never force a binary verdict when the actual pipeline cannot support it.

---

# 36. PROVENANCE / AUDITABILITY

Expose:

```text
Source
Source Type
Retrieved At
Claim Matched
Evidence Status
Agent Stage
```

Where useful provide:

```text
Human View
Structured View
```

Do not dump raw JSON by default.

---

# 37. CARD SYSTEM

```text
Background  #FFFFFF
Border      #D8E0EA
Radius      6–8px
Padding     16–20px
Shadow      minimal
```

Do not put cards inside cards inside cards.

Prefer:

```text
section
 ├── heading
 ├── content
 └── action
```

---

# 38. BUTTON SYSTEM

Primary:

```text
Start Analyzing
Run Verification
View Results
```

Secondary:

```text
Watch Demo
View Evidence
Compare
View Details
```

Tertiary:

```text
Back
Cancel
Close
```

Avoid marketing phrases such as:

```text
Launch AI
Magic Detection
AI Magic
Optimize Everything
```

---

# 39. STATUS BADGES

Use compact rectangular badges with 4–6px radius:

```text
ACTIVE
REAL
FAKE
UNVERIFIED
REVIEW
SUPPORTED
CONTRADICTED
STALE
```

Always combine colour with readable text.

---

# 40. ICONS

Use one consistent icon family:

- Lucide
- Material Symbols
- accessible SVG icons

Avoid:

- emoji as functional icons
- 3D icon packs
- glossy icons
- cartoon icons
- mixed icon families

---

# 41. ACCESSIBILITY

Target **WCAG 2.1 AA-oriented implementation**.

Required:

- keyboard navigation
- visible focus states
- semantic HTML
- labelled controls
- accessible forms
- accessible tables
- skip link
- text resizing
- sufficient contrast
- reduced motion
- non-colour-only status indicators
- meaningful alt text
- screen-reader-friendly analysis status

Focus style:

```text
2px solid #1455A0
2px offset
```

---

# 42. MOTION

Motion communicates state only.

Allowed:

```text
150–250ms
```

Use for:

- tabs
- accordions
- analysis progress
- evidence expansion
- result reveal
- chart transitions

Avoid:

- page entrance animations
- parallax
- floating cards
- glowing pulses
- animated gradients
- particle effects

---

# 43. RESPONSIVE DESIGN

Primary SIH target:

```text
1440 × 900
```

Also support:

```text
1280 × 720
1024 × 768
mobile
```

Desktop is the presentation priority.

Mobile order:

```text
Utility bar
↓
Brand
↓
Navigation menu
↓
System status
↓
Hero
↓
Primary action
↓
Verification dashboard
↓
Agent pipeline
↓
Recent analyses
↓
Capability metrics
```

Do not force desktop tables onto mobile.

---

# 44. DARK MODE

Optional only.

Default is always:

**Light Institutional Mode**

Do not automatically switch to dark mode.

---

# 45. LOADING / ERROR / EMPTY STATES

Every major page needs all three.

### Loading

```text
Analysing content...
Extracting claims...
Retrieving evidence...
Running forensic checks...
```

Use skeletons where possible.

### Error

```text
Analysis could not be completed.

The verification pipeline did not receive enough
information to produce a reliable result.

[ Retry Analysis ]
[ View Diagnostics ]
```

### Empty

```text
No analysis selected.

Start an analysis to view verification results.
```

---

# 46. FOOTER

Formal, restrained footer:

```text
TruthLens AI 2.0
AI-Powered Verification & Forensic Analysis Platform

SIH 2026 · PS 26188 · Prototype

About       Resources       Policies       Accessibility

------------------------------------------------------------

This is an SIH 2026 prototype / demonstration system.
It is not an official Government of India service unless
formally authorised and deployed by the appropriate authority.
```

Do not falsely claim official government ownership.

---

# 47. CORE TRUTHLENS ARCHITECTURE VISUAL

The UI should make this understandable:

```text
MULTIMODAL INPUT
       ↓
FORENSIC SIGNALS
       ↓
CLAIM EXTRACTION
       ↓
EVIDENCE RETRIEVAL
       ↓
FACT CHECKING
       ↓
RISK ASSESSMENT
       ↓
EXPLAINABILITY
       ↓
FINAL JUDGE
       ↓
VERDICT + TRUST SCORE + CONFIDENCE
```

The research documentation describes the same sequential flow and says each agent produces structured, inspectable artifacts that support stage-wise debugging. fileciteturn4file9L461-L477

---

# 48. RESEARCH-BACKED UI PRINCIPLES

The research identifies four gaps that the TruthLens architecture addresses:

1. **Claim-level decomposition** → Claim Extractor + Fact Checker
2. **Native forensic integration** → text and image forensic tracks feeding Risk Assessor
3. **Calibrated trust output** → calibrated fake score/risk + final confidence
4. **Explanation traceability** → dedicated Explainability Agent over structured pipeline outputs

These relationships are explicitly documented in the research. fileciteturn5file0L20-L39

The UI should make all four visible.

---

# 49. NO BLACK-BOX VERDICT

Bad:

```text
FAKE
AI Confidence 98%
```

Good:

```text
VERDICT
Likely Misleading

Trust Score
0.31

Evidence
2 supported · 1 contradicted

Forensic Signals
Elevated

Reasoning
View verification chain
```

---

# 50. DEMO DATA RULE

If the frontend uses static/sample values, make that clear.

Acceptable labels:

```text
Demo Environment
Sample Analysis
Illustrative Data
```

Never fabricate:

- live production status
- government deployment
- certification
- real-world accuracy
- real user statistics
- real uptime

---

# 51. DESIGN TOKENS

Create or adapt:

```text
src/design-system/tokens.ts
```

Suggested:

```ts
export const colors = {
  navy: "#0B2A5B",
  deepNavy: "#08224A",
  blue: "#1455A0",
  primaryBlue: "#1D63C8",
  page: "#F7F9FC",
  white: "#FFFFFF",
  surface: "#F4F7FA",
  border: "#D8E0EA",
  divider: "#E4E9F0",
  text: "#172B4D",
  secondaryText: "#425466",
  mutedText: "#667085",
  success: "#18864B",
  warning: "#B7791F",
  danger: "#B42318",
  info: "#1455A0",
} as const;

export const spacing = {
  xs: 4, sm: 8, md: 12, lg: 16,
  xl: 24, xxl: 32, xxxl: 40,
} as const;

export const radius = {
  sm: 4, md: 6, lg: 8,
} as const;
```

Adapt rather than replacing an existing mature token system unnecessarily.

---

# 52. COMPONENT ARCHITECTURE

Preferred structure:

```text
src/
├── design-system/
│   ├── tokens.ts
│   ├── typography.ts
│   └── accessibility.ts
│
├── components/
│   ├── government/
│   │   ├── GovernmentUtilityBar.tsx
│   │   ├── AccessibilityControls.tsx
│   │   └── PrototypeBadge.tsx
│   ├── branding/
│   │   ├── TruthLensLogo.tsx
│   │   ├── TruthLensWordmark.tsx
│   │   └── InstitutionalHeader.tsx
│   ├── navigation/
│   │   ├── MainNavigation.tsx
│   │   └── Breadcrumbs.tsx
│   ├── verification/
│   │   ├── VerificationDashboard.tsx
│   │   ├── VerdictCard.tsx
│   │   ├── TrustScore.tsx
│   │   └── ConfidenceIndicator.tsx
│   ├── agents/
│   │   ├── AgentPipeline.tsx
│   │   ├── AgentStep.tsx
│   │   └── AgentStatus.tsx
│   ├── evidence/
│   │   ├── EvidencePanel.tsx
│   │   ├── EvidenceSource.tsx
│   │   └── Provenance.tsx
│   ├── forensics/
│   │   ├── TextForensics.tsx
│   │   ├── ImageForensics.tsx
│   │   ├── ELAPreview.tsx
│   │   ├── EXIFPanel.tsx
│   │   └── NoiseAnalysis.tsx
│   ├── analysis/
│   │   ├── UploadPanel.tsx
│   │   ├── AnalysisProgress.tsx
│   │   └── AnalysisResult.tsx
│   └── common/
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── Badge.tsx
│       ├── Alert.tsx
│       ├── DataTable.tsx
│       └── Skeleton.tsx
│
└── pages/
    ├── Home.tsx
    ├── Detection.tsx
    ├── Forensics.tsx
    ├── Analytics.tsx
    ├── Dashboard.tsx
    └── About.tsx
```

Use the existing project structure if it already provides equivalent components.

---

# 53. PAGE PRIORITY

## P0

1. Government utility bar
2. Institutional header
3. Navigation
4. Home
5. Detection
6. Verification Dashboard
7. Six-Agent Pipeline
8. Final Verdict
9. Evidence / Explainability

## P1

10. Forensics
11. Analytics
12. Dashboard

## P2

13. About
14. Settings
15. Admin details

Do not spend the first frontend pass on low-value settings screens.

---

# 54. SIH DEMO FLOW

Ideal demo:

```text
Home
 ↓
Start Analyzing
 ↓
Upload / Paste Content
 ↓
Analysis Progress
 ↓
Claim Extractor
 ↓
Evidence Finder
 ↓
Fact Checker
 ↓
Risk Assessor
 ↓
Explainability Agent
 ↓
Final Judge
 ↓
Final Verdict
 ↓
Evidence
 ↓
Why this verdict?
 ↓
Forensic details
```

---

# 55. THE REAL “WOW” MOMENT

Do not rely on flashy animation.

The strongest demo moment is:

> **A judge sees content pass through the six-agent pipeline and can inspect the evidence and reasoning behind the final verdict.**

Visual sequence:

```text
Content
 ↓
Claims appear
 ↓
Evidence appears
 ↓
Fact checks appear
 ↓
Forensic signals appear
 ↓
Risk updates
 ↓
Explanation appears
 ↓
Final verdict appears
```

---

# 56. GOVERNMENT STYLE ≠ OLD-FASHIONED

Do not make the interface look like a 2010 portal.

Use:

```text
Government information hierarchy
+
Modern responsive UI
+
Scientific data presentation
+
Accessible interaction
+
Clean white surfaces
+
Subtle modern interaction
```

Avoid:

```text
old gradients
clutter
tiny fonts
clipart
excessive borders
heavy rounded cards
```

---

# 57. ANTIGRAVITY / CLAUDE SONNET THINKING MASTER PROMPT

Paste this prompt after placing `design.md` in the project root.

```text
Read design.md completely before making any frontend changes.

You are implementing the TruthLens AI 2.0 frontend for SIH 2026.

MODE:
Use careful reasoning before editing. First inspect the existing frontend architecture, routes, components, styling system, assets and API integration. Reuse working code where possible. Do not blindly rewrite the application.

PRIMARY OBJECTIVE:
Transform the existing TruthLens AI 2.0 dark blue/neon/cyber/SaaS visual identity into a LIGHT, WHITE, INSTITUTIONAL, GOVERNMENT-OF-INDIA-ALIGNED interface.

THIS IS ONLY TRUTHLENS AI 2.0.
Do NOT introduce HimDrishti, Antarctic navigation, NCPOR, POLARIS, route planning or unrelated concepts.

Preserve TruthLens functionality, terminology and research-backed architecture.

VISUAL TARGET:
- predominantly white/light-gray background
- Government of India-style utility/accessibility bar
- formal institutional header
- TruthLens AI 2.0 shield verification logo
- navy/blue accents
- restrained cards
- professional tables
- six-agent verification pipeline
- evidence/provenance
- forensic analysis
- explainable verdict

DO NOT:
- use dark full-page backgrounds
- use neon/cyberpunk styling
- use purple gradients
- use glowing borders
- use glassmorphism
- add fake government ownership
- invent certification
- invent production metrics
- invent forensic tools
- duplicate “2.0” in the product name

AUTHENTICITY:
TruthLens is an SIH prototype. Show “SIH 2026 · PS 26188 · Prototype”. Do not claim that TruthLens is an official Government of India service unless formally authorised.

--------------------------------------------------
PHASE 1 — INSPECT
--------------------------------------------------
Inspect the existing project before editing:
- package.json
- source tree
- routing
- pages
- components
- CSS/Tailwind/theme system
- assets
- logo files
- API integration
- existing analysis flow

Reuse existing architecture where possible.

--------------------------------------------------
PHASE 2 — DESIGN SYSTEM
--------------------------------------------------
Implement/adapt the tokens from design.md.

Default background:
#F7F9FC

Surface:
#FFFFFF

Navy:
#0B2A5B

Blue:
#1455A0

Primary Blue:
#1D63C8

Border:
#D8E0EA

Text:
#172B4D

Success:
#18864B

Warning:
#B7791F

Danger:
#B42318

Use Noto Sans or the existing accessible equivalent.

--------------------------------------------------
PHASE 3 — HEADER
--------------------------------------------------
Build:
1. Government utility bar
2. Accessibility controls
3. TruthLens AI 2.0 shield logo
4. Product name
5. AI-Powered Verification & Forensic Analysis Platform
6. SIH 2026 · PS 26188 · Prototype
7. Admin area
8. Navigation

Top utility controls must be functional:
- Skip to main content
- A−
- A
- A+
- Accessibility
- English

Product name must be exactly:
TruthLens AI 2.0

--------------------------------------------------
PHASE 4 — HOME
--------------------------------------------------
Rebuild the dark hero as a white institutional hero.
Keep:
- Verify The Truth
- At AI Scale
- Start Analyzing
- Watch Demo

Add a subtle shield/verification visual.

Show System Status.

Then show:
- Verification Dashboard
- AI Agent Pipeline
- Recent Analyses
- 6 AI Agents
- 12+ Forensic Signals
- RAG Evidence Retrieval
- 3 Detection Modes

Use real application values where available; label demo values honestly.

--------------------------------------------------
PHASE 5 — SIX AGENTS
--------------------------------------------------
Preserve:
1. Claim Extractor
2. Evidence Finder
3. Fact Checker
4. Risk Assessor
5. Explainability Agent
6. Final Judge

Display their actual responsibilities from the TruthLens documentation.

--------------------------------------------------
PHASE 6 — DETECTION
--------------------------------------------------
Make Detection the main workflow.
Support the existing upload/paste flow.
Show:
Input → Claims → Evidence → Fact Check → Risk → Explanation → Final Verdict

Do not hide the pipeline behind one generic AI result.

--------------------------------------------------
PHASE 7 — VERDICT
--------------------------------------------------
Display separately:
- Verdict
- Trust Score
- Fake Score if available
- Confidence
- Risk Level
- Evidence summary
- Explanation

Do not invent metrics.

--------------------------------------------------
PHASE 8 — EVIDENCE + EXPLAINABILITY
--------------------------------------------------
Show claim-level evidence and provenance.
Make “Why this verdict?” traceable to structured pipeline outputs.
Do not generate disconnected chatbot-style explanations.

--------------------------------------------------
PHASE 9 — FORENSICS
--------------------------------------------------
Preserve the actual supported forensic components:
Text: VADER, TextStat, spaCy
Image: ELA, EXIF, Noise Pattern Analysis

Do not invent tools.

--------------------------------------------------
PHASE 10 — ACCESSIBILITY
--------------------------------------------------
Implement:
- keyboard navigation
- visible focus
- skip link
- text resize
- semantic headings
- accessible labels
- accessible tables
- colour-independent statuses
- reduced motion

--------------------------------------------------
PHASE 11 — RESPONSIVE
--------------------------------------------------
Test:
1440x900
1280x720
1024x768
mobile

Desktop is the SIH presentation priority.

--------------------------------------------------
PHASE 12 — VISUAL QA
--------------------------------------------------
Run the frontend and inspect the first viewport.
Verify:
1. Background is predominantly white.
2. No dark cyberpunk theme remains in default mode.
3. Government-style utility bar exists.
4. TruthLens AI 2.0 is spelled exactly once in primary branding.
5. There is only one “2.0” in the product name.
6. Shield verification logo is present and compact.
7. Six-agent pipeline is visible.
8. Evidence/reasoning path is understandable.
9. No HimDrishti/unrelated terminology exists.
10. No fake government ownership exists.
11. No fake production statistics were introduced.
12. Loading, error and empty states work.
13. Keyboard/accessibility controls work.
14. First viewport looks credible at 1440x900.

Do not stop at styling. The UI must make the underlying TruthLens architecture easier for an SIH judge to understand.
```

---

# 58. FINAL ACCEPTANCE CHECKLIST

## Branding

- [ ] TruthLens AI 2.0 correct
- [ ] no duplicate 2.0
- [ ] shield verification logo
- [ ] SIH 2026 / PS 26188 / Prototype visible
- [ ] no HimDrishti terminology

## Government-style UX

- [ ] Government of India utility bar
- [ ] Skip to main content
- [ ] A− / A / A+
- [ ] Accessibility
- [ ] English selector
- [ ] formal institutional header
- [ ] restrained navigation
- [ ] white/light background

## TruthLens functionality

- [ ] Detection
- [ ] Forensics
- [ ] Analytics
- [ ] Dashboard
- [ ] About
- [ ] six agents
- [ ] RAG/evidence
- [ ] trust score
- [ ] risk
- [ ] confidence
- [ ] explainability
- [ ] provenance

## Visual quality

- [ ] no neon
- [ ] no cyberpunk
- [ ] no dark default
- [ ] no excessive gradients
- [ ] no glassmorphism
- [ ] no giant rounded cards
- [ ] no fake AI gimmicks

## Technical quality

- [ ] responsive
- [ ] keyboard accessible
- [ ] visible focus
- [ ] semantic headings
- [ ] accessible forms
- [ ] accessible tables
- [ ] loading states
- [ ] error states
- [ ] empty states

---

# 59. FINAL DESIGN STATEMENT

The target is NOT:

> “Make an AI website look like a government website.”

The target is:

> **“Make TruthLens AI 2.0 look like a credible, modern Indian public-sector verification and digital-forensics system that uses advanced multi-agent AI.”**

The white institutional visual language is intentional: government-grade hierarchy and accessibility on the outside, advanced six-agent evidence-grounded verification on the inside.
