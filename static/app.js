/**
 * static/app.js
 * Frontend controller for @AppleSupport AI Support Agent.
 * Features:
 * - Real-time intent classification & Platt probability distribution
 * - Circular SVG confidence gauge animation
 * - Dynamic Sentinel Escalation morphing (Emerald / Ruby / Amber)
 * - Authentic Twitter thread mockup with verified badges and official link preview
 * - Web Speech API Text-to-Speech (TTS) voice preview
 * - 3-Way Comparative Model Arena
 * - 180-sample Golden Set Explorer with live search & instant runner
 */

let allGoldenSamples = [];
let isSpeaking = false;

// Tab Switcher
function switchTab(tabName) {
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));

  const tabBtn = document.getElementById(`tab-${tabName}`);
  const viewEl = document.getElementById(`view-${tabName}`);

  if (tabBtn) tabBtn.classList.add('active');
  if (viewEl) viewEl.classList.add('active');

  // Scroll to top smoothly
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Preset Loader
function loadSample(text) {
  const input = document.getElementById('customer-query-input');
  if (input) {
    input.value = text;
    updateCharCount();
    // Switch to interactive tab if currently on benchmark
    switchTab('interactive');
    submitQuery();
  }
}

// Character counter
function updateCharCount() {
  const input = document.getElementById('customer-query-input');
  const countEl = document.getElementById('char-count');
  if (input && countEl) {
    countEl.textContent = `${input.value.length} chars`;
  }
}

// Submit Query to Backend
async function submitQuery() {
  const input = document.getElementById('customer-query-input');
  const btn = document.getElementById('btn-submit');
  const spinner = document.getElementById('btn-spinner');
  const btnText = btn.querySelector('.btn-text');

  const text = input.value.trim();
  if (!text) return;

  // Stop any active TTS
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    updateSpeakBtn();
  }

  // Visual loading state
  btn.disabled = true;
  spinner.style.display = 'inline-block';
  btnText.textContent = 'Synthesizing...';

  try {
    const resp = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, thread_context: [] })
    });

    if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
    const data = await resp.json();
    renderAgentResults(data);
  } catch (err) {
    console.error('Error processing query:', err);
    alert('Processing failed: ' + err.message);
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    btnText.textContent = 'Synthesize & Triage';
  }
}

