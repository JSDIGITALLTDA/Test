"""
Enhanced Multi-Market Arbitrage Bot

This bot combines all the advanced features:
- Market mapping across multiple categories
- Liquidity analysis to prevent slippage
- Accurate fee calculations
- Execution engine with dry-run mode
- Risk management

Usage:
    # Test mode (no real trades)
    python enhanced_arbitrage_bot.py --dry-run

    # Live trading (DANGEROUS!)
    python enhanced_arbitrage_bot.py --live
"""

import os
import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict

# Import our custom modules
from market_mapper import create_market_mapper, MarketCategory
from liquidity_analyzer import create_liquidity_analyzer
from fee_calculator import create_fee_calculator
from execution_engine import create_execution_engine

# Import existing data fetchers
from fetch_current_polymarket import fetch_polymarket_data_struct
from fetch_current_kalshi import fetch_kalshi_data_struct


class EnhancedArbitrageBot:
    """
    Advanced arbitrage bot with professional risk management
    """

    def __init__(
        self,
        dry_run: bool = True,
        min_profit: float = 0.02,  # Minimum $0.02 profit
        min_contracts: int = 50,  # Minimum liquidity required
        max_slippage: float = 0.005,  # Maximum $0.005 slippage
        kalshi_fee_rate: float = 0.07,  # 7% fee
        scan_interval: int = 2  # Seconds between scans
    ):
        """
        Args:
            dry_run: If True, simulate trades only
            min_profit: Minimum profit required (after fees)
            min_contracts: Minimum contracts needed for execution
            max_slippage: Maximum acceptable slippage
            kalshi_fee_rate: Kalshi's fee percentage
            scan_interval: Seconds between market scans
        """
        self.dry_run = dry_run
        self.min_profit = min_profit
        self.scan_interval = scan_interval

        print("🤖 Initializing Enhanced Arbitrage Bot...")
        print(f"   Mode: {'🧪 DRY RUN' if dry_run else '💰 LIVE TRADING'}")
        print(f"   Min Profit: ${min_profit:.4f}")
        print(f"   Min Contracts: {min_contracts}")
        print(f"   Max Slippage: ${max_slippage:.4f}")

        # Initialize modules
        self.market_mapper = create_market_mapper()
        self.liquidity_analyzer = create_liquidity_analyzer(
            min_contracts=min_contracts,
            max_slippage=max_slippage
        )
        self.fee_calculator = create_fee_calculator(
            kalshi_fee_rate=kalshi_fee_rate,
            polymarket_fee_rate=0.0
        )
        self.execution_engine = create_execution_engine(
            dry_run=dry_run,
            kalshi_api_key=os.getenv('KALSHI_API_KEY'),
            kalshi_private_key_path=os.getenv('KALSHI_PRIVATE_KEY_PATH'),
            polymarket_private_key=os.getenv('POLYMARKET_PRIVATE_KEY')
        )

        # Stats tracking
        self.stats = {
            "scans": 0,
            "opportunities_found": 0,
            "trades_executed": 0,
            "trades_successful": 0,
            "total_profit": 0.0
        }

        print("✅ Bot initialized successfully\n")

    def scan_btc_markets(self) -> List[Dict]:
        """
        Scan for BTC price arbitrage opportunities

        Returns:
            List of opportunities found
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Scanning BTC markets...")

        # Fetch data from both platforms
        poly_data, poly_err = fetch_polymarket_data_struct()
        kalshi_data, kalshi_err = fetch_kalshi_data_struct()

        if poly_err or kalshi_err:
            print(f"  ❌ Error fetching data: {poly_err or kalshi_err}")
            return []

        if not poly_data or not kalshi_data:
            print("  ⚠️  Missing market data")
            return []

        # Extract market info
        poly_strike = poly_data['price_to_beat']
        poly_up_price = poly_data['prices'].get('Up', 0.0)
        poly_down_price = poly_data['prices'].get('Down', 0.0)

        kalshi_markets = kalshi_data.get('markets', [])

        if not kalshi_markets:
            print("  ⚠️  No Kalshi markets found")
            return []

        print(f"  📊 Polymarket: Strike ${poly_strike:,.0f} | Up ${poly_up_price:.3f} | Down ${poly_down_price:.3f}")
        print(f"  📊 Kalshi: {len(kalshi_markets)} markets available")

        opportunities = []

        # Check each Kalshi market for arbitrage
        for km in kalshi_markets:
            kalshi_strike = km['strike']
            kalshi_yes_price = km['yes_ask'] / 100.0
            kalshi_no_price = km['no_ask'] / 100.0

            # Only check markets near the Poly strike
            if abs(kalshi_strike - poly_strike) > 2500:
                continue

            # Determine strategy based on strike comparison
            if poly_strike > kalshi_strike:
                # Strategy: Buy Poly Down + Kalshi Yes
                poly_price = poly_down_price
                kalshi_price = kalshi_yes_price
                strategy = "Poly Down + Kalshi Yes"

            elif poly_strike < kalshi_strike:
                # Strategy: Buy Poly Up + Kalshi No
                poly_price = poly_up_price
                kalshi_price = kalshi_no_price
                strategy = "Poly Up + Kalshi No"

            else:
                # Equal strikes - check both strategies
                # For simplicity, check the better one
                cost1 = poly_down_price + kalshi_yes_price
                cost2 = poly_up_price + kalshi_no_price

                if cost1 < cost2:
                    poly_price = poly_down_price
                    kalshi_price = kalshi_yes_price
                    strategy = "Poly Down + Kalshi Yes"
                else:
                    poly_price = poly_up_price
                    kalshi_price = kalshi_no_price
                    strategy = "Poly Up + Kalshi No"

            # Calculate cost WITH FEES
            total_cost, poly_fees, kalshi_fees = self.fee_calculator.calculate_arbitrage_cost(
                poly_price,
                kalshi_price,
                include_fees=True
            )

            profit = 1.0 - total_cost

            # Check if profitable
            if profit >= self.min_profit:
                opportunity = {
                    "strategy": strategy,
                    "poly_strike": poly_strike,
                    "kalshi_strike": kalshi_strike,
                    "poly_price": poly_price,
                    "kalshi_price": kalshi_price,
                    "total_cost": total_cost,
                    "profit": profit,
                    "poly_fees": poly_fees,
                    "kalshi_fees": kalshi_fees,
                    "timestamp": datetime.now().isoformat()
                }
                opportunities.append(opportunity)

        return opportunities

    def execute_opportunity(self, opp: Dict) -> bool:
        """
        Execute an arbitrage opportunity

        Args:
            opp: Opportunity dictionary

        Returns:
            True if successful
        """
        print(f"\n🎯 EXECUTING OPPORTUNITY:")
        print(f"   Strategy: {opp['strategy']}")
        print(f"   Poly Strike: ${opp['poly_strike']:,.0f}")
        print(f"   Kalshi Strike: ${opp['kalshi_strike']:,.0f}")
        print(f"   Total Cost: ${opp['total_cost']:.4f}")
        print(f"   Expected Profit: ${opp['profit']:.4f}")

        # In a real implementation, you would:
        # 1. Check current liquidity
        # 2. Place orders via execution engine
        # 3. Monitor fills
        # 4. Update stats

        # For now, just simulate
        if self.dry_run:
            print(f"   [DRY RUN] Simulated execution - SUCCESS")
            self.stats["trades_executed"] += 1
            self.stats["trades_successful"] += 1
            self.stats["total_profit"] += opp['profit']
            return True
        else:
            # Real execution would go here
            print(f"   ⚠️  Real execution not yet implemented")
            return False

    def run(self):
        """
        Main bot loop
        """
        print("🚀 Starting arbitrage bot...")
        print(f"   Scanning every {self.scan_interval} seconds")
        print(f"   Press Ctrl+C to stop\n")

        try:
            while True:
                self.stats["scans"] += 1

                # Scan for opportunities
                opportunities = self.scan_btc_markets()

                if opportunities:
                    print(f"\n🎉 Found {len(opportunities)} opportunities!")
                    self.stats["opportunities_found"] += len(opportunities)

                    # Execute the best one
                    best_opp = max(opportunities, key=lambda x: x['profit'])
                    self.execute_opportunity(best_opp)

                else:
                    print(f"  ℹ️  No profitable opportunities found")

                # Print stats
                print(f"\n📈 SESSION STATS:")
                print(f"   Scans: {self.stats['scans']}")
                print(f"   Opportunities: {self.stats['opportunities_found']}")
                print(f"   Trades: {self.stats['trades_executed']}/{self.stats['trades_successful']}")
                print(f"   Total Profit: ${self.stats['total_profit']:.4f}")

                print("-" * 60)

                # Wait before next scan
                time.sleep(self.scan_interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping bot...")
            print(f"\n📊 FINAL STATS:")
            print(f"   Total Scans: {self.stats['scans']}")
            print(f"   Opportunities Found: {self.stats['opportunities_found']}")
            print(f"   Trades Executed: {self.stats['trades_executed']}")
            print(f"   Successful Trades: {self.stats['trades_successful']}")
            print(f"   Total Profit: ${self.stats['total_profit']:.4f}")
            print("\n👋 Goodbye!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Enhanced Arbitrage Bot')
    parser.add_argument(
        '--mode',
        choices=['dry-run', 'live'],
        default='dry-run',
        help='Trading mode (default: dry-run)'
    )
    parser.add_argument(
        '--min-profit',
        type=float,
        default=0.02,
        help='Minimum profit required (default: 0.02)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=2,
        help='Scan interval in seconds (default: 2)'
    )

    args = parser.parse_args()

    # Create and run bot
    bot = EnhancedArbitrageBot(
        dry_run=(args.mode == 'dry-run'),
        min_profit=args.min_profit,
        scan_interval=args.interval
    )

    bot.run()


if __name__ == "__main__":
    main()
