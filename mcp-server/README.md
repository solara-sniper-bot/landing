<!-- mcp-name: co.solsniperbot/solana-snipe-bot-mcp -->

<p align="center">
  <img src="https://solsniperbot.co/mcp/mcp-software-box.png" alt="Solana Sniper Bot MCP" width="500">
</p>

<p align="center">
  <strong>Autonomous Solana trading bot with 281 MCP tools across four trading modes — controlled by Claude, Cursor, Devin, or any MCP-compatible AI.</strong>
</p>

<p align="center">
  <strong>Meme sniping · Spot trading · Perpetual futures · Mirror copy-trading · 7-day free trial · No credit card required</strong>
</p>

---

## ⚠️ READ THIS FIRST — The MCP Is Useless Without the Windows App

**This MCP server does absolutely nothing on its own.** It is a remote-control interface — a set of tools that lets your AI assistant talk to the **Solana Sniper Bot V4** Windows application. Without that application installed and running, every tool call returns empty data or an error.

You need **both** pieces:

| Component | What it is | Required? |
|---|---|---|
| **Solana Sniper Bot V4** (Windows app) | The actual trading bot — scanner, executor, GUI, wallet management | **Yes — absolutely required** |
| **solana-snipe-bot-mcp** (this repo) | The MCP server that lets AI control the bot | Optional add-on |

### Download the Windows App

