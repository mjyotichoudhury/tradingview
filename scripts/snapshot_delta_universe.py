#!/usr/bin/env python3
"""Build a compact, reviewable Delta Exchange India crypto-perpetual universe."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request


PRODUCTS_URL = "https://api.india.delta.exchange/v2/products"
NON_CRYPTO_MARKERS = ("bstocks token", "xstock token")
TOKENIZED_COMMODITIES = {"PAXGUSD", "SLVONUSD", "XAUTUSD"}
RECOMMENDED_CORE = {
    "AAVEUSD",
    "ADAUSD",
    "APTUSD",
    "AVAXUSD",
    "BCHUSD",
    "BNBUSD",
    "BTCUSD",
    "DOGEUSD",
    "DOTUSD",
    "ETHUSD",
    "HYPEUSD",
    "LINKUSD",
    "LTCUSD",
    "NEARUSD",
    "POLUSD",
    "SOLUSD",
    "SUIUSD",
    "TRXUSD",
    "UNIUSD",
    "XRPUSD",
}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def exclusion_reason(product: dict[str, object]) -> str | None:
    symbol = str(product.get("symbol", ""))
    description = str(product.get("description", "")).lower()
    if any(marker in description for marker in NON_CRYPTO_MARKERS):
        return "tokenized stock or index"
    if symbol in TOKENIZED_COMMODITIES:
        return "gold/silver-linked token"
    return None


def compact(product: dict[str, object], as_of: datetime) -> dict[str, object]:
    launched = parse_time(str(product["launch_time"]))
    ui_config = product.get("ui_config") or {}
    underlying = product.get("underlying_asset") or {}
    age_days = max(0, (as_of - launched).days)
    return {
        "symbol": product["symbol"],
        "underlying": underlying.get("symbol"),
        "name": underlying.get("name"),
        "launch_time": product["launch_time"],
        "age_days": age_days,
        "contract_value": product.get("contract_value"),
        "tick_size": product.get("tick_size"),
        "exchange_tags": ui_config.get("tags", []),
    }


def build_snapshot(payload: dict[str, object], as_of: datetime) -> dict[str, object]:
    products = payload.get("result")
    if not isinstance(products, list):
        raise ValueError("Delta response does not contain a product list")

    live_perpetuals = [
        product
        for product in products
        if product.get("contract_type") == "perpetual_futures"
        and product.get("state") == "live"
        and product.get("launch_time")
    ]
    excluded = []
    crypto = []
    for product in live_perpetuals:
        reason = exclusion_reason(product)
        if reason:
            excluded.append({"symbol": product["symbol"], "reason": reason})
        else:
            crypto.append(compact(product, as_of))

    crypto.sort(key=lambda item: (str(item["launch_time"]), str(item["symbol"])), reverse=True)
    core = [item for item in crypto if item["symbol"] in RECOMMENDED_CORE]
    probation = [item for item in crypto if int(item["age_days"]) < 365]
    established = [
        item
        for item in crypto
        if int(item["age_days"]) >= 365 and item["symbol"] not in RECOMMENDED_CORE
    ]
    recent = [item for item in crypto if int(item["age_days"]) <= 90]

    return {
        "source": PRODUCTS_URL,
        "as_of": as_of.date().isoformat(),
        "policy": {
            "instrument": "live perpetual_futures",
            "probation": "less than 365 days since Delta launch",
            "recent": "90 days or less since Delta launch",
            "excluded": "tokenized stocks, indices, and gold/silver-linked tokens",
        },
        "counts": {
            "catalogue_products": len(products),
            "live_perpetuals": len(live_perpetuals),
            "crypto_perpetuals": len(crypto),
            "recommended_core": len(core),
            "established_research": len(established),
            "probation": len(probation),
            "recent": len(recent),
            "excluded_non_crypto": len(excluded),
        },
        "recommended_core": sorted(core, key=lambda item: str(item["symbol"])),
        "recent_listings": recent,
        "probation": probation,
        "established_research": sorted(established, key=lambda item: str(item["symbol"])),
        "excluded_non_crypto": sorted(excluded, key=lambda item: str(item["symbol"])),
    }


def load_payload(source: Path | None) -> dict[str, object]:
    if source:
        return json.loads(source.read_text(encoding="utf-8"))
    request = urllib.request.Request(PRODUCTS_URL, headers={"User-Agent": "tradingview-research/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="Use a saved products response instead of the API")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--as-of", type=str, help="UTC snapshot date (YYYY-MM-DD)")
    args = parser.parse_args()

    as_of = (
        datetime.strptime(args.as_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if args.as_of
        else datetime.now(timezone.utc)
    )
    snapshot = build_snapshot(load_payload(args.source), as_of)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {snapshot['counts']['crypto_perpetuals']} crypto perpetuals to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