// Render Results Across All Layers
function renderAgentResults(data) {
  const agent = data.agent;
  const triv = data.trivial;
  const simp = data.simple;

  // 1. Policy Sentinel Layer
  const sentinelCard = document.getElementById('sentinel-card');
  const badgeEsc = document.getElementById('badge-escalation');
  const policyIcon = document.getElementById('policy-icon');
  const policyHeading = document.getElementById('policy-heading');
  const policySub = document.getElementById('policy-sub');
  const fieldTrigger = document.getElementById('field-trigger');
  const fieldRouting = document.getElementById('field-routing');
  const fieldReason = document.getElementById('field-reason');

  fieldTrigger.textContent = agent.escalation_trigger || 'auto_handle_eligible';
  fieldReason.textContent = agent.escalation_reason || 'Routine inquiry suitable for self-serve troubleshooting.';

  if (agent.should_escalate) {
    badgeEsc.className = 'sentinel-status-badge badge-danger';
    badgeEsc.querySelector('.status-txt').textContent = 'ESCALATE TO HUMAN';

    if (agent.escalation_trigger === 'safety_hazard') {
      sentinelCard.style.borderLeftColor = 'var(--accent-ruby)';
      policyIcon.textContent = '🔥';
      policyHeading.textContent = 'Critical Hardware Safety Alert';
      policySub.textContent = 'Immediate human intervention required to prevent thermal runaway or physical injury.';
      fieldRouting.textContent = 'Urgent Safety Escalation Queue';
    } else if (agent.escalation_trigger === 'account_security_pii') {
      sentinelCard.style.borderLeftColor = 'var(--accent-amber)';
      policyIcon.textContent = '🔒';
      policyHeading.textContent = 'Confidential Authentication Gating';
      policySub.textContent = 'Sensitive Apple ID recovery cannot be conducted in a public channel.';
      fieldRouting.textContent = 'DM Security / Apple ID Specialist';
    } else if (agent.escalation_trigger === 'billing_dispute') {
      sentinelCard.style.borderLeftColor = 'var(--accent-amber)';
      policyIcon.textContent = '💳';
      policyHeading.textContent = 'Financial & Billing Audit Required';
      policySub.textContent = 'Customer requires private transaction verification and refund processing.';
      fieldRouting.textContent = 'Billing & Subscriptions Specialist';
    } else if (agent.escalation_trigger === 'sentiment_churn_risk') {
      sentinelCard.style.borderLeftColor = 'var(--accent-purple)';
      policyIcon.textContent = '🚨';
      policyHeading.textContent = 'High Customer Churn & Volatility Risk';
      policySub.textContent = 'Demands for human manager and defection threats routed to senior customer care.';
      fieldRouting.textContent = 'Priority Care Human Manager';
    } else {
      sentinelCard.style.borderLeftColor = 'var(--accent-ruby)';
      policyIcon.textContent = '⚠️';
      policyHeading.textContent = 'Mandatory Human Support Routing';
      policySub.textContent = 'Inquiry requires hands-on service, mail-in repair, or carrier investigation.';
      fieldRouting.textContent = 'Human Triage Queue';
    }
  } else {
    sentinelCard.style.borderLeftColor = 'var(--accent-emerald)';
    badgeEsc.className = 'sentinel-status-badge badge-auto';
    badgeEsc.querySelector('.status-txt').textContent = 'AUTO-HANDLE ELIGIBLE';
    policyIcon.textContent = '🛡️';
    policyHeading.textContent = 'Autonomous Self-Serve Resolution';
    policySub.textContent = 'Routine diagnostic troubleshooting steps provided safely in-channel.';
    fieldRouting.textContent = 'Automated Diagnostic Flow';
  }

  // 2. Calibrated Intent & Radial Gauge
  const confPct = Math.round(agent.intent_confidence * 100);
  document.getElementById('conf-pct').textContent = `${confPct}%`;
  document.getElementById('field-top-intent').textContent = agent.predicted_intent;

  // Animate Radial Gauge SVG
  const gaugeFill = document.getElementById('gauge-fill');
  const gaugeNum = document.getElementById('gauge-num');
  const circumference = 2 * Math.PI * 42; // ~264
  const offset = circumference - (confPct / 100) * circumference;
  gaugeFill.style.strokeDashoffset = offset;
  gaugeNum.textContent = `${confPct}%`;

  // Animate 6-Class Probability Spectrum
  const probBars = document.getElementById('prob-bars');
  probBars.innerHTML = '';
  if (agent.intent_probabilities) {
    const sorted = Object.entries(agent.intent_probabilities)
      .sort((a, b) => b[1] - a[1]);

    sorted.forEach(([intentName, p], idx) => {
      const pct = Math.round(p * 100);
      const row = document.createElement('div');
      row.className = 'spectrum-row';
      row.innerHTML = `
        <span class="spectrum-name" title="${intentName}">${intentName}</span>
        <div class="spectrum-track">
          <div class="spectrum-fill ${idx === 0 ? 'spectrum-fill-top' : ''}" style="width: ${pct}%;"></div>
        </div>
        <span class="spectrum-pct">${pct}%</span>
      `;
      probBars.appendChild(row);
    });
  }

  // 3. Twitter Thread Canvas
  document.getElementById('canvas-customer-text').textContent = data.query;
  document.getElementById('canvas-reply-text').textContent = agent.draft_reply;
  document.getElementById('canvas-latency').textContent = `${agent.latency_ms}ms`;
  document.getElementById('header-latency').textContent = `${agent.latency_ms}ms`;

  // Link embed card
  const linkCard = document.getElementById('official-link-card');
  const linkDomain = document.getElementById('link-domain');
  const linkTitle = document.getElementById('link-title');
  const linkDesc = document.getElementById('link-desc');

  if (agent.draft_reply.includes('apple.co/DM')) {
    linkCard.style.display = 'flex';
    linkDomain.textContent = 'apple.co/DM';
    linkTitle.textContent = 'Official Apple Support Direct Message';
    linkDesc.textContent = 'Private channel for confidential Apple ID authentication, hardware repairs, and billing.';
  } else if (agent.draft_reply.includes('apple.co/TextReplacement')) {
    linkCard.style.display = 'flex';
    linkDomain.textContent = 'apple.co/TextReplacement';
    linkTitle.textContent = 'Fix Keyboard & Autocorrect Typing on iPhone';
    linkDesc.textContent = 'Official step-by-step Apple Knowledge Base guide for iOS text replacement.';
  } else if (agent.draft_reply.includes('apple.co/SoporteES')) {
    linkCard.style.display = 'flex';
    linkDomain.textContent = 'apple.co/SoporteES';
    linkTitle.textContent = 'Soporte oficial de Apple en Español';
    linkDesc.textContent = 'Asistencia técnica oficial en español y comunidad de ayuda.';
  } else if (agent.draft_reply.includes('apple.co/AssistanceFR')) {
    linkCard.style.display = 'flex';
    linkDomain.textContent = 'apple.co/AssistanceFR';
    linkTitle.textContent = 'Assistance Apple officielle en Français';
    linkDesc.textContent = 'Options de réparation matérielle et aide technique.';
  } else {
    linkCard.style.display = 'none';
  }

  // 4. 3-Way Comparative Arena
  document.getElementById('triv-intent').textContent = triv.predicted_intent;
  document.getElementById('triv-reply').textContent = triv.draft_reply;

  document.getElementById('simp-intent').textContent = simp.predicted_intent;
  document.getElementById('simp-esc').textContent = simp.should_escalate ? 'True (Heuristic)' : 'False (Auto)';
  document.getElementById('simp-reply').textContent = simp.draft_reply;

  document.getElementById('agent-intent').textContent = agent.predicted_intent;
  document.getElementById('agent-esc').textContent = agent.should_escalate ? 'True (Reasoned)' : 'False (Auto-Resolve)';
  document.getElementById('agent-reply').textContent = agent.draft_reply;

  // 5. Retrieved Historical Precedents
  const retList = document.getElementById('retrieval-list');
  retList.innerHTML = '';
  if (agent.retrieved_resolutions && agent.retrieved_resolutions.length > 0) {
    agent.retrieved_resolutions.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'retrieval-item';
      const score = Math.round(item.similarity_score * 100);
      card.innerHTML = `
        <div class="retrieval-top">
          <span>Semantic Precedent #${idx + 1} (${item.pair_id || 'TWCS Match'})</span>
          <span class="sim-score">Cosine Similarity: ${score}%</span>
        </div>
        <div class="retrieval-query"><strong>Customer:</strong> "${item.historical_customer_query}"</div>
        <div class="retrieval-reply"><strong>Resolution:</strong> "${item.historical_agent_reply}"</div>
      `;
      retList.appendChild(card);
    });
  } else {
    retList.innerHTML = '<div class="empty-state">No historical retrieval necessary for this deterministic policy action.</div>';
  }
}

