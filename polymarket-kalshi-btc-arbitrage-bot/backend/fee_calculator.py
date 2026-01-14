"""
Fee Calculator for Cross-Platform Arbitrage

Kalshi has a VARIABLE fee structure that depends on the contract price.
You MUST account for fees or you'll think you found an arbitrage when you didn't!

Fee Structure (as of 2025):
- Kalshi: ~7% of the LESSER of the buy/sell price (varies by market)
- Polymarket: Near-zero fees (gasless with Safe Wallet on Polygon)

CRITICAL: When calculating arbitrage, you must use the "Net Price" which is:
    Net Price = Contract Price + Fees
"""

from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class FeeBreakdown:
    """Detailed fee breakdown for a trade"""
    platform: str
    contract_price: float
    fee_rate: float
    fee_amount: float
    net_price: float  # What you actually pay


class FeeCalculator:
    """
    Calculates trading fees for Polymarket and Kalshi
    """

    def __init__(
        self,
        kalshi_fee_rate: float = 0.07,  # 7% default
        polymarket_fee_rate: float = 0.0  # Effectively 0 with Safe Wallet
    ):
        """
        Args:
            kalshi_fee_rate: Kalshi's fee percentage (0.07 = 7%)
            polymarket_fee_rate: Polymarket's fee percentage
        """
        self.kalshi_fee_rate = kalshi_fee_rate
        self.polymarket_fee_rate = polymarket_fee_rate

    def calculate_kalshi_fee(self, price: float, side: str = "buy") -> float:
        """
        Calculate Kalshi's fee for a trade

        Kalshi charges a percentage of the LESSER of buy/sell price.
        For a YES at $0.60, the NO is implicitly $0.40.
        Fee is on the lesser: min(0.60, 0.40) = 0.40

        Args:
            price: Contract price in dollars (0.00 - 1.00)
            side: "buy" or "sell" (currently unused, but here for future)

        Returns:
            Fee amount in dollars
        """
        # The fee is on the lesser of (price, 1-price)
        lesser_price = min(price, 1.0 - price)
        fee = lesser_price * self.kalshi_fee_rate

        return fee

    def calculate_polymarket_fee(self, price: float) -> float:
        """
        Calculate Polymarket's fee

        With Safe Wallet and gasless transactions, this is effectively 0.
        But we keep this method for future changes.

        Args:
            price: Contract price in dollars

        Returns:
            Fee amount in dollars
        """
        return price * self.polymarket_fee_rate

    def get_kalshi_net_price(self, price: float) -> float:
        """
        Get the NET price you'll pay on Kalshi (price + fee)

        This is the REAL cost you must use in arbitrage calculations!

        Args:
            price: Quoted contract price

        Returns:
            Net price (price + fee)
        """
        fee = self.calculate_kalshi_fee(price)
        return price + fee

    def get_polymarket_net_price(self, price: float) -> float:
        """
        Get the NET price you'll pay on Polymarket

        Args:
            price: Quoted contract price

        Returns:
            Net price (price + fee)
        """
        fee = self.calculate_polymarket_fee(price)
        return price + fee

    def calculate_arbitrage_cost(
        self,
        poly_price: float,
        kalshi_price: float,
        include_fees: bool = True
    ) -> Tuple[float, FeeBreakdown, FeeBreakdown]:
        """
        Calculate total cost for both legs of an arbitrage trade

        Args:
            poly_price: Polymarket contract price
            kalshi_price: Kalshi contract price (in dollars, not cents!)
            include_fees: Whether to include fees in calculation

        Returns:
            (total_cost, poly_fee_breakdown, kalshi_fee_breakdown)
        """
        if include_fees:
            poly_fee = self.calculate_polymarket_fee(poly_price)
            poly_net = poly_price + poly_fee

            kalshi_fee = self.calculate_kalshi_fee(kalshi_price)
            kalshi_net = kalshi_price + kalshi_fee

            total_cost = poly_net + kalshi_net
        else:
            poly_fee = 0.0
            poly_net = poly_price
            kalshi_fee = 0.0
            kalshi_net = kalshi_price
            total_cost = poly_price + kalshi_price

        poly_breakdown = FeeBreakdown(
            platform="Polymarket",
            contract_price=poly_price,
            fee_rate=self.polymarket_fee_rate,
            fee_amount=poly_fee,
            net_price=poly_net
        )

        kalshi_breakdown = FeeBreakdown(
            platform="Kalshi",
            contract_price=kalshi_price,
            fee_rate=self.kalshi_fee_rate,
            fee_amount=kalshi_fee,
            net_price=kalshi_net
        )

        return total_cost, poly_breakdown, kalshi_breakdown

    def is_profitable_after_fees(
        self,
        poly_price: float,
        kalshi_price: float,
        min_profit: float = 0.01  # Minimum $0.01 profit
    ) -> Tuple[bool, float]:
        """
        Check if an arbitrage opportunity is profitable after fees

        Args:
            poly_price: Polymarket price
            kalshi_price: Kalshi price
            min_profit: Minimum required profit margin

        Returns:
            (is_profitable, actual_profit)
        """
        total_cost, _, _ = self.calculate_arbitrage_cost(
            poly_price,
            kalshi_price,
            include_fees=True
        )

        profit = 1.0 - total_cost
        is_profitable = profit >= min_profit

        return is_profitable, profit

    def format_fee_report(
        self,
        poly_breakdown: FeeBreakdown,
        kalshi_breakdown: FeeBreakdown,
        total_cost: float
    ) -> str:
        """
        Create a human-readable fee breakdown report

        Args:
            poly_breakdown: Polymarket fee details
            kalshi_breakdown: Kalshi fee details
            total_cost: Total cost of both legs

        Returns:
            Formatted string
        """
        lines = [
            "\n💰 FEE BREAKDOWN:",
            f"\n{poly_breakdown.platform}:",
            f"  Contract Price: ${poly_breakdown.contract_price:.4f}",
            f"  Fee ({poly_breakdown.fee_rate*100:.1f}%): ${poly_breakdown.fee_amount:.4f}",
            f"  Net Price: ${poly_breakdown.net_price:.4f}",
            f"\n{kalshi_breakdown.platform}:",
            f"  Contract Price: ${kalshi_breakdown.contract_price:.4f}",
            f"  Fee ({kalshi_breakdown.fee_rate*100:.1f}%): ${kalshi_breakdown.fee_amount:.4f}",
            f"  Net Price: ${kalshi_breakdown.net_price:.4f}",
            f"\n📊 TOTAL:",
            f"  Combined Cost: ${total_cost:.4f}",
            f"  Potential Profit: ${1.0 - total_cost:.4f}",
            f"  Status: {'✅ PROFITABLE' if total_cost < 1.0 else '❌ NOT PROFITABLE'}"
        ]

        return "\n".join(lines)

    def get_break_even_prices(self, poly_price: float) -> Dict[str, float]:
        """
        Calculate what Kalshi price would break even with fees

        Given a Polymarket price, what's the maximum Kalshi price we can pay?

        Args:
            poly_price: Polymarket contract price

        Returns:
            Dictionary with break-even analysis
        """
        poly_net = self.get_polymarket_net_price(poly_price)

        # We need: poly_net + kalshi_net <= 1.00
        # So: kalshi_net <= 1.00 - poly_net
        max_kalshi_net = 1.0 - poly_net

        # But kalshi_net = kalshi_price + kalshi_fee
        # And kalshi_fee = min(kalshi_price, 1-kalshi_price) * fee_rate
        # This is a bit complex to solve algebraically, so we'll approximate

        # For simplicity: assume fee is on kalshi_price (if price < 0.5)
        # kalshi_price + (kalshi_price * fee_rate) <= max_kalshi_net
        # kalshi_price * (1 + fee_rate) <= max_kalshi_net
        max_kalshi_price_approx = max_kalshi_net / (1 + self.kalshi_fee_rate)

        return {
            "poly_net_price": poly_net,
            "max_kalshi_net": max_kalshi_net,
            "max_kalshi_price_approx": max_kalshi_price_approx
        }


# Convenience function
def create_fee_calculator(
    kalshi_fee_rate: float = 0.07,
    polymarket_fee_rate: float = 0.0
) -> FeeCalculator:
    """
    Factory function to create a fee calculator

    Args:
        kalshi_fee_rate: Kalshi's fee percentage (default 7%)
        polymarket_fee_rate: Polymarket's fee percentage (default 0%)

    Returns:
        Configured FeeCalculator
    """
    return FeeCalculator(kalshi_fee_rate, polymarket_fee_rate)
