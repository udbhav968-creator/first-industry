# Product Research Brief: Group 2 — Tech Stack Issues Finder

This document reconstructs the project assignment, client requirements, scope boundaries, and primary user stories in fulfillment of **Milestone 1 (Issue 1.2)** and **Milestone 3 (Issue 3.1)**.

---

## 1. Problem Statement & Research Gap

### The Real-World Challenge
Modern engineering organizations assemble software architectures from dozens of open-source frameworks, runtime engines, and third-party libraries. However, engineering teams face significant friction in maintaining dependency health:
- **Alert Fatigue & False Positives:** Traditional SAST and SCA tools flood developers with hundreds of CVE alerts for packages that are either unused, in transitive dead code, or where the reported vulnerability does not affect the specific version deployed.
- **Scattered Vulnerability Intelligence:** Security advisories (NVD, CVE, GitHub Security Advisory Database) are separated from lifecycle & deprecation data ([endoflife.date](https://endoflife.date)) and upgrade guidance.
- **Lack of Decision-Ready Prioritization:** Developers are presented with severity ratings without actionable upgrade effort estimations. A "Critical" patch that is backward-compatible takes 5 minutes to deploy, whereas an "Informational" deprecation that requires a major rewrite takes weeks.

### The Research Solution
**Tech Stack Issues Finder** accepts a minimal declaration of components and versions (e.g. `react@17.0.2`, `node@14.17.0`, `postgres@12.1`) and executes a targeted research pipeline that:
1. Queries public security and lifecycle repositories.
2. Applies strict **version-applicability filtering** (eliminating false positive alerts for non-matching version ranges).
3. Evaluates active vs. End-of-Life (EOL) status.
4. Generates a deterministic **Risk vs. Effort Prioritization Matrix** (1–5 scale) to provide actionable, risk-ranked upgrade paths.

---

## 2. Target Users

| User Persona | Primary Need | Value Proposition |
| :--- | :--- | :--- |
| **Tech Leads / Engineering Managers** | Stack audit before quarterly roadmap planning | Clear visibility into deprecations, upcoming EOL cliffs, and upgrade roadmaps |
| **Developers / Contributors** | Rapid checks during package upgrades | Instant answer to: *"Does upgrading component X from v1 to v2 fix our CVEs without breaking breaking changes?"* |
| **DevOps & Release Engineers** | Automated CI/CD dependency health checks | Machine-readable JSON reports detailing vulnerabilities and safe target versions |

---

## 3. User Stories

### Core User Story (Project Variant B):
> *"As a developer, I want to enter my exact stack components and active versions so that I can see only public advisories, CVEs, and EOL dates that affect my exact versions, alongside safe upgrade paths."*

### Detailed Epics & User Stories:

1. **Exact-Version Vulnerability Matching:**
   - *Given* a developer inputs `Node 18.17.0`
   - *When* the research engine analyzes CVEs
   - *Then* it includes only vulnerabilities where `18.17.0` falls inside the affected SemVer range, and completely excludes CVEs that only affect other major/minor releases (e.g. Node 20.x).

2. **End-of-Life (EOL) Deprecation Tracking:**
   - *Given* a component version that has passed official vendor support
   - *When* the report is generated
   - *Then* the report highlights the sunset date, warns of unpatched zero-day risks, and suggests the earliest maintained LTS version.

3. **Effort-vs-Impact Upgrade Matrix:**
   - *Given* an identified advisory and recommended fix
   - *When* the recommendation is rendered
   - *Then* it assigns an **Impact Score (1–5)** based on severity and an **Effort Score (1–5)** based on SemVer migration delta (patch vs minor vs major).

---

## 4. Scope Boundaries

### Explicitly In Scope:
- Public security advisories (CVE, NVD, GHSA, vendor bulletins).
- Open-source lifecycle schedules ([endoflife.date](https://endoflife.date)).
- Server-side SemVer range validation and version applicability.
- Safe, public upgrade documentation links.
- 100% public information only.

### Strictly Out of Scope:
- **No private repo access:** Never requires user source code or GitHub personal access tokens with repo write access.
- **No active network scanning:** The service never performs port scanning, penetration testing, or endpoint probing against customer infrastructure.
- **No exploit generation:** Exploit proofs-of-concept (POCs) and attack payloads are filtered out to maintain developer safety and ethical standards.

---

## 5. Open Questions for the Client

1. **CVSS vs. Exploitability (EPSS):**
   * *Question:* Should advisory severity rely strictly on NIST CVSS v3.1 base metrics, or would the client prefer incorporating EPSS (Exploit Prediction Scoring System) probability scores to reflect real-world exploit availability?
2. **Upgrade Path Strategy:**
   * *Question:* When a component requires a multi-version jump (e.g. `Node 14` to `Node 20`), should the system output intermediate stepped hops (`14 -> 16 -> 18 -> 20`) to aid gradual migration, or present the single latest LTS target?