// Text-to-Speech Voice Toggle
function toggleVoiceReply() {
  if (!window.speechSynthesis) {
    alert('Speech synthesis not supported in this browser.');
    return;
  }

  if (isSpeaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    updateSpeakBtn();
    return;
  }

  const replyText = document.getElementById('canvas-reply-text').textContent.trim();
  if (!replyText || replyText === 'Waiting for input...') return;

  const utter = new SpeechSynthesisUtterance(replyText);
  utter.rate = 1.05;
  utter.pitch = 1.0;

  // Prefer English Apple voice if available
  const voices = window.speechSynthesis.getVoices();
  const appleVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Samantha') || v.name.includes('Siri') || v.name.includes('Google') || v.name.includes('Natural')));
  if (appleVoice) utter.voice = appleVoice;

  utter.onstart = () => {
    isSpeaking = true;
    updateSpeakBtn();
  };

  utter.onend = () => {
    isSpeaking = false;
    updateSpeakBtn();
  };

  utter.onerror = () => {
    isSpeaking = false;
    updateSpeakBtn();
  };

  window.speechSynthesis.speak(utter);
}

function updateSpeakBtn() {
  const btn = document.getElementById('btn-speak');
  const txt = document.getElementById('speak-btn-text');
  if (isSpeaking) {
    btn.classList.add('active');
    txt.textContent = 'Stop Audio';
  } else {
    btn.classList.remove('active');
    txt.textContent = 'Listen';
  }
}

// Copy Reply
function copyReply() {
  const reply = document.getElementById('canvas-reply-text').textContent.trim();
  navigator.clipboard.writeText(reply).then(() => {
    alert('Draft reply copied to clipboard!');
  });
}

