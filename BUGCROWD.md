# BUGCROWD.md - Researcher Operating Policy (SOP + Terms Alignment)

Last updated: 2026-02-15  
Applies to: any testing, reporting, communication, and disclosure activity you perform via Bugcrowd ("Crowdcontrol", "Programs/Engagements", "Submissions").

This document is a practical governance/SOP for operating on the Bugcrowd platform while remaining aligned with Bugcrowd's published Terms of Service, Standard Disclosure Terms, Code of Conduct, Platform Behavior Standards, and Researcher documentation. It is not legal advice and does not replace the binding terms you accept on Bugcrowd. If there is any conflict, follow the controlling documents (see "Order of precedence").

---

## 1) Operating principles

1. **Authorization-first.** Only test what you are explicitly authorized to test, in the manner authorized, for the specific engagement you joined.
2. **Least impact.** Avoid actions that harm availability, integrity, or user data. Stop immediately if you see user data or service degradation.
3. **Confidential by default.** Treat program details, targets, findings, and communications as confidential unless you have explicit, documented permission to disclose.
4. **Professional conduct.** Communications are expected to be respectful, non-threatening, and within Bugcrowd's permitted channels.
5. **High-signal reporting.** Submit complete, reproducible reports. Avoid "placeholder" / low-detail submissions and low-impact noise.

---

## 2) Order of precedence (what rules win)

Bugcrowd's Website Terms describe a "Legal Terms" set that includes program briefs and "Researcher Terms and Conditions." They also state an explicit precedence hierarchy: **Program/Bounty Brief > Researcher Terms and Conditions > Website Terms of Service > Privacy Policy > other terms**.

Operationally:
- **The engagement's Program Brief is the top authority for scope, rules of engagement, disclosure policy, and reward conditions.**
- Bugcrowd's **Standard Disclosure Terms** apply across programs, unless the Program Brief states otherwise.
- Bugcrowd's **Code of Conduct** and **Platform Behavior Standards** govern behavior and enforcement.

---

## 3) Eligibility, account integrity, and access controls

### 3.1 Eligibility (baseline)
- Monetary eligibility is tied to being at least **18** (or age of majority where applicable) for compensation eligibility (see Standard Disclosure Terms).
- Bugcrowd's Website Terms include eligibility restrictions related to sanctions/denied-party lists and prohibit use by children under 13, with additional requirements for researchers.

### 3.2 Account rules (non-negotiable)
- Maintain **one account** only.
- Use **accurate and current** registration information.
- Do **not** use a third party's account.
- You are responsible for your account security; do not transfer the account.

These expectations appear in Standard Disclosure Terms and Website Terms.

### 3.3 Common "compliance gates" for private engagements
Some engagements require additional compliance steps before you can even view the brief:
- **NDA / compliance document signing** (private engagement access gate).
- **Two-Factor Authentication (2FA)** enablement.
- **Identity verification** (for some private programs) via Bugcrowd's third-party verification flow.

If an invitation indicates compliance requirements, complete them before doing any testing.

---

## 4) Scope management and safe testing boundaries

### 4.1 Scope = "Targets" in the Program Brief
- Test **only** the systems listed under the brief's **Targets** section. Anything else is **Out of Scope**.
- Unless the brief says otherwise, create dedicated **testing accounts** for your work.

### 4.2 Do not disrupt services
Bugcrowd's Standard Disclosure Terms prohibit actions that affect **integrity or availability** of targets and require you to **immediately suspend automated tools** if you observe performance degradation.

Practical rules:
- Prefer passive/low-volume validation over high-volume scanning.
- Throttle automation; schedule heavier checks off-peak when allowed by the brief.
- If a target slows down, errors spike, or you suspect an availability impact: **stop and reassess.**

### 4.3 Explicitly excluded / prohibited submission categories (platform baseline)
Bugcrowd's Standard Disclosure Terms list "Excluded Submission Types" that are not accepted/rewardable on the platform baseline, including:
- Physical security findings (e.g., office access).
- Social engineering-derived findings (e.g., phishing/vishing).
- Out-of-scope systems.
- UI/UX bugs, typos.
- Network-level DoS/DDoS.

Always check the Program Brief because some engagements can vary, but treat the exclusions as your default baseline.

### 4.4 Handling unintended access to data (PII/PHI/etc.)
Bugcrowd's Code of Conduct states:
- If you encounter user data (PII/PHI/card data/proprietary info), **limit access to the minimum needed to demonstrate impact, stop testing, and submit a report immediately.**
- You remain responsible for complying with applicable privacy/data laws when accessing/processing such data.

Practical rules:
- Do not download large datasets.
- Do not pivot into other accounts unless explicitly permitted.
- Use redaction in evidence (blur tokens, emails, identifiers).

