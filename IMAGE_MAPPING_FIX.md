# Image Selection Bug Fix - Silver/Gold Mismatch

## Issue Identified
**Problem:** Silver commodities article displayed a gold image instead of silver image.

**Root Cause:**
- Agent prompt hardcoded image path to `/tmp/n8n-trading-images/gold/`
- When agent selected "Silver" as the commodity, it still pulled from gold folder
- No dynamic mapping between commodity type and image folder

## Investigation Results

### Available Image Folders
```
/tmp/n8n-trading-images/
├── aud/
├── blog_samples/          ← Contains silver images!
├── btc-usd/
├── ethereum/
├── eur-usd/
├── gbp-usd/
├── gold/                  ← Gold images
├── usd-cad/
└── xrp/
```

### Commodity Image Mapping
```
Gold   → /tmp/n8n-trading-images/gold/gold-*.jpg
Silver → /tmp/n8n-trading-images/blog_samples/sample_10_silver_2.jpg
Oil    → /tmp/n8n-trading-images/blog_samples/ (use generic trading samples)
Copper → /tmp/n8n-trading-images/blog_samples/ (use generic trading samples)
```

## Fix Applied

### Updated Agent Prompt
Changed from:
```
5. Select image from /tmp/n8n-trading-images/gold/ or other commodity folders
```

To:
```
5. Select image based on commodity:
   - Gold: /tmp/n8n-trading-images/gold/gold-[1-10].jpg
   - Silver: /tmp/n8n-trading-images/blog_samples/sample_10_silver_2.jpg
   - Oil/Copper: /tmp/n8n-trading-images/blog_samples/sample_2_gold_5.jpg (generic commodities)
```

### Code Changes
- Updated `src/agents/AGENT_PROMPTS.md` with proper commodity→folder mapping
- Added validation: "If selected commodity is Silver, MUST use silver image"

## Prevention Strategy

### For Future Runs
1. **Pre-flight check:** Validate image exists for selected commodity
2. **Fallback logic:** If specific image not found, use blog_samples
3. **Logging:** Log image selection decision for audit trail
4. **Agent instruction:** Explicit mapping table in prompt

### Long-term Solution
Add more commodity images to repository:
```bash
/tmp/n8n-trading-images/
├── silver/      # Add this
├── oil/         # Add this
├── copper/      # Add this
└── commodities/ # Generic fallback
```

## Status
✅ Issue identified
✅ Root cause documented
✅ Fix implemented
🔄 Regenerating commodities article with correct image
📤 Will update HTML viewer
📤 Will resend to Zapier

## Test Results (After Fix)
- [ ] Silver article shows silver image
- [ ] Gold article shows gold image
- [ ] Image path logged correctly
- [ ] HTML viewer updated
- [ ] Zapier delivery successful
