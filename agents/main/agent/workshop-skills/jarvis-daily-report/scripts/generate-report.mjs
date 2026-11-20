#!/usr/bin/env node
/**
 * Jarvis Daily Executive Operations Report Generator
 * 
 * CORRECTED VERSION: Uses OpenClaw tool_call interfaces directly,
 * NOT CLI commands. The previous version failed because it used
 * `npx openclaw sessions_send`, `npx openclaw automations --action`,
 * etc. which don't exist as CLI commands.
 * 
 * This script is designed to be run within an OpenClaw session where
 * tool_call is available. It cannot run standalone via `node`.
 * 
 * For cron execution, the payload should invoke the skill steps directly
 * using the available tools, not by running this script as a CLI.
 */

// This file serves as a REFERENCE for the correct tool_call patterns.
// The actual cronjob payload should inline these tool calls.

const TOOL_CALL_PATTERNS = {
  // Send message to another agent session
  sessions_send: {
    id: "openclaw:core:sessions_send",
    args: {
      sessionKey: "agent:marco:main",  // Target session key
      message: "Research prompt here"
    }
  },

  // List automations (cronjobs)
  automations_list: {
    id: "openclaw:core:automations",
    args: { action: "list", includeDisabled: true }
  },

  // Get single automation details
  automations_get: {
    id: "openclaw:core:automations",
    args: { action: "get", jobId: "9a279a9f-3ccc-417f-ac6c-56a3ac4650ed" }
  },

  // List sessions
  sessions_list: {
    id: "openclaw:core:sessions_list",
    args: { relationship: "owned", activeOnly: true }
  },

  // Fetch web content (for crypto market data)
  web_fetch: {
    id: "openclaw:core:web_fetch",
    args: {
      url: "https://api.coingecko.com/api/v3/global",
      extractMode: "text"
    }
  },

  // List conversations (for Discord DM channel)
  conversations_list: {
    id: "openclaw:core:conversations_list",
    args: {}
  },

  // Send message via conversation (Discord DM)
  conversations_send: {
    id: "openclaw:core:conversations_send",
    args: {
      conversationRef: "discord-dm-willy",
      message: "Report content here"
    }
  },

  // Send message via message tool (alternative)
  message_send: {
    id: "openclaw:core:message",
    args: {
      action: "send",
      channel: "discord",
      target: "willy",
      message: "Report content here"
    }
  }
};

// Crypto market data endpoints (no API key required)
const CRYPTO_ENDPOINTS = {
  global: "https://api.coingecko.com/api/v3/global",
  btcEth: "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum&order=market_cap_desc&per_page=2&page=1&sparkline=false&price_change_percentage=24h",
  top10: "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=24h"
};

// Timezone handling for Asia/Manila (PHT = UTC+8)
function getPHTDate() {
  const now = new Date();
  return new Date(now.getTime() + (8 * 60 * 60 * 1000) + (now.getTimezoneOffset() * 60 * 1000));
}

function getPeriodBounds() {
  const end = getPHTDate();
  const start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
  return {
    start: start.toISOString(),
    end: end.toISOString(),
    date: end.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'Asia/Manila' })
  };
}