### 4.5 Out-of-scope but "high impact"
Bugcrowd's Platform Behavior Standards acknowledge that researchers may believe they found a high-impact issue that appears out of scope and recommends submitting it for Bugcrowd Triage to evaluate.  
If you decide to proceed:
- Minimize testing to safe validation only.
- Call out **why** you believe the risk is high and why it likely belongs in scope.
- Accept that it may be marked Not Applicable / Out of Scope (and typically not rewardable).

Note: Standard Disclosure Terms also say that if you want to retain disclosure rights for out-of-scope issues, you should report directly to the program owner; treat this as a scenario-specific legal/strategy decision. When in doubt, involve Bugcrowd Support.

---

## 5) Communications policy (channels, cadence, professionalism)

### 5.1 Use only authorized channels
Standard Disclosure Terms require:
- Submissions via **Crowdcontrol** to be considered for reward.
- Communication about submissions to remain within **Crowdcontrol and/or official Bugcrowd support channels** during disclosure.

Platform Behavior Standards list "Out of Band Contact" as a policy issue: do not contact customers or Bugcrowd employees outside the platform bounds.

### 5.2 Do not spam, threaten, or game the process
Platform Behavior Standards and Code of Conduct explicitly flag:
- Spamming for updates / high support-ticket volume.
- Duplicate abuse (gaming duplicates/self-duplicates).
- Disclosure threats and unauthorized disclosure.
- Extortion threats.
- Harassment or abusive behavior.

Operational guidance:
- If an issue is stuck, use the platform's process tools (see "Request a Response") instead of repeated pings.
- Keep updates concise and evidence-driven.
- Never imply "pay or I disclose." That is treated as extortion/threat behavior.

### 5.3 Responsible use of GenAI
Bugcrowd's Code of Conduct allows GenAI use only in a way that avoids disclosure of confidential information and requires:
- Compliance with all platform/program policies.
- Protecting confidential information and findings.
- Manual review/validation of any AI-assisted report prior to submission; AI-generated reports without human review may be rejected.

---

## 6) Reporting SOP (how to submit, what "good" looks like)

### 6.1 Submission basics
- File all reports through Crowdcontrol for reward consideration (Standard Disclosure Terms).
- The Program Brief can override platform defaults; read it before you start drafting.
- Bugcrowd's "Reporting a Bug" documentation states you **cannot edit a submission after it is reported**-treat the initial submission as final and complete.

### 6.2 Minimum required contents (Bugcrowd docs)
Bugcrowd's Reporting a Bug page describes minimum information such as:
- Descriptive **Summary Title**
- **Target**
- Correct **Technical Severity** classification (VRT category)
- Clear **Description** including reproduction steps
- **Evidence** (screenshots/video) and/or PoC details
- **Demonstrated impact**
- Attachments/logs as needed


Bugcrowd's Standard Disclosure Terms also emphasize that submissions should have meaningful security impact and that researchers may be asked to defend the impact to qualify for a reward.

### 6.3 Evidence handling and accidental disclosure prevention
Bugcrowd strongly recommends including screenshots/videos as PoC evidence but warns:
- Do not upload PoC videos/screenshots to publicly accessible sites (e.g., YouTube/Imgur).
- If files exceed 100MB, use a secure service (e.g., password-protected Vimeo) per Bugcrowd guidance.
- Prefer uploading directly into the submission when possible; Bugcrowd's reporting docs allow multiple attachments and specify size/quantity limits.

### 6.4 Avoid "placeholder" submissions (anti-squatting)
Bugcrowd's Code of Conduct explicitly prohibits placeholder submissions used to "squat" on findings. Reports lacking description/PoC/replication steps may be closed and must be resubmitted with full details.

### 6.5 Responsiveness expectations
Standard Disclosure Terms state that submissions may be closed if the researcher is non-responsive to requests for information after **7 days**.

Operational rule:
- Monitor notifications and respond promptly to blockers/questions with reproducible clarifications.

### 6.6 Scope compliance consequences
Bugcrowd's reporting documentation notes that submitting against targets that are out of scope can result in a negative points adjustment, and that repeatedly testing outside approved scope can lead to loss of program access or platform privileges.

---

## 7) Submission lifecycle management (triage -> resolution -> follow-up)

### 7.1 Updates and escalation: "Request a Response (RaR)"
Bugcrowd provides a "Request a Response" feature to formally request updates or re-evaluation when a submission needs attention. Bugcrowd's docs state:
- RaR can be opened for submissions in several substates (e.g., Triage, Unresolved, Resolved, Not Reproducible, etc.).
- There are limits: only a limited number open simultaneously, and a maximum of **two (2) RaRs per submission**.
- Requests track a **10-business-day countdown** to expiration; quota is restored on expiration.

