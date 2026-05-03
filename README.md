# Carousel Automation — @marketing.shekhar

Generates 2 fresh Instagram carousels daily (8 AM + 4:30 PM Bali time) and deploys to Vercel.
Runs entirely on GitHub servers — laptop can be off.

## How it works
1. GitHub Actions wakes up on schedule
2. Tavily searches for current Instagram trends (live research)
3. Claude API thinks about what topic will perform best today
4. Generates complete carousel-light HTML
5. Deploys to `shekhar-carousels` on Vercel
6. You get the live URL in the Actions run log

## Setup (one-time)

Go to **GitHub repo → Settings → Secrets → Actions** and add:

| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `VERCEL_TOKEN` | `vca_2mhwdCAOkhCNMDK6qUeeX4hrxxjAUzlkZ0DmS1E8f0k5KdnU3d0sxCqB` |
| `TAVILY_API_KEY` | `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` |

## Manual trigger
Go to **Actions → Morning Carousel** (or Afternoon) → **Run workflow**

## Timezone
Workflows run at 8:00 AM and 4:30 PM UTC+8 (Bali/Singapore).
To change, edit the `cron:` lines in `.github/workflows/*.yml`.
- UTC+5:30 (India): use `30 2 * * *` (morning) and `30 11 * * *` (afternoon)
- UTC+7 (Jakarta): use `0 1 * * *` (morning) and `30 9 * * *` (afternoon)
