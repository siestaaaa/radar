# Step 1: Liquidity

## Core Concept
Liquidity drives price. Price is constantly drawn to areas where stop orders cluster.

## Liquidity Types

### Buy-Side Liquidity (BSL)
- Area above swing highs
- Stop orders from shorts + take profits from longs
- Price drawn upward to clear

### Sell-Side Liquidity (SSL)
- Area below swing lows
- Stop orders from longs + take profits from shorts
- Price drawn downward to clear

## Priority Levels

1. **Previous Day High/Low (PDH/PDL)** — Highest priority
2. **Previous Week High/Low (PWH/PWL)**
3. **Equal Highs/Lows**
4. **Clear Swing High/Low**
5. **Internal/Minor Swings**

## Liquidity Status

| Status | Meaning | Action |
|--------|---------|--------|
| UNTAPPED | Valid target | Trade toward |
| SWEPT | Weak/Look opposite | Caution |
| FULLY TAKEN | Ignore | Skip |
| FAILED SWEEP | Reversal signal | Watch for shift |

## Market State

- **TRENDING** → Target external liquidity (PDH/PDL, PWH/PWL)
- **RANGING** → Target internal liquidity (equal highs/lows)
- **UNCLEAR** → Wait, do not trade

## Conflict Resolution

1. Multiple untapped liquidity → Compare priority first
2. Same priority → Choose nearest
3. Equal distance/unclear → Wait for confirmation
4. Never force direction without clear dominance

## Liquidity Mapping

1. Mark PDH and PDL
2. Mark PWH and PWL
3. Mark equal highs and equal lows
4. Mark most recent swing high and swing low
5. Extend all levels forward as active zones

## Target Validation

- Target must be clear and visible
- Target must NOT be already swept
- Target should have clean price path
- If path messy → lower probability or wait

## Time Context

- Prefer during active sessions (London / New York)
- Avoid low volatility periods
- Session opens increase probability

## No Trade Conditions

- Market state UNCLEAR
- No clear UNTAPPED liquidity
- Conflict unresolved
- Target path messy/choppy
- No session volatility

## Guardrails

- Liquidity defines POTENTIAL direction only
- DO NOT enter trade based on liquidity alone
- WAIT for confirmation (Step 2)
