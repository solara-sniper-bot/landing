"""Solana Sniper Bot MCP Server.

Exposes every control, setting, and data view from the Solana Sniper Bot as MCP
tools. The project directory is read from the SOLANA_SNIPER_BOT_DIR environment
variable (default is the current working directory).
"""
import json
import os
import time
from datetime import datetime
from mcp.server.fastmcp import FastMCP

from .config_schema import (
    PROFILE_NAME,
    analyze_trade_history,
    apply_researched_profile,
    build_risk_level_profile,
    config_catalog,
    parse_config_value,
    risk_level_name,
    validate_config,
)
from .position_audit import (
    audit_open_positions as run_position_audit,
    audit_token_account_rent,
    get_exit_quote,
    get_wallet_summary,
)

PROJECT_DIR = os.environ.get("SOLANA_SNIPER_BOT_DIR", os.getcwd())
COMMAND_FILE = os.path.join(PROJECT_DIR, "command_queue.json")

mcp = FastMCP("solana-snipe-bot")


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_json(path, data):
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_path, path)


def _read_env(path):
    entries = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    key, value = stripped.split("=", 1)
                    entries[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return entries


def _set_env_value(path, key, value):
    lines = []
    replaced = False
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        lines = ["# Local secrets. Never commit this file."]
    for index, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[index] = f"{key}={value}"
            replaced = True
            break
    if not replaced:
        lines.append(f"{key}={value}")
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_path, path)


def _rpc_pool_status():
    entries = _read_env(os.path.join(PROJECT_DIR, "secrets.env"))
    slots = []
    configured_count = 0
    for slot in range(1, 6):
        prefix = f"HELIUS_{slot:02d}"
        configured = bool(entries.get(f"{prefix}_KEY", "").strip())
        configured_count += int(configured)
        slots.append({
            "slot": slot,
            "label": f"Helius {slot:02d}",
            "configured": configured,
            "skip_until": entries.get(f"{prefix}_SKIP_UNTIL") or None,
        })
    return {"configured_count": configured_count, "minimum_required": 1, "slots": slots}


def _enqueue_command(cmd: str, **params):
    """Write a command to the command queue file. The running bot polls this."""
    queue = _read_json(COMMAND_FILE) or []
    queue.append({
        "cmd": cmd,
        "params": params,
        "timestamp": time.time(),
    })
    queue = queue[-50:]
    _write_json(COMMAND_FILE, queue)


def _pulse_purchase_context(mint: str) -> dict:
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json")) or {}
    asset = next((row for row in (_read_json(os.path.join(PROJECT_DIR, "pulse_data.json")) or [])
                  if row.get("mint") == mint), {})
    status = _read_json(os.path.join(PROJECT_DIR, "positions_status.json")) or {}
    sol_price = float(status.get("sol_price", 0) or status.get("sol_price_usd", 0) or 0)
    if cfg.get("dry_run", True) and float(cfg.get("simulated_balance_sol", 0) or 0) > 0:
        balance_sol = float(cfg["simulated_balance_sol"])
        reserve_sol = 0.0
    else:
        wallet = get_wallet_summary(PROJECT_DIR).get("trading_wallet", {})
        balance_sol = float(wallet.get("sol", 0) or 0)
        reserve_sol = float(cfg.get("min_wallet_reserve_sol", 0) or 0)
        if sol_price <= 0 and balance_sol > 0:
            sol_price = float(wallet.get("usd", 0) or 0) / balance_sol
    available_sol = max(0.0, balance_sol - reserve_sol)
    return {
        "asset": asset,
        "mint": mint,
        "dry_run": bool(cfg.get("dry_run", True)),
        "balance_sol": balance_sol,
        "reserved_sol": reserve_sol,
        "available_sol": available_sol,
        "sol_price_usd": sol_price,
        "available_usd": available_sol * sol_price,
    }


@mcp.tool()
def start_bot() -> str:
    """Start the snipe bot (equivalent to clicking 'Start Bot' in the GUI)."""
    _enqueue_command("start_bot")
    return "Command queued: start_bot. The bot will start if not already running."


@mcp.tool()
def stop_bot() -> str:
    """Stop the snipe bot (equivalent to clicking 'Stop Bot' in the GUI)."""
    _enqueue_command("stop_bot")
    return "Command queued: stop_bot. The bot will stop gracefully."


