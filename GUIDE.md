# When to Report a Bug (Bug Bounty Pre-Report Guide)

This guide is a pre-report workflow for bug bounty / vulnerability disclosure programs. The goal is to avoid rushing, avoid false positives, avoid out-of-scope submissions, and maximize impact (and payout) by verifying and escalating responsibly before you submit.

## Why you shouldn't report immediately

Finding something feels exciting, but submitting too early commonly leads to:
- Money left on the table: you report a low-impact issue that could have been escalated (e.g., to account takeover).
- "Not Applicable" (NA) outcomes: the behavior is expected, requires unrealistic prerequisites, or is a self-inflicted scenario.
- Out-of-scope work: you touched assets the program explicitly told you not to touch, which can lead to penalties.

Use this guide to confirm you've found a real vulnerability, confirm it's in scope, and confirm the impact is clearly demonstrated.

---

## TL;DR checklist (before you hit "Submit")

Ask yourself:

1) Is this actually a security bug worth reporting?
- Is it impactful?
- Will a security team likely care?
- Are you about to spend hours arguing about a low-severity finding?

2) Have I confirmed it's a real vulnerability (not a misunderstanding)?
- Especially for common pitfalls like IDOR, XSS, SSRF.

3) Is the affected asset definitely in scope and owned by the program?
- If it's out of scope, don't expect a bounty even if it gets fixed.

4) Do I understand the vulnerability requirements?
- Exact account types, roles, org structure, permissions, victim prerequisites.

5) Do I understand the impact and can I explain it cleanly?
- What does the attacker gain?
- What can be changed/damaged?
- What does the victim have to do (if anything)?

6) Can I escalate responsibly?
- Can this become account takeover, privilege escalation, org takeover, financial impact, etc.?

7) Is it worth the time?
- If you're likely to argue whether it's a P4/P5/NA, it's often not worth it.

---

## Step-by-step: Pre-report validation workflow

### Step 1 - Pause and sanity-check "Is this a real vulnerability?"
Before collecting screenshots and writing a report, confirm you're not seeing:
- Expected behavior
- Misinterpreted auth/session handling
- A "self" scenario (user has to attack themselves)
- A third-party issue unrelated to the target program

This is where many NAs come from.

---

### Step 2 - Confirm scope and ownership (non-negotiable)
Check the program scope page and verify:
- The exact domain/subdomain/app you tested is listed in scope
- You're not on a lookalike host, old acquisition property, or vendor platform
- You're not interacting with something explicitly marked out of scope

Key guidance:
- If an asset is out of scope, do not expect a bounty even if the issue is fixed.
- Repeated out-of-scope testing can lead to penalties or removal from the program.

Practical habit:
- When you discover an issue on a host, immediately map it back to the scope list and confirm it's not a "nearby" subdomain you drifted into during recon.

---

### Step 3 - Validate the vulnerability using correct methodology
A lot of false reports are caused by testing the right category incorrectly.

#### Common pitfall: IDOR misunderstandings
A frequent mistake:
- Copy cookie from Account A, paste into Account B's context, request returns 200 -> not automatically an IDOR.

What an IDOR actually looks like:
- You use Account A's valid session and access/modify Account B's resource by changing a user-controlled identifier (e.g., user_id, order_id, org_id) on an endpoint that is meant to enforce authorization.

A simple IDOR validation pattern:
- Create two accounts: Attacker (A) and Victim (B)
- Identify a victim-owned object ID (legally/ethically, using your own test accounts)
- Using A's session, attempt to read/update/delete B's object by swapping the object ID in the request
- Confirm unauthorized access or modification occurs without using B's cookies

If the only "exploit" is "use the victim's cookie to access victim data," that's normal session behavior.

#### Common pitfall: Self-XSS / self-only effects
If the injected payload is only visible to the same user who injected it, many programs treat it as:
- Not exploitable
- A self-inflicted condition
- Not worth fixing (or very low severity)

A more credible XSS report generally includes:
- A path where another user (victim) renders the payload, or
- A realistic workflow where a victim is likely to view the affected content

#### Common pitfall: SSRF but the callback isn't from the target
If your "SSRF pingback" comes from infrastructure that isn't the target application, many programs will reject it.
Validate that:
- The target server is actually making the request, and
- You can demonstrate a meaningful security impact (internal access, metadata, restricted services, etc.)

---

### Step 4 - Understand and document the requirements (avoid "can't reproduce")
A large portion of NAs happen because triage cannot reproduce due to unclear setup.

