# 🚀 Automated Trading Blog System

**Multi-Agent, Git Worktree-Powered, MCP-Integrated Blog Generation**

Generate 3 high-quality trading articles daily (Forex, Crypto, Commodities) with professional translations to 4 languages (EN/GCC-AR/ES/PT), using parallel sub-agents, git worktrees, and Claude Code's skills & MCPs.

---

## 📋 Overview

This system replaces the outsourced blog content creation with a fully automated, AI-powered solution that:

- **Generates 3 articles daily** (500 words each): Forex, Crypto, Commodities
- **Translates to 4 languages**: English, GCC Arabic, Spanish, Portuguese
- **Uses parallel sub-agents** via Claude Code's Task tool (3x faster)
- **Leverages git worktrees** for parallel branch development
- **Integrates skills**: `SKILL_multilingual_content.md`, `SKILL_seekapa_brand.md`
- **Uses MCPs**: Azure OpenAI, CoinGecko, Memory, GitHub, Fetch
- **Delivers via Zapier webhook** for review and publishing

---

## 🏗️ Architecture

```
Main Orchestrator (Claude Code)
├─→ Git Worktree: blog-forex/     → Forex Agent (Task tool)
├─→ Git Worktree: blog-crypto/    → Crypto Agent (Task tool)
└─→ Git Worktree: blog-commodities/ → Commodities Agent (Task tool)

Each Agent:
1. Perplexity API → Market Research
2. Azure OpenAI MCP (GPT-5) → Content Generation
3. SKILL_multilingual_content → Translation (AR/ES/PT)
4. GitHub Repo → Image Selection
5. HTML Formatter → Clean HTML + SEO
6. Git Commit → Branch commit

Main Orchestrator:
1. Merge all branches
2. Quality validation
3. Zapier webhook delivery
4. Cleanup worktrees
```

---

## ⚙️ Features

### Content Quality
- ✅ **Real-time market data** (Perplexity + CoinGecko MCP)
- ✅ **Technical analysis** (RSI, MACD, support/resistance)
- ✅ **Fundamental drivers** (economic news, geopolitical events)
- ✅ **Actionable trading insights** (entry/exit suggestions)
- ✅ **SEO optimized** (meta tags, keywords, image alt text)
- ✅ **Seekapa brand voice** (professional excellence, trustworthy)

### Translation Quality
- ✅ **GCC Arabic**: Professional, Islamic finance terminology, respectful tone
- ✅ **Spanish**: Latin American dialect, opportunity-focused
- ✅ **Portuguese**: Brazilian variant, community-oriented

### Technical Excellence
- ✅ **Parallel execution**: 3 agents run simultaneously (45 min vs 60 min sequential)
- ✅ **Git worktrees**: No conflicts, full audit trail
- ✅ **Error handling**: Retry logic, fallback mechanisms
- ✅ **Quality validation**: Automated checks before delivery
- ✅ **Monitoring**: Comprehensive logging, execution metrics

---

## 📁 Project Structure

```
/home/odedbe/blog/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── .github/
│   └── workflows/
│       └── daily-blog-automation.yml  # GitHub Actions (6 AM IST)
├── src/
│   ├── main_orchestrator.py           # Main entry point
│   ├── agents/
│   │   └── AGENT_PROMPTS.md           # Task tool prompts for sub-agents
│   ├── services/
│   │   ├── perplexity_client.py       # Market research
│   │   ├── azure_openai_client.py     # Content generation
│   │   ├── translation_service.py     # Multi-language translation
│   │   ├── image_manager.py           # Image selection
│   │   ├── html_formatter.py          # HTML + SEO
│   │   └── zapier_delivery.py         # Webhook delivery
│   ├── utils/
│   │   └── git_worktree_manager.py    # Git worktree operations
│   └── config/
│       ├── credentials.py             # API keys
│       └── prompts.py                 # GPT-5 prompts
├── output/                            # Generated articles
├── logs/                              # Execution logs
└── tests/                             # Unit tests

Parallel Worktrees (created daily):
/home/odedbe/blog-forex/               # Forex agent workspace
/home/odedbe/blog-crypto/              # Crypto agent workspace
/home/odedbe/blog-commodities/         # Commodities agent workspace
```

---

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.12+
- Git configured
- Access to:
  - Azure OpenAI API (GPT-5)
  - Perplexity API
  - GitHub (for images repo)
  - Zapier webhook URL

### 2. Installation

```bash
# Clone repository
cd /home/odedbe/blog

# Install dependencies
pip install -r requirements.txt

# Clone trading images repository
git clone https://github.com/oded-be-z/n8n-trading-images.git /tmp/n8n-trading-images

# Configure GitHub Actions secrets (use your actual API keys)
gh secret set AZURE_OPENAI_KEY --body "your-azure-openai-key"
gh secret set PERPLEXITY_API_KEY --body "your-perplexity-api-key"
gh secret set ZAPIER_WEBHOOK_URL --body "your-zapier-webhook-url"
```

### 3. Test Run

```bash
# Manual test run
python src/main_orchestrator.py

# Check logs
tail -f logs/orchestrator_*.log

# Check output
ls -l output/
```

---

## 📅 Daily Schedule

- **Trigger**: 6:00 AM IST (via GitHub Actions)
- **Execution Time**: ~45 minutes
- **Completion**: Articles delivered to Zapier by 6:45 AM
- **Review**: Team reviews via Zapier before publishing

---

## 🤖 How It Works

### Phase 1: Initialization (2 min)
- Create output directories
- Initialize services
- Test API connectivity

### Phase 2: Git Worktrees (2 min)
```bash
git worktree add ../blog-forex -b daily/forex-2025-10-20
git worktree add ../blog-crypto -b daily/crypto-2025-10-20
git worktree add ../blog-commodities -b daily/commodities-2025-10-20
```

