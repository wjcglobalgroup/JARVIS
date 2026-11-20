---
name: marco-macro-gate-reporting
description: Macro gate reporting and STZ crypto media research planning. Fix RSS parsing, replace failed APIs with working RSS feeds, fix PowerShell syntax, verify Discord delivery. Create media-research-planner.ps1 covering 6 research areas: cryptocurrency news, Bitcoin/market developments, blockchain/DeFi, AI tools for crypto, education/security, exchange/regulatory announcements.
---

# Marco Macro Gate Reporting System Maintenance

## Trigger
- Macro gate report not delivering to Discord
- RSS feeds returning empty URLs or timestamps
- API sources failing (rate limits, auth errors)
- PowerShell script syntax errors
- Need to verify end-to-end Discord delivery
- Expand research planning for STZ crypto media strategy
- Need media-research-plan-YYYY-MM-DD.md for Vera content production

## Procedure

### 1. Inspect Automation Job Status
```bash
openclaw automations show <job-id>
```
Check: enabled state, schedule, delivery target, last run status, error details.

### 2. Fix RSS Feed Parsing (PowerShell)
The core issue: different RSS feeds handle `link` and `pubDate` inconsistently:
- Some auto-convert XmlElement to string (`$item.link` works)
- Others use CDATA requiring `.InnerText` (`$item.link.InnerText` works)

**Fix**: Update `Extract-ItemUrl` and `Parse-PubDate` to try both patterns:
```powershell
function Extract-ItemUrl {
    param($item)
    $link = $null
    if ($item.link) {
        $link = $item.link.ToString().Trim()
        if ([string]::IsNullOrWhiteSpace($link)) { $link = $item.link.InnerText.Trim() }
    }
    if (-not [string]::IsNullOrWhiteSpace($link)) { return $link }
    if ($item.guid) {
        $guid = $item.guid.ToString().Trim()
        if ([string]::IsNullOrWhiteSpace($guid)) { $guid = $item.guid.InnerText.Trim() }
        if (-not [string]::IsNullOrWhiteSpace($guid)) { return $guid }
    }
    if ($item.enclosure -and $item.enclosure.url) { return $item.enclosure.url }
    return "URL unavailable"
}

function Parse-PubDate {
    param($item, [datetime]$fallback)
    $pub = $null
    if ($item.pubDate) {
        $pub = $item.pubDate.ToString().Trim()
        if ([string]::IsNullOrWhiteSpace($pub)) { $pub = $item.pubDate.InnerText.Trim() }
    }
    if (-not [string]::IsNullOrWhiteSpace($pub)) {
        try { return [datetime]$pub.ToUniversalTime() } catch { }
    }
    if ($item["dc:date"]) {
        $dc = $item["dc:date"].ToString().Trim()
        if ([string]::IsNullOrWhiteSpace($dc)) { $dc = $item["dc:date"].InnerText.Trim() }
        if (-not [string]::IsNullOrWhiteSpace($dc)) {
            try { return [datetime]$dc.ToUniversalTime() } catch { }
        }
    }
    return $fallback
}
```

### 3. Replace Failed API Sources with Working RSS Feeds
Test feeds first, then update configuration:
```powershell
# Working feeds (tested 2026-10-26):
$CoinTelegraphRss   = "https://cointelegraph.com/rss"        # OK
$TheBlockRss        = "https://www.theblock.co/rss"           # OK
$BitcoinMagazineRss = "https://bitcoinmagazine.com/.rss/full/"  # OK
$DecryptRss         = "https://decrypt.co/feed"                # OK
$UTodayRss          = "https://u.today/rss"                    # OK
$NewsBtcRss         = "https://www.newsbtc.com/feed/"          # OK
$CryptoSlateRss     = "https://cryptoslate.com/feed/"          # OK

# CoinDesk RSS returns 308 redirect - use alternative or fix URL
$CoinDeskRss        = "https://www.coindesk.com/arc/outboundfeeds/rss/"  # 308 redirect

# Add to sources array:
$sources = @(
    @{ Name = "CoinTelegraph"; Url = $CoinTelegraphRss; Weight = 1.0 },
    @{ Name = "The Block"; Url = $TheBlockRss; Weight = 1.0 },
    @{ Name = "Bitcoin Magazine"; Url = $BitcoinMagazineRss; Weight = 0.9 },
    @{ Name = "Decrypt"; Url = $DecryptRss; Weight = 0.9 },
    @{ Name = "U.Today"; Url = $UTodayRss; Weight = 0.8 },
    @{ Name = "NewsBTC"; Url = $NewsBtcRss; Weight = 0.8 },
    @{ Name = "CryptoSlate"; Url = $CryptoSlateRss; Weight = 0.8 }
)
```
Remove failed API sources (CryptoPanic - requires auth_token, 403 without).

### 4. Fix PowerShell Syntax in Source Verification and Function Returns
Replace C#-style ternary in `$()` with proper PowerShell:
```powershell
# Wrong:
Write-Output "  - CoinDesk RSS: $([string]::IsNullOrWhiteSpace((Try-WebRequest $CoinDeskRss -TimeoutSec 5)) ? 'FAILED' : 'OK')"

# Correct:
$cdOk = if ([string]::IsNullOrWhiteSpace((Try-WebRequest $CoinDeskRss -TimeoutSec 5))) { 'FAILED' } else { 'OK' }
Write-Output "  - CoinDesk RSS: $cdOk"
```

Fix function return syntax - PowerShell returns all output, not just `return` value:
```powershell
# Wrong - return with parentheses breaks in functions:
function Categorize-Story { ... return ($categories -join ", ") }

# Correct - output the joined string directly:
function Categorize-Story { ... $categories -join ", " }

# Wrong - return with parentheses:
function Get-AffectedAssets { ... return (($assets | Select-Object -Unique) -join ", ") }

# Correct - output directly:
function Get-AffectedAssets { ... ($assets | Select-Object -Unique) -join ", " }
```

