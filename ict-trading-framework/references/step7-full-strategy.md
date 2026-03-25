# Step 7: Full Strategy Integration

## Core Rules

1. **Step 1: Liquidity** — Identify nearest UNTAPPED liquidity as target
2. **Step 2: Confirmation** — Wait for CISD or MSS after liquidity interaction
3. **Step 3: FVG** — Identify FVG from displacement as entry zone
4. **Step 3B: Stop** — Place stop beyond protected swing
5. **Step 6: Alignment** — Follow HTF direction only
6. **R:R** — Minimum 1:2

## Optional Enhancements

- Candle 3 closure for better timing
- Equilibrium entry (CE 50%)
- Session timing (London/NY)
- Higher timeframe confluence

## Entry Checklist

```
□ Step 1: Mark all liquidity → Filter UNTAPPED → Pick nearest
□ Step 1: Market state clear? If UNCLEAR → NO TRADE
□ Step 6 HTF: Bias aligns with target? If NO → NO TRADE
□ Step 2: Price interacts with liquidity
□ Step 2: CISD or MSS forms? If NO → WAIT
□ Step 6 MTF: Confirmation aligns? If NO → NO TRADE
□ Step 3: Valid FVG present? If NO → WAIT
□ Step 3B: Protected swing clear? If NO → SKIP
□ Step 5: Candle 3 closure valid?
□ Step 3: Price in FVG zone?
□ Step 6 LTF: Entry aligns?
□ R:R >= 1:2?
□ ALL checked → ENTER
```

## Entry Execution

| Type | Entry | Risk |
|------|-------|------|
| Aggressive | Touch FVG | Higher |
| Refined | CE 50% | Medium |
| Conservative | LTF confirmation | Lower |

**Stop:** Protected swing
**Target:** Step 1 liquidity

## Entry Type Output (For Bot Conversion)

```json
{
  "entry_type": "aggressive | refined | conservative",
  "entry_zone": "FVG range / CE 50% level",
  "stop_loss": "protected swing level",
  "take_profit": "Step 1 liquidity target",
  "confidence": "high | medium | low",
  "execute": true | false,
  "no_trade_reason": "if execute = false"
}
```

### Entry Type Definitions

- **Aggressive** = Entry at first touch of FVG (higher risk, earlier entry)
- **Refined** = Entry at Consequent Encroachment 50% (optimal R:R)
- **Conservative** = Wait for LTF confirmation inside FVG (lower risk, later entry)

## Full Flow Example

**Bullish Example:**
1. PDH untapped above → bullish target
2. Price sweeps PDL → bullish CISD forms
3. FVG created at sweep point
4. Protected swing = PDL low
5. Candle 3 closes bullish
6. Daily bullish + 1H bullish + 5M FVG = ALIGNED
7. **ENTER LONG**

## No Trade Conditions

- No clear HTF bias
- No liquidity interaction
- No CISD or MSS
- No valid FVG
- R:R < 1:2
- HTF vs LTF conflict

## Guardrails

- Do NOT trade against HTF direction
- Do NOT enter without confirmation
- Do NOT force trades
- When in doubt → NO TRADE

## Flex Rules

- CISD OR MSS present → valid (not both required)
- FVG slightly messy + strong displacement → still valid
- R:R slightly below 1:2 + high probability → optional

## Market Filter

- Do NOT trade in tight consolidation
- Prefer trending or expansion phase
- Range detected → only trade edges or skip

## Risk Control

- Max 2-3 losses in a row → stop session
- Reduce risk after consecutive losses
- Do not revenge trade

## Complete Framework Summary

| Step | Function | Output |
|------|----------|--------|
| 1 | Liquidity | Target |
| 2 | CISD/MSS | Confirmation |
| 3 | FVG | Entry zone |
| 3B | Protected Swing | Stop loss |
| 5 | Candle 3 | Timing |
| 6 | MTF | Alignment |
| 7 | Integration | Execute |

**Golden Rule:** All 6 steps must ✅. One ❌ = NO TRADE.
