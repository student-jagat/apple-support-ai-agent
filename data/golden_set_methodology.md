# Golden Evaluation Set Methodology

## Overview
The Golden Evaluation Set consists of **180 meticulously curated and hand-labelled customer queries** grounded in real interactions from the Twitter Customer Support (TWCS) dataset for `@AppleSupport`.

To ensure our evaluation is rigorous, honest, and reflective of production realities, the benchmark avoids easy cherry-picking by utilizing **stratified sampling across 5 critical operational strata**.

---

## 1. Stratification Breakdown

| Stratum | Description | Count | Percentage | Key Evaluation Objective |
|---|---|---|---|---|
| **1. Standard Inbound Queries** | Clean, representative queries covering each of the 6 core intents (12 cases each). | 72 | 40.0% | Baseline competency across standard troubleshooting & policy domains. |
| **2. Ambiguous & Multi-Intent Queries** | Blended issues (e.g. battery drain during update causing boot loop, hardware button causing recovery mode). | 36 | 20.0% | Model robustness when intent signals conflict; primary intent disambiguation. |
| **3. Escalation Boundary Edge Cases** | Subtle boundary cases (hyperbole vs literal damage, figurative 'robbery' vs real unauthorized billing, safety hazards). | 28 | 15.6% | Safety-critical discrimination between self-serve KB advice and mandatory escalation. |
| **4. Frustrated & Churn-Risk Language** | High-emotion, agitated inquiries, competitor defection threats (Samsung/Pixel), demands for managers. | 26 | 14.4% | Escalation sensitivity to customer sentiment volatility and brand risk mitigation. |
| **5. Noise, Out-of-Scope & Multilingual** | Foreign languages (ES, FR, PT, DE), spam links, gibberish, and non-Apple competitor inquiries. | 18 | 10.0% | Graceful handling of out-of-distribution inputs without hallucinating answers. |
| **Total** | | **180** | **100.0%** | Comprehensive real-world support benchmark. |

---

## 2. Intent Taxonomy Definitions

1. `software_os_update`: Glitches, freezes, keyboard typing errors (iOS 11 autocorrect), app crashes, update installation loops, storage calculation bugs.
2. `battery_power_charging`: Battery drain regressions, unexpected shutdowns at high percentages, cable accessory warnings, wireless charging alignment.
3. `hardware_physical_defect`: Cracked screens, broken home buttons, camera optical stabilization vibration, water damage, swollen batteries (urgent safety).
4. `account_icloud_billing`: Apple ID lockouts, 2FA recovery, duplicate App Store charges, unauthorized child in-app purchases, subscription cancellations.
5. `connectivity_pairing`: Bluetooth disconnects, AirPods call audio drops, cellular "No Service" baseband faults, CarPlay USB disconnects, Wi-Fi drops.
6. `order_delivery_tradein`: Pre-order delivery delays (iPhone X launch), trade-in kit return status, lost carrier shipments, in-store pickup authorization.

---

## 3. Escalation Ground Truth Policy

A customer interaction **MUST BE ESCALATED (`true_escalate = True`)** if and only if:
1. **Safety Risk**: Battery swelling, smoke, excessive heat, sparking charger, cracked glass injury risk.
2. **Confidential Authentication (PII)**: Apple ID account recovery, password resets, two-factor authorization changes.
3. **Financial / Transactional Disputes**: Duplicate credit card charges, refund audits, unauthorized child purchases, trade-in valuation audits.
4. **Physical Inspection / Hardware Repair**: Component failures that cannot be resolved via settings or reboots (TrueDepth camera broken, shattered OLED, jammed buttons).
5. **Logistics & Order Tracking**: Missing shipments, shipping address alterations, order cancellations.
6. **Severe Customer Churn Risk**: Express demands for human agents, repeated failed interactions, legal/regulatory threats.

All other routine troubleshooting steps (force restart, settings reset, text replacement workarounds, feature how-tos) **MUST BE AUTO-HANDLED (`true_escalate = False`)** to avoid overwhelming human support queues.

---

## 4. Ground Truth Quality & Review
- Each example was individually reviewed and paired with a **Human Gold Reply** adhering to official Apple Support Twitter response guidelines:
  - Empathetic opening acknowledgement
  - Direct diagnostic question or actionable self-serve step
  - Clean, official Apple escalation link (`apple.co/DM` or `apple.co/...`)
- Human judge ratings were calibrated on all 180 samples as the target gold standard (composite score: 5.0).