Use RaR instead of repeated "any updates?" comments.

### 7.2 Subscribe to brief changes
Bugcrowd supports engagement subscriptions; subscribing provides email notifications when the engagement brief changes. You are automatically subscribed once you submit your first report to an engagement and (for private engagements) upon accepting the invitation.

---

## 8) Disclosure and public communication

### 8.1 Default: nondisclosure unless explicitly allowed
Bugcrowd's Public Disclosure Policy states:
- Disclosure policies apply to **all submissions** (including duplicates, out-of-scope, not applicable, etc.).
- **Nondisclosure** is the default for certain engagement types (e.g., On-Demand bug bounty and Pen Test MAX), and in cases of ambiguity the expectation is nondisclosure.
- Private program existence/details must not be communicated to anyone not authorized (Bugcrowd employee or authorized organization employee).

Code of Conduct likewise states no submitted vulnerability may be disclosed without explicit customer permission, and the Program Brief supersedes.

### 8.2 Coordinated disclosure (when allowed)
Bugcrowd's policy describes coordinated disclosure as:
- Requiring explicit program-owner permission to disclose in the submission record.
- Agreement on disclosure timing and disclosure level.

Bugcrowd's "Disclosing Submissions" docs explain the mechanics:
- You can request disclosure only if the program owner has enabled disclosure.
- Disclosed submissions become visible in CrowdStream with a public summary and timeline.
- Disclosure can be "Full visibility" or "Limited visibility."
- Your avatar/username may be revealed when publicly disclosing.

Operational rules:
- Do not publish anything until "approved" and you have complied with the agreed disclosure constraints.
- Keep disclosure summary factual and avoid including sensitive reproduction details beyond what was approved.

---

## 9) Rewards, payment, and tax

### 9.1 Reward qualification (platform baseline)
Standard Disclosure Terms state rewards are first-to-find and qualify when:
- You are the first to alert the program owner to a previously unknown issue, and
- The issue triggers a code/configuration change.

Program Briefs can include focus areas, reward bands, and additional requirements.

### 9.2 Payment requirements and forfeiture
Standard Disclosure Terms note that, to get paid, you may need to provide additional verification and tax information, meet eligibility requirements, and accept additional terms with a third-party payment processor. Unclaimed/undeliverable monetary rewards for six (6) months may be forfeited, and taxes are your responsibility.

---

## 10) Intellectual property and ownership of testing results

Standard Disclosure Terms contain an IP assignment model:
- You agree to disclose all "Testing Results" to Bugcrowd.
- You assign your Testing Results (and rights) to Bugcrowd, with a broad license grant where assignment is not possible.
- You represent you have necessary approvals/consents from third parties (including your employer) to participate as a researcher.

Operational implications:
- Do not reuse private-program artifacts (screenshots, code, logs) for other contexts.
- Keep internal notes, but treat the core "Testing Results" as belonging to the Bugcrowd/program process.

---

## 11) Confidentiality and data classification

Standard Disclosure Terms define "Confidential Information" broadly, including (non-exhaustive):
- Customer info, target systems, private program existence and terms, fees/reward amounts, etc.

Treat as confidential unless:
- The Program Brief explicitly allows disclosure, and
- You have explicit permission recorded for that submission (and, when applicable, via the disclosure workflow).

---

## 12) Enforcement risk management

Bugcrowd's Platform Behavior Standards are point-based and include enforcement actions such as:
- Coaching message -> warning -> final warning -> temporary suspension -> platform ban.
They also note Bugcrowd can adjust severity based on the gravity of the infraction and can impose additional penalties (program removal, permanent removal).

Practical risk controls:
- Never disclose private program existence.
- Never threaten disclosure.
- Keep all contact in authorized channels.
- Avoid repetitive out-of-scope testing.
- Keep professionalism high; avoid any harassment/abusive language.

---

## 13) Support and service expectations

- Bugcrowd's docs direct researchers to submit support requests through the Bugcrowd Support ticketing portal.
- Bugcrowd counts business days in Pacific Time (Mon-Fri), with non-business days documented in their "Days of Operation" page. Use this when interpreting "business day" timelines (e.g., RaR countdown).

---

## 14) Practical checklists

### 14.1 Pre-engagement checklist (before testing)
- Confirm eligibility (age/identity where needed; sanctions/denied-party constraints).
- Enable 2FA (recommended; required for some engagements).
- Accept and sign NDA/compliance docs if required (private engagements).
- Read the Program Brief end-to-end:
  - Targets / out-of-scope
  - Allowed testing techniques and any rate limits
  - Disclosure policy and safe harbor indicators
  - Reward rules and focus areas