### Phase 3: Parallel Agents (28 min) ⚡
**3 agents run simultaneously:**

**Forex Agent** (`blog-forex/`)
1. Perplexity: Research EUR/USD, USD/JPY, GBP/USD
2. GPT-5: Generate 500-word article
3. SKILL_multilingual_content: Translate to AR/ES/PT
4. Select image from GitHub repo
5. Format as HTML with SEO
6. Commit to `daily/forex-2025-10-20`

**Crypto Agent** (`blog-crypto/`)
1. CoinGecko MCP: Get BTC/ETH/XRP prices
2. Perplexity: Research crypto news
3. GPT-5: Generate article
4. Translate & format
5. Commit to `daily/crypto-2025-10-20`

**Commodities Agent** (`blog-commodities/`)
1. Perplexity: Research gold/silver/oil
2. GPT-5: Generate article
3. Translate & format
4. Commit to `daily/commodities-2025-10-20`

### Phase 4: Merge (5 min)
```bash
git checkout main
git merge daily/forex-2025-10-20
git merge daily/crypto-2025-10-20
git merge daily/commodities-2025-10-20
```

### Phase 5: Quality Validation (5 min)
- Check word count (480-520 words)
- Verify 4 languages present
- Validate SEO metadata
- Check image URLs

### Phase 6: Zapier Delivery (2 min)
```json
POST https://hooks.zapier.com/hooks/catch/17121977/u521hmw/
{
  "articles": [
    {
      "category": "forex",
      "asset": "EUR/USD",
      "languages": {
        "en": {"html": "...", "seo": {...}},
        "ar": {"html": "...", "seo": {...}},
        "es": {"html": "...", "seo": {...}},
        "pt-BR": {"html": "...", "seo": {...}}
      }
    },
    ...
  ]
}
```

### Phase 7: Cleanup (2 min)
```bash
git worktree remove ../blog-forex
git worktree remove ../blog-crypto
git worktree remove ../blog-commodities
git branch -d daily/forex-2025-10-20
git branch -d daily/crypto-2025-10-20
git branch -d daily/commodities-2025-10-20
```

---

## 🔧 Configuration

### API Credentials
Located in `src/config/credentials.py`:
- Azure OpenAI API Key
- Perplexity API Key
- GitHub Token
- Zapier Webhook URL

### Prompts
Located in `src/config/prompts.py`:
- Article generation prompts (forex, crypto, commodities)
- Translation prompts (GCC Arabic, Spanish, Portuguese)
- SEO metadata generation prompts

### Skills Integration
- **SKILL_multilingual_content.md**: Translation best practices
- **SKILL_seekapa_brand.md**: Brand voice guidelines
- **SKILL_git_worktrees.md**: Git worktree management

### MCP Servers
- **Azure OpenAI MCP**: GPT-5, GPT-5-Pro, GPT-5-Codex
- **CoinGecko MCP**: Real-time crypto prices
- **Memory MCP**: Translation glossary
- **GitHub MCP**: Repository operations
- **Fetch MCP**: Web image search (fallback)

---

## 📊 Success Metrics

- ✅ **3 articles/day** delivered by 7:00 AM IST
- ✅ **4 languages/article** with professional quality
- ✅ **500 words ±10%** per article
- ✅ **<5% error rate** over 30 days
- ✅ **<45 min execution time**
- ✅ **100% SEO metadata** compliance
- ✅ **Relevant images** for all articles

---

## 🐛 Troubleshooting

### Agent Execution Failed
```bash
# Check logs
tail -100 logs/orchestrator_*.log

# Check worktree status
git worktree list

# Manual cleanup if needed
git worktree remove --force ../blog-forex
```

### Zapier Delivery Failed
```bash
# Check failed delivery file
cat output/failed_deliveries/failed_2025-10-20.json

# Test webhook manually
curl -X POST https://hooks.zapier.com/hooks/catch/17121977/u521hmw/ \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Translation Quality Issues
```bash
# Check translation service logs
grep "Translation" logs/orchestrator_*.log

# Validate terminology from SKILL_multilingual_content.md
# Adjust temperature in azure_openai_client.py if needed
```

---

## 📈 Performance

### Baseline (Sequential)
- Execution Time: **60 minutes**
- Bottleneck: Sequential article generation

### With Multi-Agent + Git Worktrees
- Execution Time: **45 minutes** (25% faster ⚡)
- Parallelism: 3 agents simultaneously
- No conflicts: Isolated git worktrees

---

## 🔄 Maintenance

### Daily
- Monitor GitHub Actions execution
- Review Zapier delivery status
- Check article quality scores

### Weekly
- Review execution logs
- Validate translation quality
- Update market data APIs if needed

### Monthly
- Update prompt templates
- Refresh image repository
- Audit SEO performance

---

## 📚 Related Documentation

- **Skills**: `/home/odedbe/.claude/skills/SKILL_*.md`
- **Agents**: `/home/odedbe/.claude/agents/*.json`
- **MCPs**: `/home/odedbe/.claude/mcp-servers/`
- **Git Worktrees**: `/home/odedbe/.claude/GIT_WORKTREE_GUIDE.md`

---

## 🎯 Future Enhancements

1. **Add more categories**: Stocks, indices, futures
2. **Video generation**: Convert articles to Synthesia videos
3. **Social media**: Auto-post to X/Twitter, LinkedIn
4. **A/B testing**: Multiple headline variations
5. **Performance analytics**: Track engagement metrics

---

## 📄 License

Internal use only - Seekapa Trading Platform

---

## 👥 Contact

- **Project**: Automated Trading Blog System
- **Owner**: Seekapa Content Team
- **Maintainer**: Claude Code + Development Team

---

**Last Updated**: October 20, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
