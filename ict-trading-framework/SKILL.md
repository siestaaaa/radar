---
name: ict-trading-framework
description: ICT-based trading framework for systematic trade analysis and execution using Smart Money Concepts. Use when analyzing markets, identifying trade setups, or executing trades based on ICT principles including liquidity, market structure shifts (MSS), change in state of delivery (CISD), fair value gaps (FVG), and multi-timeframe analysis.
---

# ICT Trading Framework

Complete 7-step trading system based on ICT Smart Money Concepts from TTrades.

## Quick Reference

| Step | Concept | Purpose |
|------|---------|---------|
| 1 | Liquidity | Define target (PDH/PDL) |
| 2 | CISD/MSS | Confirm direction |
| 3 | FVG | Entry zone |
| 3B | Protected Swing | Stop loss |
| 5 | Candle 3 | Timing |
| 6 | MTF | Alignment |
| 7 | Full Strategy | Integration |

## When to Use This Skill

Use this skill when:
- Analyzing price action for trade setups
- Determining market direction and bias
- Finding entry and exit points
- Managing risk with stop placement
- Aligning multiple timeframe analysis

## Framework Overview

### Core Philosophy
1. **Liquidity drives price** — Price is drawn to untapped liquidity
2. **Confirmation required** — Never trade without CISD or MSS
3. **Structure-based** — All decisions based on market structure, not indicators
4. **Risk-first** — Minimum 1:2 R:R, protected swing stops

### Entry Checklist

```
□ Step 1: Untapped liquidity identified (PDH/PDL priority)
□ Step 2: CISD or MSS after liquidity interaction
□ Step 3: Valid FVG from displacement
□ Step 3B: Protected swing clear for stop
□ Step 6: HTF bias aligned
□ R:R >= 1:2
□ ALL checked → ENTER
```

### No Trade Conditions

- No clear HTF bias
- No liquidity interaction
- No CISD or MSS confirmation
- No valid FVG
- R:R < 1:2
- HTF vs LTF conflict

## Detailed Steps

See references for complete step-by-step details:
- [Step 1: Liquidity](references/step1-liquidity.md)
- [Step 2: CISD & MSS](references/step2-cisd-mss.md)
- [Step 3: FVG](references/step3-fvg.md)
- [Step 3B: Protected Swing](references/step3b-protected-swing.md)
- [Step 5: Candle 3](references/step5-candle3.md)
- [Step 6: MTF Alignment](references/step6-mtf.md)
- [Step 7: Full Strategy](references/step7-full-strategy.md)

## Entry Types

| Type | Condition | Risk Level |
|------|-----------|------------|
| Aggressive | Touch FVG | Higher |
| Refined | CE 50% | Medium |
| Conservative | LTF confirmation | Lower |

### Entry Type Output Format

```json
{
  "entry_type": "aggressive | refined | conservative",
  "entry_zone": "price level",
  "stop_loss": "protected swing",
  "take_profit": "liquidity target",
  "confidence": "high | medium | low",
  "execute": true | false,
  "no_trade_reason": "reason if not executing"
}
```

## Risk Control

- Max 2-3 losses in a row → stop session
- Reduce risk after consecutive losses
- No revenge trading
- When in doubt → NO TRADE

## Flex Rules

- CISD OR MSS present → valid (not both required)
- FVG slightly messy + strong displacement → still valid
- R:R slightly below 1:2 + high probability → optional

## Market Filter

- Do NOT trade in tight consolidation
- Prefer trending or expansion phase
- Range detected → only trade edges or skip