@mcp.tool()
def set_trading_mode(mode: str) -> str:
    """Switch between practice and live trading, matching the GUI mode button."""
    normalized = mode.strip().lower()
    if normalized not in {"practice", "live"}:
        return "Mode not changed: mode must be practice or live."
    cfg_path = os.path.join(PROJECT_DIR, "config.json")
    cfg = _read_json(cfg_path) or {}
    cfg["dry_run"] = normalized == "practice"
    _write_json(cfg_path, cfg)
    _enqueue_command("set_trading_mode", dry_run=cfg["dry_run"])
    return json.dumps({"updated": True, "mode": normalized, "dry_run": cfg["dry_run"]}, indent=2)


@mcp.tool()
def sell_all() -> str:
    """Panic sell — liquidate ALL open positions immediately."""
    _enqueue_command("sell_all")
    return "Command queued: sell_all. All open positions will be liquidated."


@mcp.tool()
def sell_position(mint: str) -> str:
    """Sell a single position by mint address immediately."""
    _enqueue_command("sell_position", mint=mint)
    return f"Command queued: sell_position for {mint[:12]}..."


@mcp.tool()
def buy_mint(mint: str) -> str:
    """Buy a specific token by mint address using configured automatic sizing."""
    _enqueue_command("buy_mint", mint=mint)
    return f"Command queued: buy_mint for {mint[:12]}..."


@mcp.tool()
def get_pulse_purchase_preview(mint: str) -> str:
    """Return the Pulse asset data and SOL/USD funds available for a purchase."""
    return json.dumps(_pulse_purchase_context(mint), indent=2)


@mcp.tool()
def buy_pulse_asset(mint: str, amount: float, amount_type: str = "sol") -> str:
    """Purchase a Pulse asset by SOL quantity, USD value, or available-funds percentage.

    amount_type must be sol, usd, or percentage. This queues the purchase immediately
    without another confirmation, matching the Pulse-tab purchase dialog.
    """
    context = _pulse_purchase_context(mint)
    kind = amount_type.strip().lower()
    value = float(amount)
    if value <= 0:
        return "Purchase not queued: amount must be greater than zero."
    if kind == "sol":
        buy_sol = value
    elif kind == "usd":
        if context["sol_price_usd"] <= 0:
            return "Purchase not queued: SOL/USD price is unavailable."
        buy_sol = value / context["sol_price_usd"]
    elif kind in {"percentage", "percent", "pct"}:
        if value > 100:
            return "Purchase not queued: percentage must be between 0 and 100."
        buy_sol = context["available_sol"] * value / 100
    else:
        return "Purchase not queued: amount_type must be sol, usd, or percentage."
    if buy_sol > context["available_sol"]:
        return "Purchase not queued: requested amount exceeds available funds."
    buy_lamports = int(buy_sol * 1e9)
    if buy_lamports <= 0:
        return "Purchase not queued: calculated purchase amount is below one lamport."
    _enqueue_command("buy_mint", mint=mint, buy_lamports=buy_lamports)
    return json.dumps({
        "queued": True,
        "mint": mint,
        "buy_sol": buy_lamports / 1e9,
        "buy_usd": (buy_lamports / 1e9) * context["sol_price_usd"],
        "amount_type": kind,
        "dry_run": context["dry_run"],
    }, indent=2)


@mcp.tool()
def get_config() -> str:
    """Get the current bot configuration as JSON."""
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json"))
    if cfg is None:
        return "No config file found."
    return json.dumps(cfg, indent=2)


@mcp.tool()
def get_rpc_pool_status() -> str:
    """List configured RPC pool slots without exposing API key values."""
    return json.dumps(_rpc_pool_status(), indent=2)


@mcp.tool()
def set_rpc_pool_key(slot: int, api_key: str) -> str:
    """Set one Helius RPC pool key in the private local secrets.env file."""
    if slot < 1 or slot > 5:
        return "RPC pool key not changed: slot must be between 1 and 5."
    if not api_key.strip():
        return "RPC pool key not changed: api_key cannot be empty."
    key = f"HELIUS_{slot:02d}_KEY"
    _set_env_value(os.path.join(PROJECT_DIR, "secrets.env"), key, api_key.strip())
    return json.dumps({
        "updated": True,
        "slot": slot,
        "label": f"Helius {slot:02d}",
        "configured": True,
        "restart_required": True,
    }, indent=2)


