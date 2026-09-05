# Solana Sniper Bot MCP

**Autonomous Solana trading bot with 281 MCP tools for AI-assisted control across four trading modes.**

Four trading modes. One Windows desktop app. Full MCP integration for Claude, Cursor, Devin, and any MCP-compatible AI assistant.

## IMPORTANT: Requires the Solana Sniper Bot V4 Windows Application

This MCP server is **useless on its own**. It requires the **Solana Sniper Bot V4** Windows GUI application to be installed and running.

**Download the Windows executable from [solsniperbot.co](https://solsniperbot.co/download.html).**

## What It Does

The Solana Sniper Bot watches the Solana blockchain for trading opportunities across four modes:

1. **Meme / New-Token Sniping** — Detects new Pump.fun token launches, applies safety/liquidity/market-cap/volume/holder/age/creator-holding filters, executes buys through Pump.fun bonding curves or Jupiter, and manages positions with take-profit ladders, trailing stops, rug detection, volume-death detection, and momentum-reversal detection.

2. **Spot Trading** — General spot trading via the Jupiter DEX aggregator with market/limit orders, DCA, portfolio rebalancing, risk-level presets, and slippage control.

3. **Perpetual Futures** — Long and short positions with configurable leverage, margin trading, funding-rate controls, liquidation avoidance, market discovery, and signal generation.

4. **Mirror Mode** — Whale-wallet copy trading with proportional sizing, configurable limits, token filtering, and dry-run support.

Using the 281 MCP tools, your AI agent can start/stop bots, execute trades, configure safety filters, query positions and P&L, manage wallets, analyze market data, and fine-tune strategy across all four trading modes.

## Pricing

- **7-day free trial** (168 hours of actual bot running time — no credit card required)
- **First month: $49.99** (50% off with promo code `SOLV4FIRST50`)
- **$99.99/month** thereafter — Cancel anytime

Subscribe at: [https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07](https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07?prefilled_promo_code=SOLV4FIRST50)

## Installation

```bash
pip install solana-snipe-bot-mcp
```

## Client Configuration

```json
{
  "mcpServers": {
    "solana-snipe-bot": {
      "command": "python",
      "args": ["-m", "solana_snipe_bot_mcp"],
      "env": {
        "SOLANA_SNIPER_BOT_DIR": "P:\\snipe-bot"
      }
    }
  }
}
```

## Links

- **Website:** [https://solsniperbot.co/](https://solsniperbot.co/)
- **Download:** [https://solsniperbot.co/download.html](https://solsniperbot.co/download.html)
- **MCP Landing Page:** [https://solsniperbot.co/mcp/](https://solsniperbot.co/mcp/)
- **PyPI:** [https://pypi.org/project/solana-snipe-bot-mcp/](https://pypi.org/project/solana-snipe-bot-mcp/)
- **MCP Registry:** `co.solsniperbot/solana-snipe-bot-mcp`

## License

Proprietary. 7-day free trial (168 hours of actual bot running time). First month $49.99 with code SOLV4FIRST50, then $99.99/month. Cancel anytime. Use at your own risk. On-chain trading is risky.