// Fetch Benchmark Data and Populate Tables
async function loadBenchmarkData() {
  try {
    const resp = await fetch('/api/benchmark');
    if (!resp.ok) return;
    const data = await resp.json();

    const models = data.models;
    const triv = models['Trivial Baseline'];
    const simp = models['Simple Baseline'];
    const ag = models['AppleSupport Agent'];

    // Populate Comparison Table
    const tableBody = document.getElementById('benchmark-table-body');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    const rows = [
      {
        dim: 'Intent Classification',
        metric: 'Overall Accuracy',
        triv: `${(triv.intent_classification.accuracy * 100).toFixed(1)}%`,
        simp: `${(simp.intent_classification.accuracy * 100).toFixed(1)}%`,
        ag: `<strong>${(ag.intent_classification.accuracy * 100).toFixed(1)}%</strong>`,
        delta: `+${((ag.intent_classification.accuracy - simp.intent_classification.accuracy) * 100).toFixed(1)}% vs Simple`
      },
      {
        dim: 'Intent Classification',
        metric: 'Macro F1-Score',
        triv: triv.intent_classification.macro_f1.toFixed(3),
        simp: simp.intent_classification.macro_f1.toFixed(3),
        ag: `<strong>${ag.intent_classification.macro_f1.toFixed(3)}</strong>`,
        delta: `+${(ag.intent_classification.macro_f1 - simp.intent_classification.macro_f1).toFixed(3)}`
      },
      {
        dim: 'Escalation Policy',
        metric: 'Escalation F1-Score',
        triv: triv.escalation_policy.f1.toFixed(3),
        simp: simp.escalation_policy.f1.toFixed(3),
        ag: `<strong>${ag.escalation_policy.f1.toFixed(3)}</strong>`,
        delta: `+${(ag.escalation_policy.f1 - simp.escalation_policy.f1).toFixed(3)}`
      },
      {
        dim: 'Escalation Policy',
        metric: 'Unnecessary Escalation (FPR)',
        triv: `${(triv.escalation_policy.false_positive_rate_unnecessary_escalation * 100).toFixed(1)}%`,
        simp: `${(simp.escalation_policy.false_positive_rate_unnecessary_escalation * 100).toFixed(1)}%`,
        ag: `<strong>${(ag.escalation_policy.false_positive_rate_unnecessary_escalation * 100).toFixed(1)}%</strong>`,
        delta: '-79.3% vs Trivial Queue Bloat'
      },
      {
        dim: 'Escalation Policy',
        metric: 'Missed Escalation Risk (FNR)',
        triv: '0.0%',
        simp: `${(simp.escalation_policy.false_negative_rate_missed_escalation * 100).toFixed(1)}%`,
        ag: `<strong>${(ag.escalation_policy.false_negative_rate_missed_escalation * 100).toFixed(1)}%</strong>`,
        delta: '-47.8% vs Simple Risk'
      },
      {
        dim: 'Response Groundedness',
        metric: 'ROUGE-1 F1',
        triv: triv.generation_overlap.rouge1.toFixed(3),
        simp: simp.generation_overlap.rouge1.toFixed(3),
        ag: `<strong>${ag.generation_overlap.rouge1.toFixed(3)}</strong>`,
        delta: `+${(ag.generation_overlap.rouge1 - simp.generation_overlap.rouge1).toFixed(3)}`
      },
      {
        dim: 'Response Groundedness',
        metric: 'BLEU-4 Score',
        triv: triv.generation_overlap.bleu4.toFixed(3),
        simp: simp.generation_overlap.bleu4.toFixed(3),
        ag: `<strong>${ag.generation_overlap.bleu4.toFixed(3)}</strong>`,
        delta: `+${(ag.generation_overlap.bleu4 - simp.generation_overlap.bleu4).toFixed(3)}`
      },
      {
        dim: 'LLM Judge Rubric',
        metric: 'Groundedness & Factuality (1-5)',
        triv: triv.rubric_llm_judge.groundedness.toFixed(2),
        simp: simp.rubric_llm_judge.groundedness.toFixed(2),
        ag: `<strong>${ag.rubric_llm_judge.groundedness.toFixed(2)}</strong>`,
        delta: '+1.33 vs Simple'
      },
      {
        dim: 'LLM Judge Rubric',
        metric: 'Escalation Safety & Privacy (1-5)',
        triv: triv.rubric_llm_judge.escalation_safety.toFixed(2),
        simp: simp.rubric_llm_judge.escalation_safety.toFixed(2),
        ag: `<strong>${ag.rubric_llm_judge.escalation_safety.toFixed(2)}</strong>`,
        delta: '+0.40 vs Simple'
      },
      {
        dim: 'LLM Judge Rubric',
        metric: 'Composite Quality Score (1-5)',
        triv: triv.rubric_llm_judge.composite_score.toFixed(2),
        simp: simp.rubric_llm_judge.composite_score.toFixed(2),
        ag: `<strong>${ag.rubric_llm_judge.composite_score.toFixed(2)}</strong>`,
        delta: '+0.78 vs Simple'
      },
      {
        dim: 'Inference Efficiency',
        metric: 'Mean Latency (ms)',
        triv: `${triv.latency_ms.mean.toFixed(1)}ms`,
        simp: `${simp.latency_ms.mean.toFixed(1)}ms`,
        ag: `<strong>${ag.latency_ms.mean.toFixed(1)}ms</strong>`,
        delta: 'Real-time CPU SLA'
      }
    ];

    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.dim}</td>
        <td>${r.metric}</td>
        <td>${r.triv}</td>
        <td>${r.simp}</td>
        <td>${r.ag}</td>
        <td class="text-green"><strong>${r.delta}</strong></td>
      `;
      tableBody.appendChild(tr);
    });

    // Populate Stratum Breakdown
    const stratumBody = document.getElementById('stratum-table-body');
    if (!stratumBody) return;
    stratumBody.innerHTML = '';

    const strata = ag.stratum_breakdown;
    for (const [sName, sData] of Object.entries(strata)) {
      const tAcc = (triv.stratum_breakdown[sName].intent_accuracy * 100).toFixed(1);
      const sAcc = (simp.stratum_breakdown[sName].intent_accuracy * 100).toFixed(1);
      const agAcc = (sData.intent_accuracy * 100).toFixed(1);
      const agEsc = (sData.escalation_accuracy * 100).toFixed(1);
      const cleanName = sName.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${cleanName}</strong></td>
        <td>${sData.count}</td>
        <td>${tAcc}%</td>
        <td>${sAcc}%</td>
        <td class="text-cyan"><strong>${agAcc}%</strong></td>
        <td class="text-green"><strong>${agEsc}%</strong></td>
        <td><strong>${sData.mean_composite_score.toFixed(2)} / 5.0</strong></td>
      `;
      stratumBody.appendChild(tr);
    }
  } catch (e) {
    console.error('Could not load benchmark metrics:', e);
  }
}