@mcp.tool()
def set_rpc_pool_skip_until(slot: int, skip_date: str) -> str:
    """Set or clear the skip-until date for an RPC pool slot.

    Pass an empty string to clear the skip date and re-activate the slot.
    The slot will be omitted from the round-robin pool until the specified
    date (YYYY-MM-DD), then automatically rejoin.
    """
    if slot < 1 or slot > 5:
        return "Skip date not changed: slot must be between 1 and 5."
    key = f"HELIUS_{slot:02d}_SKIP_UNTIL"
    if skip_date.strip():
        try:
            datetime.strptime(skip_date.strip(), "%Y-%m-%d")
        except ValueError:
            return "Skip date not changed: must be YYYY-MM-DD format."
        _set_env_value(os.path.join(PROJECT_DIR, "secrets.env"), key, skip_date.strip())
    else:
        # Clear by setting empty value (load_rpc_pool treats missing/empty as no skip)
        _set_env_value(os.path.join(PROJECT_DIR, "secrets.env"), key, "")
    return json.dumps({
        "updated": True,
        "slot": slot,
        "label": f"Helius {slot:02d}",
        "skip_until": skip_date.strip() or None,
        "restart_required": True,
    }, indent=2)


@mcp.tool()
def update_config(key: str, value: str) -> str:
    """Update a single config key. The bot must be restarted for some settings."""
    cfg_path = os.path.join(PROJECT_DIR, "config.json")
    cfg = _read_json(cfg_path) or {}
    try:
        parsed = parse_config_value(key, value)
    except (TypeError, ValueError) as exc:
        return f"Config not changed: {exc}"
    cfg[key] = parsed
    validation = validate_config(cfg)
    if validation["errors"]:
        return "Config not changed: " + "; ".join(validation["errors"])
    _write_json(cfg_path, cfg)
    return f"Config updated: {key} = {cfg.get(key)}"


@mcp.tool()
def get_config_catalog() -> str:
    """List every supported variable, type, range, description, and value."""
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json")) or {}
    return json.dumps(config_catalog(cfg), indent=2)


@mcp.tool()
def validate_current_config() -> str:
    """Validate all current settings and return errors and risk warnings."""
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json")) or {}
    return json.dumps(validate_config(cfg), indent=2)


@mcp.tool()
def preview_strategy_profile(live_trading: bool = False) -> str:
    """Preview the guarded small-account profile without changing files."""
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json")) or {}
    proposed = apply_researched_profile(cfg, live_trading=live_trading)
    changes = {
        key: {"current": cfg.get(key), "proposed": value}
        for key, value in proposed.items() if cfg.get(key) != value
    }
    return json.dumps({
        "profile": PROFILE_NAME,
        "live_trading": live_trading,
        "change_count": len(changes),
        "changes": changes,
        "validation": validate_config(proposed),
    }, indent=2)


@mcp.tool()
def apply_strategy_profile(confirm: bool = False,
                           live_trading: bool = False) -> str:
    """Apply the guarded profile atomically; requires confirm=true."""
    if not confirm:
        return "No change made. Call again with confirm=true after previewing the profile."
    cfg_path = os.path.join(PROJECT_DIR, "config.json")
    cfg = _read_json(cfg_path) or {}
    proposed = apply_researched_profile(cfg, live_trading=live_trading)
    _write_json(cfg_path, proposed)
    return json.dumps({
        "applied": True,
        "profile": PROFILE_NAME,
        "live_trading": live_trading,
        "dry_run": proposed["dry_run"],
        "validation": validate_config(proposed),
    }, indent=2)


@mcp.tool()
def preview_risk_level(level: int) -> str:
    """Preview one of the 20 unified risk levels without changing files."""
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json")) or {}
    try:
        proposed = build_risk_level_profile(cfg, level)
    except (TypeError, ValueError) as exc:
        return f"Risk profile not previewed: {exc}"
    changes = {
        key: {"current": cfg.get(key), "proposed": value}
        for key, value in proposed.items() if cfg.get(key) != value
    }
    return json.dumps({
        "risk_level": int(level),
        "name": risk_level_name(int(level)),
        "change_count": len(changes),
        "changes": changes,
        "validation": validate_config(proposed),
    }, indent=2)


