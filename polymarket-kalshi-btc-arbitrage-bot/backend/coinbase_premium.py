"""
Coinbase Premium Indicator

This module tracks the price difference between Coinbase BTCUSD and Binance BTCUSDT,
adjusted for the USD/USDT exchange rate.

Premium = Coinbase_BTCUSD - (Binance_BTCUSDT * USD_USDT_Rate)

A positive premium indicates Coinbase is trading at a higher price (bullish signal for US demand).
A negative premium indicates Coinbase is trading at a lower price (bearish signal).
"""

import requests
import time
from datetime import datetime
from typing import Optional, Dict, Tuple, Any

# API Endpoints
COINBASE_API_URL = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_TICKER_24H_URL = "https://api.binance.com/api/v3/ticker/24hr"

# Request timeout
REQUEST_TIMEOUT = 10


def get_coinbase_btcusd() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetches the current BTC/USD spot price from Coinbase.

    Returns:
        Tuple of (price, error_message)
    """
    try:
        response = requests.get(COINBASE_API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        price = float(data["data"]["amount"])
        return price, None
    except requests.exceptions.RequestException as e:
        return None, f"Coinbase API error: {str(e)}"
    except (KeyError, ValueError) as e:
        return None, f"Coinbase data parsing error: {str(e)}"


def get_binance_btcusdt() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetches the current BTC/USDT price from Binance.

    Returns:
        Tuple of (price, error_message)
    """
    try:
        response = requests.get(
            BINANCE_PRICE_URL,
            params={"symbol": "BTCUSDT"},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        price = float(data["price"])
        return price, None
    except requests.exceptions.RequestException as e:
        return None, f"Binance BTCUSDT API error: {str(e)}"
    except (KeyError, ValueError) as e:
        return None, f"Binance BTCUSDT data parsing error: {str(e)}"


def get_usd_usdt_rate() -> Tuple[Optional[float], Optional[str]]:
    """
    Estimates the USD/USDT exchange rate using USDC/USDT pair.
    USDC is a USD-backed stablecoin, so USDC/USDT ≈ USD/USDT.

    A rate > 1.0 means USDT is trading at a discount to USD.
    A rate < 1.0 means USDT is trading at a premium to USD.

    Returns:
        Tuple of (rate, error_message)
    """
    try:
        response = requests.get(
            BINANCE_PRICE_URL,
            params={"symbol": "USDCUSDT"},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        # USDCUSDT gives us how many USDT per 1 USDC
        # Since USDC ≈ USD, this is approximately USD/USDT
        rate = float(data["price"])
        return rate, None
    except requests.exceptions.RequestException as e:
        return None, f"Binance USDCUSDT API error: {str(e)}"
    except (KeyError, ValueError) as e:
        return None, f"Binance USDCUSDT data parsing error: {str(e)}"


def calculate_premium(
    coinbase_price: float,
    binance_price: float,
    usd_usdt_rate: float
) -> Dict[str, float]:
    """
    Calculates the Coinbase premium metrics.

    Args:
        coinbase_price: Coinbase BTCUSD price
        binance_price: Binance BTCUSDT price
        usd_usdt_rate: USD/USDT exchange rate

    Returns:
        Dictionary with premium metrics
    """
    # Adjust Binance price to USD terms
    binance_price_usd = binance_price * usd_usdt_rate

    # Calculate absolute premium (in USD)
    premium_absolute = coinbase_price - binance_price_usd

    # Calculate percentage premium
    premium_percentage = (premium_absolute / binance_price_usd) * 100

    return {
        "premium_absolute": round(premium_absolute, 2),
        "premium_percentage": round(premium_percentage, 4),
        "binance_price_usd_adjusted": round(binance_price_usd, 2)
    }


def fetch_coinbase_premium() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetches all data and calculates the Coinbase premium.

    Returns:
        Tuple of (premium_data, error_message)
    """
    errors = []

    # Fetch all prices
    coinbase_price, cb_err = get_coinbase_btcusd()
    binance_price, bn_err = get_binance_btcusdt()
    usd_usdt_rate, rate_err = get_usd_usdt_rate()

    if cb_err:
        errors.append(cb_err)
    if bn_err:
        errors.append(bn_err)
    if rate_err:
        errors.append(rate_err)

    # If any critical data is missing, return error
    if coinbase_price is None or binance_price is None:
        return None, "; ".join(errors) if errors else "Failed to fetch prices"

    # Default USD/USDT rate to 1.0 if unavailable (assume parity)
    if usd_usdt_rate is None:
        usd_usdt_rate = 1.0
        errors.append("USD/USDT rate unavailable, using 1.0")

    # Calculate premium
    premium_metrics = calculate_premium(coinbase_price, binance_price, usd_usdt_rate)

    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "coinbase_btcusd": round(coinbase_price, 2),
        "binance_btcusdt": round(binance_price, 2),
        "usd_usdt_rate": round(usd_usdt_rate, 6),
        "binance_btcusd_adjusted": premium_metrics["binance_price_usd_adjusted"],
        "premium_usd": premium_metrics["premium_absolute"],
        "premium_percent": premium_metrics["premium_percentage"],
        "signal": _interpret_premium(premium_metrics["premium_percentage"]),
        "warnings": errors if errors else None
    }

    return result, None


def _interpret_premium(premium_pct: float) -> str:
    """
    Interprets the premium percentage into a market signal.

    Args:
        premium_pct: Premium as a percentage

    Returns:
        Signal interpretation string
    """
    if premium_pct > 0.5:
        return "Strong US Demand (Bullish)"
    elif premium_pct > 0.1:
        return "Moderate US Demand"
    elif premium_pct > -0.1:
        return "Neutral"
    elif premium_pct > -0.5:
        return "Moderate Selling Pressure"
    else:
        return "Strong Selling Pressure (Bearish)"


def fetch_premium_history(intervals: int = 60, delay: float = 1.0) -> list:
    """
    Collects premium data over time for analysis.

    Args:
        intervals: Number of data points to collect
        delay: Seconds between each fetch

    Returns:
        List of premium data points
    """
    history = []

    for i in range(intervals):
        data, err = fetch_coinbase_premium()
        if data:
            history.append(data)

        if i < intervals - 1:
            time.sleep(delay)

    return history


def main():
    """CLI interface for the Coinbase Premium indicator."""
    print("=" * 60)
    print("COINBASE PREMIUM INDICATOR")
    print("Tracking: Coinbase BTCUSD vs Binance BTCUSDT (USD adjusted)")
    print("=" * 60)
    print()

    data, err = fetch_coinbase_premium()

    if err:
        print(f"Error: {err}")
        return

    print(f"Timestamp: {data['timestamp']}")
    print("-" * 60)
    print(f"Coinbase BTC/USD:       ${data['coinbase_btcusd']:,.2f}")
    print(f"Binance BTC/USDT:       ${data['binance_btcusdt']:,.2f}")
    print(f"USD/USDT Rate:          {data['usd_usdt_rate']:.6f}")
    print(f"Binance Adjusted (USD): ${data['binance_btcusd_adjusted']:,.2f}")
    print("-" * 60)
    print(f"PREMIUM (USD):          ${data['premium_usd']:+,.2f}")
    print(f"PREMIUM (%):            {data['premium_percent']:+.4f}%")
    print(f"SIGNAL:                 {data['signal']}")

    if data.get('warnings'):
        print("-" * 60)
        print("Warnings:")
        for w in data['warnings']:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
