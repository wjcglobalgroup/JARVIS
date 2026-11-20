---
name: social-media-intelligence
description: Retrieve, interpret, compare, and report read-only social media analytics from YouTube, Instagram, and Facebook Page using Composio.
---

# Social Media Intelligence Skill

## Authorized Platforms

Marco is authorized to access ONLY these three social media platforms:

1. YouTube
2. Instagram
3. Facebook Page

This is the complete authorized platform scope for social media research responsibilities. Do not add, mention, research, connect, or request access to any other social media platform.

Binance Square: Not required per Willy.

## Access Level: READ-ONLY

You may:

- Retrieve account analytics
- Read post and video performance
- Analyze engagement
- Read impressions and reach
- Analyze audience growth
- Read watch time and retention where available
- Analyze shares, saves, and interactions where available
- Compare historical content performance
- Identify high-performing topics and formats

You are NOT authorized to:

- Publish posts
- Schedule posts
- Edit content
- Delete content
- Comment
- Reply to comments
- Send messages
- Change account settings
- Execute any write operation

Only execute read-only analytics actions. If Composio exposes write-capable tools, do not execute them. Do not request additional write permissions.

## Prerequisites

Before using this skill, verify:

1. Composio CLI is installed and version 0.4.0 or newer: `wsl ~/.composio/composio --version`
2. Composio is authenticated: `wsl ~/.composio/composio whoami`
3. The target platform integration is connected and authentication is valid

## Platform-Specific Metrics

### YouTube

- Views
- Watch time
- Average view duration
- Audience retention
- Impressions and click-through rate
- Subscribers gained
- Top-performing videos
- Traffic sources where available

### Instagram

- Reach
- Impressions
- Engagement
- Views and video performance
- Shares and saves
- Audience growth
- Content performance by format where available

### Facebook Page

- Page reach
- Impressions
- Engagement
- Video views
- Audience growth
- Post performance
- Available audience insights



## Research Methodology

### Performance Analysis

1. Retrieve analytics data for each authorized platform via Composio
2. Identify top-performing content by engagement metrics
3. Identify underperforming content for review
4. Compare content performance over time periods
5. Identify engagement patterns (time of day, day of week, content type)
6. Identify successful topics and content formats
7. Analyze audience growth trends
8. Identify opportunities to improve performance

### Intelligence Reporting

Do not simply send raw analytics. Convert findings into recommendations with:

- Reporting period
- Platform
- Supporting metrics
- Research observations (measured results)
- Recommendation (hypothesis clearly distinguished from measured results)
- Confidence level
- Data limitations

## Composio Integration Workflow

1. Check CLI version: `wsl ~/.composio/composio --version` (requires 0.4.0 or newer; validated 0.6.0)
2. Check authentication: `wsl ~/.composio/composio whoami`
3. List connections: `wsl ~/.composio/composio connections list`
4. Search for tools: `wsl ~/.composio/composio search <platform>`
5. Execute read-only action via WSL with JSON file parameter:
   ```bash
   wsl ~/.composio/composio execute <ACTION_SLUG> --account "<CONNECTION_ALIAS>" -d @/mnt/c/Users/dizon/params.json
   ```

Only execute read-only analytics actions. If Composio exposes write-capable tools, do not execute them.

## Verified Connections

| Platform | Connection ID | Alias | Status | Tested Action |
|----------|--------------|-------|--------|---------------|
| YouTube | ca_NH0Mc1VIIHJD | SMART TRADER ZONE | ACTIVE | YOUTUBE_GET_CHANNEL_STATISTICS (quota limited) |
| Instagram | ca_T4Abpi_jDPZp | stz | ACTIVE | INSTAGRAM_GET_USER_INSIGHTS (reach=0) |
| Facebook Page | ca_mtbqOpF2Zvoi | STZ PAGE | ACTIVE | FACEBOOK_GET_PAGE_INSIGHTS (needs numeric page_id) |

Binance Square: Not required per Willy.

Note: Google Calendar is covered by the separate `calendar-operations-awareness` skill.

## Data Limitations

Never invent unavailable metrics. Clearly document limitations for each platform, including:
- Whether historical performance data is available
- Whether any permission limitations exist
- Whether the integration is connected
- Whether authentication is valid

## Verification

After retrieving analytics:
1. Verify the data is from the correct platform
2. Verify the reporting period is correct
3. Verify metrics are complete or document gaps
4. Distinguish measured results from hypotheses