### 5. Fix PowerShell Special Character Escaping
PowerShell treats `&` as call operator and `%` as modulo operator inside double-quoted strings:

**Ampersand in URLs and strings** - Use single quotes or concatenation:
```powershell
# Wrong - & in double-quoted string causes parse error:
$priceUrl = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

# Correct - single quotes or concatenation:
$priceUrl = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
# or
$priceUrl = $base + '/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
```

**Percent in format strings** - `%` is modulo operator, use `pct` or escape:
```powershell
# Wrong - % in format string causes parse error:
Write-Output ("BTC: {0:N2} USD ({1:+0.00;-0.00}% 24h)" -f $price, $change)

# Correct - replace % with pct in format strings:
Write-Output ('BTC: {0:N2} USD ({1:+0.00;-0.00} pct 24h)' -f $price, $change)
```

**Fear & Greed literal** - Avoid `&` in double-quoted output:
```powershell
# Wrong:
Write-Output "Fear & Greed Index: $($fearGreed.Value)"

# Correct:
Write-Output 'Fear and Greed Index: ' + $fearGreed.Value
# or
Write-Output "Fear and Greed Index: $($fearGreed.Value)"
```

**Nested double quotes in function returns** - PowerShell does not handle `"` inside `return` within double-quoted strings:
```powershell
# Wrong - escaped quotes inside double-quoted return string cause parse error:
return "Frame as \"smart money\" move."

# Correct - use single quotes for strings containing embedded double quotes:
return 'Frame as "smart money" move.'
```

Apply to every `return` string that contains `"` inside the text.

### 6. Re-enable Automation Job if Disabled
```bash
openclaw automations enable <job-id>
```
Reset consecutive error count.

### 7. Verify End-to-End Delivery
```bash
openclaw automations run <job-id> --wait --wait-timeout 5m --poll-interval 2s
```
Confirm: `"delivered": true` and `"deliveryStatus": "delivered"` to correct Discord channel.

## Outputs
- Fixed `macro-risk.ps1` with robust RSS parsing
- Updated sources array with 7 working RSS feeds
- Verified Discord delivery to target channel
- Automation job enabled and scheduled at HH:50 Asia/Manila
- `media-research-planner.ps1` covering 6 STZ crypto media strategy areas
- `media-research-plan-YYYY-MM-DD.md` output for Vera editorial planning

## Checks
- Script runs without syntax errors (`pwsh -File macro-risk.ps1`)
- `media-research-planner.ps1` runs without syntax errors (`pwsh -File media-research-planner.ps1`)
- All RSS feeds return items with valid URLs and pubDates
- Media research plan output file `media-research-plan-YYYY-MM-DD.md` exists with all 6 areas
- Automation job shows `enabled: true` and next run scheduled
- Manual run delivers to correct Discord channel

## Manual Component Testing (when script has syntax errors)
Test each component individually to verify data sources work:
```powershell
# Price data
Invoke-WebRequest 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true' -UseBasicParsing

# Fear & Greed
Invoke-WebRequest 'https://api.alternative.me/fng/' -UseBasicParsing

# RSS feeds
Invoke-WebRequest 'https://cointelegraph.com/rss' -UseBasicParsing -TimeoutSec 10
Invoke-WebRequest 'https://www.theblock.co/rss' -UseBasicParsing -TimeoutSec 10
```
This validates sources before fixing script syntax.

### 8. Create Media Research Planner (STZ Crypto Media Strategy)
Trigger: Expand research planning for STZ crypto media strategy; need media-research-plan-YYYY-MM-DD.md for Vera content production.

Script: `C:\Users\dizon\.openclaw\workspace-marco\media-research-planner.ps1`

6 Research Areas:
1. Important Cryptocurrency News — CoinDesk, CoinTelegraph, The Block
2. Bitcoin and Broader Market Developments — CoinGecko API, NewsBTC, CryptoSlate
3. Blockchain and DeFi Developments — Decrypt, U.Today, CoinTelegraph, The Block
4. AI Tools and Technology Relevant to Crypto — Decrypt, CoinDesk, CoinTelegraph
5. Crypto Education and Security — Decrypt, CoinTelegraph, U.Today, CryptoSlate
6. Exchange and Regulatory Announcements — CoinDesk, The Block, CoinTelegraph

PowerShell-specific fixes:
- Use `[datetime]::Parse($pub, $null, [System.Globalization.DateTimeStyles]::AssumeUniversal)` instead of `[datetime]$pub.ToUniversalTime()` for RSS pubDate parsing
- In catch blocks, assign `$_` to a local variable before string interpolation: `$errMsg = $_.Exception.Message; Write-Warning "... $errMsg"`
- Handle both RSS (XML) and JSON API sources (CoinGecko returns JSON, not RSS) using `IsApiSource` flag on each source
- Rank stories per area by relevance score, select top 5
- Flag areas with 0 stories as "DATA UNAVAILABLE" — do not fabricate content
- Output structured markdown with: Headline, What happened, Claim type, Verification level, Published timestamp (Asia/Manila + UTC), Source URL
- Verification levels: VERIFIED (Tier-1: CoinDesk/CoinTelegraph/The Block), VERIFIED (Tier-2: Bitcoin Magazine/Decrypt), UNVERIFIED (link provided)
- Claim type classification: market data, regulatory development, AI/technology development, official announcement, security incident, education/security topic, exchange announcement, general news

Run:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Users\dizon\.openclaw\workspace-marco\media-research-planner.ps1
```