@mcp.tool()
def apply_risk_level(level: int, confirm: bool = False) -> str:
    """Atomically apply a 1-20 unified risk level; requires confirm=true."""
    if not confirm:
        return "No change made. Preview the level, then call again with confirm=true."
    cfg_path = os.path.join(PROJECT_DIR, "config.json")
    cfg = _read_json(cfg_path) or {}
    try:
        proposed = build_risk_level_profile(cfg, level)
    except (TypeError, ValueError) as exc:
        return f"Risk profile not applied: {exc}"
    _write_json(cfg_path, proposed)
    return json.dumps({
        "applied": True,
        "risk_level": int(level),
        "name": risk_level_name(int(level)),
        "validation": validate_config(proposed),
    }, indent=2)


@mcp.tool()
def update_config_batch(settings_json: str, confirm: bool = False) -> str:
    """Validate and atomically update multiple settings from a JSON object."""
    if not confirm:
        return "No change made. Call again with confirm=true."
    try:
        updates = json.loads(settings_json)
        if not isinstance(updates, dict):
            raise ValueError("settings_json must contain a JSON object")
        parsed = {key: parse_config_value(key, value) for key, value in updates.items()}
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return f"Config not changed: {exc}"
    cfg_path = os.path.join(PROJECT_DIR, "config.json")
    cfg = _read_json(cfg_path) or {}
    proposed = dict(cfg)
    proposed.update(parsed)
    validation = validate_config(proposed)
    if validation["errors"]:
        return "Config not changed: " + "; ".join(validation["errors"])
    _write_json(cfg_path, proposed)
    return json.dumps({"updated": parsed, "validation": validation}, indent=2)


@mcp.tool()
def analyze_trade_performance() -> str:
    """Analyze closed-trade performance and exit-reason distribution."""
    trades = _read_json(os.path.join(PROJECT_DIR, "trade_history.json")) or []
    return json.dumps(analyze_trade_history(trades), indent=2)


@mcp.tool()
def audit_open_positions() -> str:
    """Compare saved positions to wallet balances and live exit routes (read-only)."""
    try:
        return json.dumps(run_position_audit(PROJECT_DIR), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc), "read_only": True}, indent=2)


@mcp.tool()
def get_position_exit_quote(mint: str = "") -> str:
    """Get a read-only Jupiter exit quote for a persisted open position."""
    positions = _read_json(os.path.join(PROJECT_DIR, "open_positions.json")) or []
    active = [position for position in positions if int(position.get("token_amount", 0)) > 0]
    if not mint and len(active) == 1:
        mint = active[0].get("mint", "")
    position = next((item for item in active if item.get("mint") == mint), None)
    if not position:
        return json.dumps({"error": "Open position not found", "mint": mint}, indent=2)
    cfg = _read_json(os.path.join(PROJECT_DIR, "config.json")) or {}
    try:
        result = get_exit_quote(
            mint, int(position["token_amount"]), int(cfg.get("slippage_bps", 250)))
        result["mint"] = mint
        return json.dumps(result, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc), "mint": mint, "read_only": True}, indent=2)


@mcp.tool()
def save_settings() -> str:
    """Save current settings to config.json."""
    _enqueue_command("save_settings")
    return "Command queued: save_settings."


@mcp.tool()
def get_open_positions() -> str:
    """Get all currently open (unsold) positions as JSON."""
    positions = _read_json(os.path.join(PROJECT_DIR, "open_positions.json"))
    if positions is None:
        return "No open positions file found."
    return json.dumps(positions, indent=2)


@mcp.tool()
def get_positions_status() -> str:
    """Get real-time position status (P&L, portfolio value, SOL price)."""
    status = _read_json(os.path.join(PROJECT_DIR, "positions_status.json"))
    if status is None:
        return "No positions status file found. Bot may not be running."
    return json.dumps(status, indent=2)