// Report template - matches AGENTS.md structure
const REPORT_TEMPLATE = `# 🧠 JARVIS DAILY EXECUTIVE REPORT

**Date:** {{date}}  
**Report Period:** Previous 24 hours ({{period_start}} → {{period_end}})

---

## 1. 🚨 IMMEDIATE ATTENTION

{{immediate_attention}}

---

## 2. ₿ CRYPTO MARKET — LAST 24 HOURS

{{crypto_market}}

---

## 3. 📰 IMPORTANT CRYPTO / INDUSTRY DEVELOPMENTS

{{developments}}

---

## 4. 📧 EMAIL EXECUTIVE TRIAGE

{{email_triage}}

---

## 5. 💰 BILLING / PAYMENT ALERTS

{{billing_alerts}}

---

## 6. 🤝 SPONSORSHIP OPPORTUNITIES

{{sponsorships}}

---

## 7. 📅 CALENDAR / UPCOMING OPERATIONS

{{calendar}}

---

## 8. 🤖 AGENT / STZ OPERATIONS STATUS

{{agent_status}}

---

## 9. 📊 SOCIAL MEDIA ANALYTICS (READ-ONLY)

{{social_analytics}}

---

## 10. 🧠 EXECUTIVE PRIORITIZATION

{{prioritization}}

---

## 11. 🎯 TODAY'S PRIORITIES

### 1. Immediate
{{today_immediate}}

### 2. Important
{{today_important}}

### 3. Delegated
{{today_delegated}}

### 4. Monitor
{{today_monitor}}

### 5. No Action Required
{{today_no_action}}

---

## 12. 📋 EXECUTIVE SUMMARY

**Overall STZ Status:** {{overall_status}}  
**Crypto Market:** {{market_summary}}  
**Immediate Owner Attention:** {{immediate_count}} item(s)  
**Important Email Items:** {{email_count}}  
**Important Bills/Deadlines:** {{bill_count}}  
**Agent/System Issues:** {{agent_issue_count}}  
**Key Recommendation:** {{key_recommendation}}
`;

function buildReport(data) {
  return REPORT_TEMPLATE
    .replace('{{date}}', data.date || 'Unknown')
    .replace('{{period_start}}', data.period_start || 'Unknown')
    .replace('{{period_end}}', data.period_end || 'Unknown')
    .replace('{{immediate_attention}}', data.immediate_attention || '**No critical action required.**')
    .replace('{{crypto_market}}', data.crypto_market || '_Market data unavailable._')
    .replace('{{developments}}', data.developments || '_No major developments identified._')
    .replace('{{email_triage}}', data.email_triage || '_Email triage unavailable._')
    .replace('{{billing_alerts}}', data.billing_alerts || '**No critical billing alerts.**')
    .replace('{{sponsorships}}', data.sponsorships || '**No sponsorship opportunities identified.**')
    .replace('{{calendar}}', data.calendar || '**No critical upcoming commitments.**')
    .replace('{{agent_status}}', data.agent_status || '_Agent status check pending._')
    .replace('{{social_analytics}}', data.social_analytics || '_Social analytics unavailable (read-only integrations not connected)._')
    .replace('{{prioritization}}', data.prioritization || '_Prioritization pending._')
    .replace('{{today_immediate}}', data.today_immediate || 'None')
    .replace('{{today_important}}', data.today_important || 'None')
    .replace('{{today_delegated}}', data.today_delegated || 'None')
    .replace('{{today_monitor}}', data.today_monitor || 'None')
    .replace('{{today_no_action}}', data.today_no_action || 'None')
    .replace('{{overall_status}}', data.overall_status || '🟡')
    .replace('{{market_summary}}', data.market_summary || 'Mixed')
    .replace('{{immediate_count}}', data.immediate_count || 0)
    .replace('{{email_count}}', data.email_count || 0)
    .replace('{{bill_count}}', data.bill_count || 0)
    .replace('{{agent_issue_count}}', data.agent_issue_count || 0)
    .replace('{{key_recommendation}}', data.key_recommendation || 'Review report and prioritize immediate items.');
}

// Export for reference - this script is not meant to run standalone
module.exports = {
  TOOL_CALL_PATTERNS,
  CRYPTO_ENDPOINTS,
  getPeriodBounds,
  buildReport,
  REPORT_TEMPLATE
};

// If run directly, show usage
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('⚠️  This script is a REFERENCE for tool_call patterns.');
  console.log('It cannot run standalone via `node`.');
  console.log('');
  console.log('For cron execution, inline the tool_call patterns in the');
  console.log('cronjob payload or invoke via the OpenClaw session.');
  console.log('');
  console.log('Key correction from failed attempt:');
  console.log('  ❌ npx openclaw sessions_send --agentId marco --message "..."');
  console.log('  ✅ tool_call({id: "openclaw:core:sessions_send", args: {...}})');
  console.log('');
  console.log('Available tool_call interfaces:');
  Object.entries(TOOL_CALL_PATTERNS).forEach(([name, pattern]) => {
    console.log(`  ${name}: ${JSON.stringify(pattern, null, 2)}`);
  });
}