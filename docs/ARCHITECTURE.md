# Architecture

## Overview
Bug_Bounty_Hunter_AI is a docs-first planning repo for an AI-assisted bug bounty
workflow. The "hub" coordinates component repos, shared schemas, and safe
operational guidance.

## Core concepts
- Hub orchestrator: defines shared schemas, ROE, and integration rules.
- Components: single-capability repos that produce or consume structured data.
- Schemas: JSON schemas for TargetProfile, TestCase, Finding, and Evidence.
- Guardrails: rules of engagement and safety constraints baked into workflows.

## Data flow (conceptual)
1. Input: TargetProfile (authorized scope and AI surface map).
2. Review modules: generate TestCase and draft Finding candidates.
3. Evidence capture: collect minimal proof and references.
4. Reporting: assemble report bundles and issue drafts.

## Boundaries and responsibilities
- The hub should not contain exploit code or target-specific tooling.
- Components must stay non-weaponized and respect ROE.
- Shared schemas are the contract between components.

## Extensibility
Components should expose a small manifest describing:
- Capabilities (discovery, review, reporting).
- Supported schemas and versions.
- Inputs and outputs.

This enables future automation without hardcoding component logic into the hub.
