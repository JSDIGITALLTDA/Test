"""
Liquidity Analysis Module

Before executing an arbitrage trade, you MUST check if there's enough liquidity
at the current price. Otherwise, slippage will eat your profits.

Example:
- You find an arb opportunity: Buy 1000 contracts at $0.48 + $0.50 = $0.98
- But the order book only has 10 contracts available at $0.48
- The next 990 contracts are priced at $0.52
- Your actual average cost becomes $0.52 + $0.50 = $1.02 (LOSS!)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import requests


@dataclass
class OrderBookLevel:
    """Single level in the order book"""
    price: float
    size: int  # Number of contracts


@dataclass
class LiquidityAnalysis:
    """Result of liquidity check"""
    total_available: int  # Total contracts available
    average_price: float  # Volume-weighted average price
    slippage: float  # How much worse than best price
    is_sufficient: bool  # Whether there's enough liquidity
    levels: List[OrderBookLevel]  # Individual price levels


class LiquidityAnalyzer:
    """
    Analyzes order book depth to prevent slippage losses
    """

    def __init__(self, min_contracts: int = 100, max_slippage: float = 0.005):
        """
        Args:
            min_contracts: Minimum contracts needed for trade
            max_slippage: Maximum acceptable slippage (0.005 = 0.5 cents)
        """
        self.min_contracts = min_contracts
        self.max_slippage = max_slippage

    def analyze_polymarket_liquidity(
        self,
        token_id: str,
        side: str,  # "buy" or "sell"
        desired_size: int
    ) -> LiquidityAnalysis:
        """
        Check liquidity on Polymarket's order book

        Args:
            token_id: Polymarket token ID
            side: "buy" (get asks) or "sell" (get bids)
            desired_size: How many contracts we want to trade

        Returns:
            LiquidityAnalysis with depth information
        """
        try:
            # Fetch order book from Polymarket CLOB API
            url = f"https://clob.polymarket.com/book?token_id={token_id}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            order_book = response.json()

            # Get asks (for buying) or bids (for selling)
            orders = order_book.get('asks' if side == 'buy' else 'bids', [])

            return self._calculate_liquidity(orders, desired_size, 'polymarket')

        except Exception as e:
            print(f"Error fetching Polymarket liquidity: {e}")
            # Return pessimistic analysis
            return LiquidityAnalysis(
                total_available=0,
                average_price=999.0,
                slippage=999.0,
                is_sufficient=False,
                levels=[]
            )

    def analyze_kalshi_liquidity(
        self,
        ticker: str,
        side: str,  # "yes" or "no"
        desired_size: int
    ) -> LiquidityAnalysis:
        """
        Check liquidity on Kalshi's order book

        Args:
            ticker: Kalshi market ticker
            side: "yes" or "no"
            desired_size: How many contracts we want to trade

        Returns:
            LiquidityAnalysis with depth information
        """
        try:
            # Fetch order book from Kalshi API
            url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}/orderbook"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            order_book = response.json()

            # Kalshi has separate yes/no order books
            if side.lower() == 'yes':
                # To buy yes, we look at yes asks
                orders = order_book.get('yes', {}).get('asks', [])
            else:
                # To buy no, we look at no asks
                orders = order_book.get('no', {}).get('asks', [])

            return self._calculate_liquidity(orders, desired_size, 'kalshi')

        except Exception as e:
            print(f"Error fetching Kalshi liquidity: {e}")
            return LiquidityAnalysis(
                total_available=0,
                average_price=999.0,
                slippage=999.0,
                is_sufficient=False,
                levels=[]
            )

    def _calculate_liquidity(
        self,
        orders: List[Dict],
        desired_size: int,
        platform: str
    ) -> LiquidityAnalysis:
        """
        Calculate volume-weighted average price and slippage

        Args:
            orders: List of order book entries [{"price": ..., "size": ...}, ...]
            desired_size: How many contracts we want
            platform: "polymarket" or "kalshi" (for price normalization)

        Returns:
            LiquidityAnalysis
        """
        if not orders:
            return LiquidityAnalysis(
                total_available=0,
                average_price=999.0,
                slippage=999.0,
                is_sufficient=False,
                levels=[]
            )

        levels = []
        cumulative_size = 0
        cumulative_cost = 0.0

        for order in orders:
            # Normalize price to dollars
            if platform == 'kalshi':
                # Kalshi prices are in cents
                price = order['price'] / 100.0
            else:
                # Polymarket prices are already in dollars
                price = order['price']

            size = order['size']

            # Add this level
            levels.append(OrderBookLevel(price=price, size=size))

            # Calculate how much of this level we need
            size_to_take = min(size, desired_size - cumulative_size)
            cumulative_size += size_to_take
            cumulative_cost += price * size_to_take

            # Stop if we have enough
            if cumulative_size >= desired_size:
                break

        # Calculate metrics
        if cumulative_size > 0:
            avg_price = cumulative_cost / cumulative_size
            best_price = levels[0].price
            slippage = avg_price - best_price
        else:
            avg_price = 999.0
            slippage = 999.0

        is_sufficient = (
            cumulative_size >= self.min_contracts and
            slippage <= self.max_slippage
        )

        return LiquidityAnalysis(
            total_available=cumulative_size,
            average_price=avg_price,
            slippage=slippage,
            is_sufficient=is_sufficient,
            levels=levels
        )

    def check_arbitrage_liquidity(
        self,
        poly_token_id: str,
        poly_side: str,  # "Up" or "Down"
        kalshi_ticker: str,
        kalshi_side: str,  # "yes" or "no"
        desired_size: int = 100
    ) -> Tuple[LiquidityAnalysis, LiquidityAnalysis, bool]:
        """
        Check if both legs of an arbitrage have sufficient liquidity

        Args:
            poly_token_id: Polymarket token ID
            poly_side: Which side to buy on Polymarket
            kalshi_ticker: Kalshi market ticker
            kalshi_side: Which side to buy on Kalshi
            desired_size: Contracts to trade

        Returns:
            (poly_liquidity, kalshi_liquidity, both_sufficient)
        """
        poly_liq = self.analyze_polymarket_liquidity(
            poly_token_id,
            "buy",  # Always buying
            desired_size
        )

        kalshi_liq = self.analyze_kalshi_liquidity(
            kalshi_ticker,
            kalshi_side,
            desired_size
        )

        both_sufficient = poly_liq.is_sufficient and kalshi_liq.is_sufficient

        return poly_liq, kalshi_liq, both_sufficient

    def calculate_effective_cost(
        self,
        poly_liq: LiquidityAnalysis,
        kalshi_liq: LiquidityAnalysis
    ) -> float:
        """
        Calculate the REAL cost including slippage

        This is what you'll actually pay, not the "best bid/ask" price

        Returns:
            Total effective cost per unit
        """
        return poly_liq.average_price + kalshi_liq.average_price

    def format_liquidity_report(self, analysis: LiquidityAnalysis, platform: str) -> str:
        """
        Create a human-readable liquidity report

        Args:
            analysis: LiquidityAnalysis result
            platform: Platform name for display

        Returns:
            Formatted string
        """
        lines = [
            f"\n{platform.upper()} Liquidity:",
            f"  Available: {analysis.total_available} contracts",
            f"  Avg Price: ${analysis.average_price:.4f}",
            f"  Slippage: ${analysis.slippage:.4f} ({analysis.slippage*100:.2f}%)",
            f"  Sufficient: {'✓ YES' if analysis.is_sufficient else '✗ NO'}",
            f"  Top Levels:"
        ]

        for i, level in enumerate(analysis.levels[:5], 1):  # Show top 5 levels
            lines.append(f"    {i}. ${level.price:.4f} × {level.size}")

        return "\n".join(lines)


# Convenience function
def create_liquidity_analyzer(min_contracts: int = 100, max_slippage: float = 0.005) -> LiquidityAnalyzer:
    """
    Factory function to create a liquidity analyzer

    Args:
        min_contracts: Minimum contracts required (default: 100)
        max_slippage: Maximum slippage allowed in dollars (default: $0.005)

    Returns:
        Configured LiquidityAnalyzer
    """
    return LiquidityAnalyzer(min_contracts, max_slippage)