@mcp.tool()
def get_graduation_status(mint: str = "") -> str:
    """Check graduation status for all open positions or a specific mint."""
    positions = _read_json(os.path.join(PROJECT_DIR, "open_positions.json")) or []
    if not positions:
        return "No open positions."
    results = []
    for pos in positions:
        if mint and pos.get("mint", "") != mint:
            continue
        results.append({
            "mint": pos.get("mint", ""),
            "name": pos.get("name", ""),
            "symbol": pos.get("symbol", ""),
            "bonding_curve": pos.get("bonding_curve", False),
            "graduated": pos.get("graduated", False),
            "graduation_time": pos.get("graduation_time", 0),
            "token_amount": pos.get("token_amount", 0),
            "buy_sol_amount": pos.get("buy_sol_amount", 0),
        })
    return json.dumps({"positions": results}, indent=2)


@mcp.tool()
def get_bot_status() -> str:
    """Get overall bot status."""
    status = _read_json(os.path.join(PROJECT_DIR, "positions_status.json")) or {}
    positions = _read_json(os.path.join(PROJECT_DIR, "open_positions.json")) or []
    summary = {
        "open_positions": len(positions),
        "sol_price_usd": status.get("sol_price_usd", 0),
        "total_invested_sol": status.get("total_invested_sol", 0),
        "total_current_sol": status.get("total_current_sol", 0),
        "total_pnl_sol": status.get("total_pnl_sol", 0),
        "total_pnl_usd": status.get("total_pnl_usd", 0),
        "active_count": status.get("active_count", 0),
        "wallet_balance_sol": status.get("wallet_balance_sol", 0),
    }
    return json.dumps(summary, indent=2)


@mcp.tool()
def get_trade_history(limit: int = 20) -> str:
    """Get recent trade history records."""
    history = _read_json(os.path.join(PROJECT_DIR, "trade_history.json")) or []
    return json.dumps(history[-limit:], indent=2)


@mcp.tool()
def clear_trade_history() -> str:
    """Clear all trade history."""
    _write_json(os.path.join(PROJECT_DIR, "trade_history.json"), [])
    return "Trade history cleared."


@mcp.tool()
def get_pnl_tally() -> str:
    """Get the persistent all-time P&L tally."""
    tally = _read_json(os.path.join(PROJECT_DIR, "pnl_tally.json"))
    if tally is None:
        return "No P&L tally file found."
    return json.dumps(tally, indent=2)


@mcp.tool()
def reset_pnl_tally() -> str:
    """Reset the all-time P&L tally to zero."""
    _enqueue_command("reset_pnl_tally")
    return "Command queued: reset_pnl_tally."


@mcp.tool()
def get_wallet_balances() -> str:
    """Get trading and savings wallet balances."""
    try:
        return json.dumps(get_wallet_summary(PROJECT_DIR), indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc), "read_only": True}, indent=2)


@mcp.tool()
def transfer_sol(direction: str, amount_sol: float) -> str:
    """Transfer SOL between trading and savings wallets."""
    if direction not in ("to_savings", "to_trading"):
        return "Invalid direction."
    _enqueue_command("transfer", direction=direction, amount_sol=amount_sol)
    return f"Command queued: transfer {amount_sol} SOL {direction}."


@mcp.tool()
def move_all_sol(direction: str) -> str:
    """Move ALL SOL from one wallet to the other."""
    if direction not in ("to_savings", "to_trading"):
        return "Invalid direction."
    _enqueue_command("transfer_all", direction=direction)
    return f"Command queued: move ALL SOL {direction}."


@mcp.tool()
def get_pulse_results() -> str:
    """Get all Pulse tab results."""
    results = _read_json(os.path.join(PROJECT_DIR, "pulse_data.json"))
    if results is None:
        return "No pulse data found."
    return json.dumps(results, indent=2)


@mcp.tool()
def set_pulse_match_mode(mode: str) -> str:
    """Set the Pulse match mode."""
    if mode not in ("exact", "word", "fuzzy"):
        return "Invalid mode."
    _enqueue_command("set_pulse_mode", mode=mode)
    return f"Command queued: set pulse match mode to {mode}."


@mcp.tool()
def clear_pulse_results() -> str:
    """Clear all Pulse results."""
    _write_json(os.path.join(PROJECT_DIR, "pulse_data.json"), [])
    return "Pulse results cleared."


@mcp.tool()
def get_log(tail_lines: int = 50) -> str:
    """Get the last N lines of the bot log."""
    log_path = os.path.join(PROJECT_DIR, "snipe_bot.log")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-tail_lines:])
    except FileNotFoundError:
        return "No log file found."