- Set up dedicated testing accounts if required/allowed.
- Prepare secure evidence handling (local encrypted folder; redaction tooling).

### 14.2 During testing checklist (safety guardrails)
- Stay strictly in-scope.
- Keep automation throttled; stop if performance impact is observed.
- Avoid interacting with other users' accounts unless explicitly permitted.
- If you see PII/PHI/payment data: minimize access, stop, document safely, report immediately.

### 14.3 Before clicking "Report Vulnerability"
- Title is descriptive (bug type + location + impact).
- Target is correct and in-scope.
- VRT category chosen correctly.
- Reproduction steps are complete and deterministic.
- Impact is clearly explained with realistic threat model.
- Evidence attached (screenshots/video) and redacted as needed.
- No public links to sensitive PoC content.
- You are comfortable that you cannot edit after submission.

### 14.4 Post-submission checklist
- Respond to blockers/questions quickly (<= 7 days).
- Keep all comms inside Crowdcontrol/support.
- Use "Request a Response" instead of repeated pings when appropriate.
- Do not disclose publicly unless explicitly approved and aligned with the disclosure policy.

---

## 15) Appendices

### 15.1 Submission template (copy/paste)
Use this structure in your "Description" field where possible.

- Overview:
  - What is the vulnerability?
  - Where is it located (endpoint/component)?
- Preconditions:
  - Account role/permissions needed
  - Any special configuration
- Steps to Reproduce:
  1.
  2.
  3.
- Expected vs Actual:
- Evidence:
  - Screenshots / video notes (redacted)
  - Logs / request/response snippets (redacted)
- Impact:
  - Who is affected?
  - What can an attacker achieve?
  - Practical exploitation constraints
- Suggested Fix (optional):
- Additional Notes:
  - Environment/build numbers
  - Any scope clarifications

---


### 15.2 Common low-value report categories (platform baseline)

Bugcrowd's Standard Disclosure Terms include:
- "Excluded Submission Types" (not accepted / not rewardable), such as physical testing, social engineering-derived findings, out-of-scope systems, UI/UX bugs, and network-level DoS/DDoS.
- A list of "Common Non-qualifying" submission types that are frequently low-impact unless you can demonstrate meaningful, chained impact.

Examples often considered low-value unless chained or clearly impactful include: generic stack traces/error pages, HTTP 404/non-200 pages, clickjacking-only issues, and missing/misconfigured security headers. Always defer to the Program Brief if it explicitly accepts a category.

## 16) Primary references (read these periodically)

Bugcrowd may update these documents. Treat the current versions as authoritative.

- Standard Disclosure Terms (Researcher Terms & Conditions component): https://www.bugcrowd.com/resources/hacker-resources/standard-disclosure-terms/
- Website Terms & Conditions (Terms of Service): https://www.bugcrowd.com/website-terms-and-conditions/
- Code of Conduct: https://www.bugcrowd.com/resources/hacker-resources/code-of-conduct/
- Platform Behavior Standards: https://www.bugcrowd.com/resources/hacker-resources/platform-behavior-standards/
- Reporting a Bug (Docs): https://docs.bugcrowd.com/researchers/reporting-managing-submissions/reporting-a-bug/
- Public Disclosure Policy (Docs): https://docs.bugcrowd.com/researchers/disclosure/disclosure/
- Disclosing Submissions (Docs): https://docs.bugcrowd.com/researchers/disclosure/disclosing-submissions/
- Disclose.io and Safe Harbor (Docs): https://docs.bugcrowd.com/researchers/disclosure/disclose-io-and-safe-harbor/
- NDA for Private Engagements (Docs): https://docs.bugcrowd.com/researchers/engagement-management/signing-nda-for-program/
- Two-Factor Authentication Compliance (Docs): https://docs.bugcrowd.com/researchers/engagement-management/two-factor-authentication-compliance/
- Verifying Your Identity (Docs): https://docs.bugcrowd.com/researchers/managing-account/account-settings/verifying-your-identity/
- Request a Response (Docs): https://docs.bugcrowd.com/researchers/reporting-managing-submissions/researchers-unread-comments/
- Support (Docs): https://docs.bugcrowd.com/researchers/onboarding/support/
- Bugcrowd Days of Operation (Docs): https://docs.bugcrowd.com/researchers/onboarding/days-of-operation/
- Logging in to Crowdcontrol (Docs): https://docs.bugcrowd.com/researchers/onboarding/logging-into-crowdcontrol/
- Welcome (Docs): https://docs.bugcrowd.com/researchers/onboarding/welcome/