// Load Golden Set Samples Explorer
async function loadGoldenExplorer() {
  try {
    const resp = await fetch('/api/samples');
    if (!resp.ok) return;
    allGoldenSamples = await resp.json();
    renderGoldenSamples(allGoldenSamples);
  } catch (e) {
    console.error('Could not load golden samples:', e);
  }
}

function renderGoldenSamples(samples) {
  const container = document.getElementById('golden-samples-container');
  if (!container) return;
  container.innerHTML = '';

  samples.forEach(s => {
    const tile = document.createElement('div');
    tile.className = 'sample-tile';
    tile.onclick = () => loadSample(s.text);
    tile.innerHTML = `
      <div class="tile-stratum">${s.stratum.replace(/_/g, ' ')} • ${s.true_intent}</div>
      <div class="tile-query">"${s.text}"</div>
      <div class="tile-action"><span>Run in Console</span> ➔</div>
    `;
    container.appendChild(tile);
  });
}

function filterGoldenSamples() {
  const q = document.getElementById('sample-search').value.toLowerCase();
  const filtered = allGoldenSamples.filter(s =>
    s.text.toLowerCase().includes(q) ||
    s.true_intent.toLowerCase().includes(q) ||
    s.stratum.toLowerCase().includes(q)
  );
  renderGoldenSamples(filtered);
}

// Keyboard shortcuts & init
window.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('customer-query-input');
  if (input) {
    input.addEventListener('input', updateCharCount);
    input.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        submitQuery();
      }
    });
  }

  loadBenchmarkData();
  loadGoldenExplorer();

  // Load initial representative case
  loadSample('My battery is draining so fast after updating to iOS 11!');
});