> **Download:** [https://solsniperbot.co/download.html](https://solsniperbot.co/download.html)

---

## Free Trial — A Full Week of Trading

The Solana Sniper Bot comes with a **free 7-day trial**: you get **168 hours (7 days)** of actual bot running time — not calendar days, but real hours the bot is actively trading. That's an entire week of live sniping, position management, and P&L tracking to see if the bot works for you.

**No credit card required to start.** Download the app, run it, and decide for yourself. When the trial expires, the Go Live button is disabled until you subscribe.

## Pricing

- **7-day free trial** — 168 hours of actual bot running time (no credit card required)
- **First month: $49.99** (50% off with promo code `SOLV4FIRST50`)
- **$99.99/month** thereafter — Cancel anytime

> **Subscribe:** [https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07](https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07?prefilled_promo_code=SOLV4FIRST50)

---

## What Is This?

**Solana Sniper Bot MCP** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives AI assistants full control over Solana Sniper Bot V4. It exposes **281 tools** across four trading modes:

1. **Meme / New-Token Sniping** — Detects new Pump.fun token launches, applies safety/liquidity/market-cap/volume/holder/age/creator-holding filters, executes buys through Pump.fun bonding curves or Jupiter, and manages positions with take-profit ladders, trailing stops, rug detection, volume-death detection, and momentum-reversal detection.

2. **Spot Trading** — General spot trading via the Jupiter DEX aggregator with market/limit orders, DCA, portfolio rebalancing, risk-level presets, and slippage control.

3. **Perpetual Futures** — Long and short positions with configurable leverage, margin trading, funding-rate controls, liquidation avoidance, market discovery, and signal generation.

4. **Mirror Mode** — Whale-wallet copy trading with proportional sizing, configurable limits, token filtering, and dry-run support.

Using the 281 MCP tools, your AI agent can start/stop bots, execute trades, configure safety filters, query positions and P&L, manage wallets, analyze market data, and fine-tune strategy across all four trading modes.

> **Important:** The MCP server alone does nothing. It requires the **Solana Sniper Bot V4** Windows application to be installed and running. Download it from [https://solsniperbot.co/download.html](https://solsniperbot.co/download.html).

### How It Works

```
Your AI Assistant (Claude, Cursor, Devin, etc.)
       │
       │  talks MCP (stdio)
       ▼
  solana_snipe_bot_mcp/server.py  ← runs on your machine
       │
       │  reads/writes JSON state files in your snipe-bot directory
       ▼
  SolanaSniperBot.exe (required)  ← the Windows GUI / bot executable
       │
       ▼
  Helius RPC Pool (up to 10 keys)  ← round-robin load-balanced RPC calls
       │
       ▼
  Pump.fun bonding curve           ← direct buy/sell instructions
  Jupiter Aggregator               ← graduated-token & spot swaps
  Orderly Network (Raydium Perps)  ← perpetual futures routing
```

The MCP server runs as a separate process and communicates with the running bot through JSON command queues and state files. It reads configuration, positions, trade history, P&L tallies, wallet balances, and market data to give your AI assistant a complete, real-time view of the bot's state across all four trading modes.

---

## Quick Start

### Prerequisites

- **Windows 10/11**
- **Python 3.10+**
- **The Solana Sniper Bot V4 Windows application** — download from [https://solsniperbot.co/download.html](https://solsniperbot.co/download.html)
- **A funded Solana wallet** (trading wallet + savings wallet keypairs)
- **Helius RPC endpoint** with API key
- An MCP-compatible AI assistant (Claude Desktop, Cursor, Devin, Codex, etc.)

### Step 1 — Install the MCP Server

From PyPI:

```bash
pip install solana-snipe-bot-mcp
```

### Step 2 — Configure Your AI Assistant

Set the project directory so the MCP server can find your bot's state files:

```bash
# Windows
set SOLANA_SNIPER_BOT_DIR=P:\snipe-bot

# Or on the command line when launching
python -m solana_snipe_bot_mcp
```

#### Claude Desktop

Edit `claude_desktop_config.json`:

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

#### Cursor

Edit `.cursor/mcp.json`:

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

#### Devin

Add to `mcp_config.json`:

```json
{
  "mcpServers": {
    "snipe-bot": {
      "command": "python",
      "args": ["-m", "solana_snipe_bot_mcp"],
      "env": {
        "SOLANA_SNIPER_BOT_DIR": "P:\\snipe-bot"
      }
    }
  }
}
```

#### Claude Code

```bash
claude mcp add solana-snipe-bot -- python -m solana_snipe_bot_mcp
```

#### Any MCP Client (generic)

The server uses **stdio transport**. Launch it with:

```bash
set SOLANA_SNIPER_BOT_DIR=P:\snipe-bot
python -m solana_snipe_bot_mcp
```

### Step 3 — Start the Bot

Ask your AI assistant:

> "Start the Solana sniper bot"

The assistant calls `start_bot`. Then try:

> "What is my wallet balance and open positions?"

---

## All 281 Tools

### Bot Control (6)
`start_bot`, `stop_bot`, `sell_all`, `sell_position`, `buy_mint`, `get_bot_stats`

### RPC Pool (3)
`get_rpc_pool_status`, `set_rpc_pool_key`, `set_rpc_pool_skip_until` — No API key values exposed.

### Configuration (8)
`get_config`, `update_config`, `update_config_batch`, `get_config_catalog`, `validate_current_config`, `preview_strategy_profile`, `apply_strategy_profile`, `save_settings`

### Positions (8)
`get_open_positions`, `get_positions_status`, `get_graduation_status`, `audit_open_positions`, `get_position_exit_quote`, `close_position`, `get_bot_status`, `get_pending_commands`

### Trade History & P&L (8)
`get_trade_history`, `analyze_trade_performance`, `clear_trade_history`, `get_pnl_tally`, `reset_pnl_tally`, `refresh_pnl`, `get_fee_summary`, `clear_commands`

### Wallet (3)
`get_wallet_balances`, `transfer_sol`, `move_all_sol`

### Pulse Trends (6)
`get_pulse_results`, `set_pulse_match_mode`, `clear_pulse_results`, `get_pulse_price_history`, `get_pulse_purchase_preview`, `buy_pulse_asset`

### Trading Mode (1)
`set_trading_mode`

### Log & Commands (2)
`get_log`, `clear_log`

### ATA Rent (1)
`close_empty_token_accounts`

### Meme Bot — Safety & Filters (12)
`set_meme_max_buy_amount`, `set_meme_min_buy_amount`, `set_meme_min_liquidity`, `set_meme_min_market_cap`, `set_meme_min_volume_24h`, `set_meme_min_holders`, `set_meme_max_token_age`, `set_meme_max_creator_holdings_pct`, `set_meme_max_positions`, `set_meme_position_size_pct`, `set_meme_slippage_bps`, `add_to_blacklist`

### Meme Bot — Exit Strategy (11)
`set_meme_stop_loss_pct`, `set_meme_take_profit_pct`, `set_meme_tp_ladder_steps`, `set_meme_trailing_stop`, `set_meme_rug_detection`, `set_meme_volume_death_detection`, `set_meme_momentum_reversal`, `set_meme_position_timeout`, `enable_meme_stop_loss`, `enable_meme_take_profit_ladder`, `enable_meme_trailing_stop`

### Meme Bot — Signals & Auto-Buy (3)
`enable_meme_auto_buy`, `enable_meme_signals`, `clear_meme_signals`

### Meme Bot — Savings & Alerts (4)
`set_meme_auto_savings`, `set_meme_savings_threshold`, `set_meme_alert_threshold`, `set_meme_exposure`

### Meme Bot — Analytics (15)
`get_meme_statistics`, `get_meme_win_rate`, `get_meme_total_pnl`, `get_meme_best_worst_trades`, `get_meme_portfolio_concentration`, `get_meme_market_stats`, `get_meme_pulse_summary`, `get_meme_risk_status`, `get_meme_signal_detail`, `get_meme_position_detail`, `get_meme_position_pnl`, `get_meme_position_timeout`, `get_meme_trade_detail`, `get_meme_pending_graduations`, `get_meme_graduated_tokens`

### Meme Bot — Tokens (8)
`get_trending_meme_tokens`, `search_meme_tokens`, `get_meme_alerts`, `add_to_whitelist`, `remove_from_whitelist`, `remove_from_blacklist`, `get_blacklist`, `get_whitelist`

### Meme Bot — Risk Levels (2)
`apply_risk_level`, `preview_risk_level`

### Spot Trading — Orders (5)
`spot_market_buy`, `spot_market_sell`, `spot_limit_buy`, `cancel_spot_order`, `close_spot_position`

### Spot Trading — Configuration (6)
`get_spot_config`, `update_spot_config`, `batch_update_spot_config`, `get_spot_config_field`, `validate_spot_config_values`, `get_spot_config_catalog`

### Spot Trading — Risk & DCA (10)
`set_spot_risk_level`, `set_spot_max_exposure`, `set_spot_max_positions`, `set_spot_slippage`, `set_spot_dca_interval`, `set_spot_dca_steps`, `enable_spot_dca`, `enable_spot_rebalancing`, `set_spot_rebalance_threshold`, `set_spot_alert_threshold`

### Spot Trading — Positions & P&L (13)
`get_spot_positions`, `get_spot_position_detail`, `get_spot_position_pnl`, `get_spot_trade_history`, `get_spot_trade_detail`, `get_spot_statistics`, `get_spot_win_rate`, `get_spot_total_pnl`, `get_spot_best_worst_trades`, `get_spot_portfolio_concentration`, `get_spot_trade_pnl_tally`, `reset_spot_pnl_tally`, `clear_spot_trade_history`

### Spot Trading — Markets & Data (8)
`get_spot_markets`, `get_spot_market_detail`, `get_spot_market_stats`, `search_spot_tokens`, `get_trending_spot_tokens`, `get_spot_quote`, `get_spot_swap_transaction`, `refresh_spot_markets`

### Spot Trading — Signals & Bot (11)
`get_spot_signals`, `get_spot_signal_detail`, `clear_spot_signals`, `enable_spot_signals`, `get_spot_risk_status`, `get_spot_risk_levels`, `get_spot_alerts`, `start_spot_bot`, `stop_spot_bot`, `sell_all_spot`, `get_spot_bot_status`

### Spot Trading — Wallet & Logs (8)
`get_spot_wallet_balances`, `get_spot_token_balance`, `transfer_spot_to_savings`, `add_allowed_spot_token`, `remove_allowed_spot_token`, `get_spot_logs`, `clear_spot_logs`

### Perpetual Futures — Positions (7)
`open_perp_long`, `open_perp_short`, `close_perp_position`, `sell_all_perps`, `get_perp_positions`, `get_perp_position_detail`, `get_perp_position_pnl`

### Perpetual Futures — Configuration (8)
`get_perp_config`, `update_perp_config`, `update_perp_config_batch`, `get_perp_config_catalog`, `save_perp_settings`, `validate_perp_config_tool`, `set_perp_auto_execute`, `set_perp_dry_run`

### Perpetual Futures — Leverage & Margin (8)
`set_perp_leverage`, `set_perp_max_leverage`, `set_perp_position_size`, `set_perp_max_exposure`, `set_perp_margin_mode`, `get_perp_margin_info`, `get_perp_margin_ratio`, `get_perp_liquidation_price`

### Perpetual Futures — Risk & Exits (10)
`set_perp_stop_loss`, `set_perp_take_profit_ladder`, `set_perp_trailing_stop`, `set_perp_funding_exit`, `set_perp_liquidation_floor`, `set_perp_position_timeout`, `set_perp_direction`, `set_perp_auto_savings`, `get_perp_exposure`, `get_perp_risk_status`

### Perpetual Futures — Market Filters (6)
`set_perp_market_filters`, `set_perp_allowed_tokens`, `set_perp_blocked_tokens`, `set_perp_signal_mode`, `enable_perp_signal`, `disable_perp_signal`

### Perpetual Futures — Orders (9)
`set_perp_order_type`, `set_perp_slippage`, `set_perp_poll_intervals`, `set_perp_testnet`, `cancel_all_perp_orders`, `cancel_perp_order`, `modify_perp_order`, `get_perp_open_orders`, `get_perp_order_history`

### Perpetual Futures — Markets & Data (8)
`get_perp_markets`, `get_top_perp_markets`, `search_perp_markets`, `get_perp_market_detail`, `get_perp_market_stats`, `get_perp_candles`, `get_perp_orderbook`, `get_perp_price_changes`

### Perpetual Futures — P&L & Analytics (14)
`get_perp_pnl_tally`, `reset_perp_pnl_tally`, `get_perp_trade_history`, `get_perp_trade_detail`, `clear_perp_trade_history`, `get_perp_fee_summary`, `refresh_perp_pnl`, `analyze_perp_performance`, `get_perp_funding_cost`, `get_funding_rates`, `get_funding_history`, `get_liquidations`, `get_perp_correlation_matrix`, `get_perp_var_estimate`

### Perpetual Futures — Signals (5)
`get_perp_signals`, `get_perp_signal_detail`, `get_perp_signal_summary`, `get_perp_signal_history`, `clear_perp_signal_history`

### Perpetual Futures — Bot Control & Wallet (7)
`start_perp_bot`, `stop_perp_bot`, `get_perp_bot_status`, `get_perp_log`, `clear_perp_log`, `get_perp_wallet_balances`, `transfer_perp_sol`

### Perpetual Futures — Risk Levels (2)
`apply_perp_risk_level`, `preview_perp_risk_level`

### Mirror Mode — Whale Management (6)
`add_mirror_whale`, `remove_mirror_whale`, `toggle_mirror_whale`, `get_mirror_whales`, `get_mirror_whale_stats`, `get_all_mirror_whale_stats`

### Mirror Mode — Configuration (9)
`get_mirror_config`, `update_mirror_config_field`, `set_mirror_mode`, `set_mirror_allocation_pct`, `set_mirror_copy_sells`, `set_mirror_dry_run`, `set_mirror_max_trade_usd`, `set_mirror_stop_loss_pct`, `set_mirror_take_profit_pct`

### Mirror Mode — Positions & Bot (6)
`get_mirror_trades`, `clear_mirror_trade_history`, `sell_all_mirror_positions`, `get_mirror_bot_status`, `start_mirror_bot`, `stop_mirror_bot`

### Technical Indicators (8)
`get_all_indicators`, `get_rsi`, `get_macd`, `get_moving_averages`, `get_bollinger_bands`, `get_atr`, `get_volume_analysis`, `get_token_candles`

### Market Data (5)
`get_token_market_data`, `get_token_price`, `get_token_prices`, `get_sol_price`, `get_signal_summary`

---

## Example Conversations with Your AI

> "Start the bot"

→ `start_bot`

> "What are my open positions and what is the current P&L?"

→ `get_open_positions` + `get_positions_status`

> "Buy this mint: 6EF8rBh8gKQj6n5hX2P9Yq3wL4ZmN7vK8xT5fD1sQ2aR"

→ `buy_mint`

> "Open a 3x long on SOL perps with $500"

→ `open_perp_long`

> "Add this whale wallet and start mirror mode"

→ `add_mirror_whale` + `start_mirror_bot`

> "What's my RSI on BONK?"

→ `get_rsi`

> "How much have I paid in fees and ATA rent?"

→ `get_fee_summary`

> "Show me the last 50 log lines"

→ `get_log(50)`

---

## Safety & Risk

This is a live-trading tool. The included filters reduce but do not eliminate risk. Use only funds you can afford to lose. All MCP actions execute immediately with no confirmation unless the client itself asks for one.

---

## License & Support

**Proprietary.** All rights reserved. The Solana Sniper Bot V4 Windows application includes a 7-day free trial (168 hours of actual bot running time). After the trial, a membership is required for live trading: $49.99 for the first month (50% off with code `SOLV4FIRST50`), then $99.99/month. Cancel anytime.

- **Download the app:** [https://solsniperbot.co/download.html](https://solsniperbot.co/download.html)
- **Subscribe:** [https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07](https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07?prefilled_promo_code=SOLV4FIRST50)

---

**MCP Source Repo:** https://github.com/solara-sniper-bot/MCP  
**PyPI:** https://pypi.org/project/solana-snipe-bot-mcp/  
**MCP Registry:** `co.solsniperbot/solana-snipe-bot-mcp`  
**Download App:** https://solsniperbot.co/download.html  
**Subscribe:** https://buy.stripe.com/dRm14ngiB5MBfIK6QM7bW07?prefilled_promo_code=SOLV4FIRST50