Before reporting, write down precisely:
- What accounts are needed (free vs paid, admin vs standard)
- What roles/permissions must be set
- How the organization/tenant is configured
- What data must exist beforehand (objects, projects, shared resources)
- Whether the victim must do anything (click a link, visit a page, accept an invite, etc.)

Rule of thumb:
- If you cannot describe the setup in a few clean steps, triage probably won't reproduce it.

---

### Step 5 - Understand and prove impact (make it obvious)
Good reports explain impact in concrete terms.

Answer these:
- What does the attacker gain? (data access, state change, privilege increase)
- What can the attacker do to the victim? (delete, modify, transfer, lockout, impersonate)
- Does the victim need to do anything? (lower victim interaction usually increases severity)

A practical severity heuristic:
- No victim interaction + meaningful damage -> generally higher severity
- Victim must perform unlikely actions -> usually lower severity / debatable

---

### Step 6 - Attempt escalation (responsibly)
Many initial findings are "entry points" that can be upgraded.

Common escalation targets:
- Account takeover (ATO)
- Privilege escalation / org takeover
- Money movement / billing impact
- Permission bypass affecting sensitive resources

Examples of escalation thinking (high level):
- XSS -> can it perform authenticated actions as victim (CSRF-like actions, password reset flows, token theft in realistic contexts)?
- IDOR -> does it allow modifying roles/permissions, or accessing financial/admin resources?

Important:
- Do not cross program boundaries or violate rules trying to "force" escalation. Stay in scope and keep exploitation minimal and safe.

---

### Step 7 - Decide if it's worth reporting
Some findings create long back-and-forth for little return.

Signals it might not be worth it:
- You're debating whether it's P4 vs P5.
- The issue looks like accepted risk / expected behavior.
- You anticipate extensive argument to convince triage it matters.

Professional approach:
- Many experienced hunters do not report everything; they optimize for high-confidence, high-impact submissions.
- Newer hunters can still benefit from reporting P3/P4 issues, but understand that some low-severity categories are commonly ignored or heavily contested.

---

## "Report" decision matrix (quick guidance)

Report now if:
- In scope + clearly owned by target
- Reproducible in a clean minimal PoC
- Clear unauthorized impact
- Low/no victim interaction (or realistic interaction)
- You can explain requirements and impact in a few steps
- You've checked for straightforward escalation

Hold and investigate more if:
- You suspect escalation is possible (e.g., could become ATO/org takeover)
- The setup is complex and you haven't documented it yet
- Reproduction is flaky or depends on timing/race conditions without solid evidence

Don't report (or expect NA) if:
- Out of scope assets
- "Exploit" depends on using the victim's cookies to access victim data
- Pure self-XSS/self-harm scenarios with no realistic victim
- The SSRF callback isn't demonstrably from the target system
- The "issue" is a known feature / intended behavior

---

## Pre-report evidence package (what to collect before submitting)

Minimum:
- Clear reproduction steps from a fresh state
- Request/response evidence (Burp or equivalent)
- Exact endpoint(s), parameters, IDs involved
- Screenshots or short video if it helps reproducibility
- Explanation of required roles/accounts/org configuration

Impact proof:
- Show unauthorized access/change
- Show what data is exposed or what action was performed
- If escalation exists, demonstrate it safely and minimally

---

## One-page pre-submit template (copy/paste)

- Scope confirmed: Yes/No (asset: `...`)
- Vulnerability type: `...`
- Requirements:
  - Attacker account: `...`
  - Victim account: `...`
  - Roles/permissions/org setup: `...`
- Steps to reproduce:
  1. ...
  2. ...
  3. ...
- Expected behavior:
- Actual behavior:
- Impact:
  - What attacker can do:
  - What victim loses:
  - Victim interaction required: None/Low/High
- Escalation attempted:
  - Not attempted / Attempted and successful / Attempted and not possible (explain)
- Supporting evidence:
  - Requests/responses:
  - Screenshots/video:

---

## Summary principles

- Don't rush. Verify first.
- Confirm it's in scope and owned by the program.
- Make sure it's a real vulnerability (not cookie/session misunderstanding, self-only behavior, or third-party behavior).
- Understand the required setup and document it so triage can reproduce.
- Prove impact clearly; escalate when appropriate.
- Value your time: avoid long arguments over borderline low-severity issues when you could be finding better bugs.