@mcp.tool()
def clear_log() -> str:
    """Clear the bot log file."""
    log_path = os.path.join(PROJECT_DIR, "snipe_bot.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("")
    _enqueue_command("clear_log")
    return "Log cleared."


@mcp.tool()
def get_pending_commands() -> str:
    """Get pending commands from the command queue."""
    queue = _read_json(COMMAND_FILE)
    if queue is None:
        return "No command queue file."
    return json.dumps(queue, indent=2)


@mcp.tool()
def clear_commands() -> str:
    """Clear the command queue."""
    _write_json(COMMAND_FILE, [])
    return "Command queue cleared."


@mcp.tool()
def get_fee_summary() -> str:
    """Get fee + ATA rent breakdown."""
    tally = _read_json(os.path.join(PROJECT_DIR, "pnl_tally.json")) or {}
    summary = {
        "total_fees_paid_sol": tally.get("total_fees_paid_sol", 0),
        "total_fees_paid_usd": tally.get("total_fees_paid_usd", 0),
    }
    try:
        summary.update(audit_token_account_rent(PROJECT_DIR))
    except Exception as exc:
        summary["rent_audit_error"] = str(exc)
    return json.dumps(summary, indent=2)


@mcp.tool()
def close_empty_token_accounts() -> str:
    """Close all empty token accounts to reclaim ATA rent."""
    _enqueue_command("close_empty_token_accounts")
    return "Command queued: close_empty_token_accounts."


@mcp.tool()
def refresh_pnl() -> str:
    """Force a P&L recompute."""
    _enqueue_command("refresh_pnl")
    return "Command queued: refresh_pnl."


@mcp.tool()
def close_position(mint: str) -> str:
    """Manually close a position without executing an on-chain sell."""
    if not mint:
        return "Error: mint required."
    positions_path = os.path.join(PROJECT_DIR, "open_positions.json")
    positions = _read_json(positions_path) or []
    for pos in positions:
        if pos.get("mint", "") == mint:
            pos["sold"] = True
            pos["manual_review"] = True
            _write_json(positions_path, positions)
            return f"Position {mint[:12]}... closed manually."
    return f"Error: Position {mint} not found."


@mcp.tool()
def get_pulse_price_history(mint: str) -> str:
    """Get price tracking for a specific mint."""
    if not mint:
        return "Error: mint required."
    results = _read_json(os.path.join(PROJECT_DIR, "pulse_data.json")) or []
    for r in results:
        if r.get("mint", "") == mint:
            return json.dumps({
                "mint": mint,
                "name": r.get("name", ""),
                "symbol": r.get("symbol", ""),
                "price_at_match_sol": r.get("price_at_match_sol", 0),
                "price_at_match_usd": r.get("price_at_match_usd", 0),
                "current_price_sol": r.get("current_price_sol", 0),
                "current_price_usd": r.get("current_price_usd", 0),
                "price_change_pct": r.get("price_change_pct", 0),
                "price_history": r.get("price_history", []),
                "last_price_update": r.get("last_price_update", 0),
            }, indent=2)
    return f"Mint {mint} not found in pulse data."


@mcp.tool()
def get_bot_stats() -> str:
    """Get bot operational statistics and per-category rejection totals."""
    log_path = os.path.join(PROJECT_DIR, "snipe_bot.log")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return "No log file found."
    stats_line = ""
    stats_index = -1
    for index, line in enumerate(lines):
        if "Stats" in line and "=" in line:
            stats_line = line.strip()
            stats_index = index
    if not stats_line:
        return "No stats found."
    stats = {}
    for part in stats_line.split():
        if "=" in part:
            key, val = part.split("=", 1)
            try:
                stats[key] = int(val)
            except ValueError:
                stats[key] = val
    rejection_reasons = {}
    for line in lines[stats_index + 1:]:
        if "Stats" in line and "=" in line:
            break
        marker = "Rejections by reason:"
        if marker not in line:
            continue
        for part in line.split(marker, 1)[1].split():
            if "=" not in part:
                continue
            key, val = part.split("=", 1)
            try:
                rejection_reasons[key] = int(val)
            except ValueError:
                continue
    stats["rejection_reasons"] = rejection_reasons
    return json.dumps(stats, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
