# Solana Sniper Bot MCP — Marketplace Listing

**Version:** 1.1.0

## Download

> **The MCP server is useless without the Solana Sniper Bot Windows application.**
> The MCP exposes the bot's controls to your AI assistant, but the bot itself — the scanner, trader, and GUI — runs as a Windows desktop app. Install both.

1. **Download the Windows app** from [https://solana-snipe-bot-landing.pages.dev/](https://solana-snipe-bot-landing.pages.dev/)
2. **Install the MCP server** via pip:
   ```bash
   pip install solana-snipe-bot-mcp
   ```
3. **Or download from PyPI:**
   https://pypi.org/project/solana-snipe-bot-mcp/

## One-liner

Control and audit an autonomous Solana meme-coin sniper bot with 40 MCP tools. Buy, sell, validate strategy, verify on-chain positions, track P&L, and monitor Pulse trends from Claude, Cursor, Devin, or any MCP client.

## Tags

`solana` `sniper` `pumpfun` `mcp` `model-context-protocol` `trading-bot` `meme-coin` `ai-agent` `jupiter` `profit`

## Description

**Solana Sniper Bot MCP** exposes every control, setting, and data view from the Solana Sniper Bot as a Model Context Protocol server. The bot autonomously scans the Solana blockchain for new meme-coin launches (especially Pump.fun), applies configurable safety filters, executes buys and sells on Pump.fun bonding curves or Jupiter, and manages positions with take-profit ladders, trailing stops, and rug detection.

Your AI assistant gets 40 tools to:
- Start/stop the bot and panic-sell
- Buy and sell specific tokens
- Read and update the full `config.json`
- Query open positions, P&L, wallet balances, and fees
- Manage Pulse trend matching and price history
- Reclaim ATA rent from empty token accounts

Using the MCP server tools, your agentic AI can analyze how market conditions change over time. With more than 45 tools exposed to your agent, it can continuously fine-tune bot settings and help zero in on a strategy aligned with your risk factors and preferred level of aggressiveness.

## Installation

```bash
pip install solana-snipe-bot-mcp
```

Set the project directory before launching:

```bash
export SOLANA_SNIPER_BOT_DIR=/path/to/snipe-bot   # macOS/Linux
set SOLANA_SNIPER_BOT_DIR=P:\snipe-bot            # Windows
python -m solana_snipe_bot_mcp
```

## Client Config Examples

### Claude Desktop

```json
{
  "mcpServers": {
    "solana-snipe-bot": {
      "command": "python",
      "args": ["-m", "solana_snipe_bot_mcp"],
      "env": { "SOLANA_SNIPER_BOT_DIR": "P:\\snipe-bot" }
    }
  }
}
```

### Cursor

```json
{
  "mcpServers": {
    "solana-snipe-bot": {
      "command": "python",
      "args": ["-m", "solana_snipe_bot_mcp"],
      "env": { "SOLANA_SNIPER_BOT_DIR": "P:\\snipe-bot" }
    }
  }
}
```

## Tool Categories

- **Bot Control:** start_bot, stop_bot, sell_all, sell_position, buy_mint, get_bot_stats
- **Config:** get_config, update_config, save_settings, get_config_catalog, validate_current_config, update_config_batch
- **Strategy Profiles:** preview_strategy_profile, apply_strategy_profile
- **Positions:** get_open_positions, get_positions_status, get_graduation_status, close_position, get_bot_status, audit_open_positions, get_position_exit_quote
- **P&L:** get_pnl_tally, reset_pnl_tally, refresh_pnl, get_fee_summary, analyze_trade_performance
- **Wallet:** get_wallet_balances, transfer_sol, move_all_sol
- **Pulse:** get_pulse_results, set_pulse_match_mode, get_pulse_price_history, clear_pulse_results
- **Log:** get_log, clear_log
- **Utility:** close_empty_token_accounts, get_pending_commands, clear_commands

## Links

- **MCP Source Repo:** https://github.com/solara-sniper-bot/MCP
- **Download App:** https://solana-snipe-bot-landing.pages.dev/
- **Buy License ($99.99):** https://buy.stripe.com/3cI7sLc2l3Et1RU4IE7bW06
- **PyPI:** https://pypi.org/project/solana-snipe-bot-mcp/

## What's New in v1.1.0

- **Upgraded from 32 to 40 MCP tools** — added 8 new tools for strategy profiles, config validation, trade analysis, on-chain auditing, and read-only exit quotes.
- **Strategy profile system with schema validation** — centralized `small_account_guarded_v1` profile plus `preview_strategy_profile` and `apply_strategy_profile` tools, with confirmation gates on profile and batch mutations.
- **Hard stop loss, reserve-aware sizing, min/max trade sizes** — new `hard_stop_loss_pct`, `min_wallet_reserve_sol`, `min_trade_size_sol`, and `max_trade_size_sol` settings protect positions before the trailing stop arms and keep entries within safe bounds.
- **Fixed Pump.fun price-impact filter and bonding-curve progress calculation** — the impact filter no longer silently skips itself, and progress now uses real SOL reserves instead of incompatible token reserve values.
- **Replaced retired Jupiter v6** — swapped the dead `quote-api.jup.ag/v6` integration for the Swap v1 lite endpoint, and replaced Jupiter Price v6 in Pulse tracking with Price API v3.
- **Graduated positions now persist and monitor** instead of being dropped — positions stay tracked while a route is temporarily unavailable, and buy/sell state only changes after a transaction reaches confirmed/finalized status.
- **On-chain ownership auditing and read-only exit quotes** — `audit_open_positions` compares `open_positions.json` to the wallet's actual token accounts, and `get_position_exit_quote` returns a quote without building, signing, or submitting a transaction.
- **New GUI controls** for entry budgets, hard/trailing exits, staged take profit, and advanced entry filters — plus a fix so GUI saves preserve hidden/advanced settings instead of deleting them.
- **Added unit tests** for strategy validation, sizing, take-profit parsing, trade analysis, and Jupiter endpoint selection.

See the full CHANGELOG.md for details.

## License

Proprietary. All rights reserved. The Solana Sniper Bot Windows application requires a license — a generous full-week (168 hours) free trial is included, and a lifetime license is available for $99.99 at https://buy.stripe.com/3cI7sLc2l3Et1RU4IE7bW06
