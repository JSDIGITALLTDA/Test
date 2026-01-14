"""
Market Mapping System for Cross-Platform Arbitrage

This module handles the complex task of matching markets between Polymarket and Kalshi.
Markets may have different tickers, descriptions, and resolution criteria, so we need
intelligent mapping logic.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MarketCategory(Enum):
    """Categories of markets we support"""
    CRYPTO_PRICE = "crypto_price"
    SPORTS = "sports"
    POLITICS = "politics"
    MACRO = "macro"
    WEATHER = "weather"


@dataclass
class MarketMapping:
    """Represents a matched pair of markets across platforms"""
    polymarket_id: str
    kalshi_id: str
    category: MarketCategory
    description: str
    resolution_source: str  # e.g., "Coinbase", "Associated Press", etc.
    expiry_time: str
    confidence_score: float  # 0-1, how confident we are in the match


class MarketMapper:
    """
    Intelligent market matching system that pairs Polymarket and Kalshi markets
    """

    def __init__(self):
        # Predefined mappings for common markets
        self.static_mappings = {
            # BTC Price Markets
            "btc_hourly": {
                "polymarket_pattern": r"Bitcoin.*1-Hour.*Price",
                "kalshi_pattern": r"INXBTC-.*",
                "category": MarketCategory.CRYPTO_PRICE,
                "resolution_source": "Coinbase"
            },
            # Add more static mappings here for sports, politics, etc.
            "nfl_games": {
                "polymarket_pattern": r"NFL.*Winner",
                "kalshi_pattern": r"NFL-.*",
                "category": MarketCategory.SPORTS,
                "resolution_source": "ESPN"
            },
            "us_elections": {
                "polymarket_pattern": r"(President|Senate|House).*202[0-9]",
                "kalshi_pattern": r"(PRES|SEN|HOUSE)-.*",
                "category": MarketCategory.POLITICS,
                "resolution_source": "Associated Press"
            }
        }

    def extract_btc_strike(self, description: str) -> Optional[float]:
        """
        Extract BTC strike price from market description
        Examples:
        - "Bitcoin 1-Hour Price Above $95,000?" -> 95000
        - "BTC >= $100k" -> 100000
        """
        # Remove commas
        desc = description.replace(',', '')

        # Try various patterns
        patterns = [
            r'\$(\d+)k',  # $95k format
            r'\$(\d+)K',  # $95K format
            r'\$(\d+)',   # $95000 format
            r'(\d+)k',    # 95k format
            r'(\d+)K',    # 95K format
        ]

        for pattern in patterns:
            match = re.search(pattern, desc)
            if match:
                value = float(match.group(1))
                # If it's in 'k' format, multiply by 1000
                if 'k' in pattern.lower():
                    value *= 1000
                return value

        return None

    def match_btc_markets(
        self,
        poly_markets: List[Dict],
        kalshi_markets: List[Dict]
    ) -> List[MarketMapping]:
        """
        Match BTC price markets between platforms

        Args:
            poly_markets: List of Polymarket market data
            kalshi_markets: List of Kalshi market data

        Returns:
            List of matched market pairs
        """
        mappings = []

        for poly in poly_markets:
            poly_desc = poly.get('description', '')
            poly_strike = self.extract_btc_strike(poly_desc)

            if not poly_strike:
                continue

            # Find matching Kalshi market
            for kalshi in kalshi_markets:
                kalshi_desc = kalshi.get('title', '')
                kalshi_strike = kalshi.get('strike_price', 0)

                # Check if strikes match (within small tolerance)
                if abs(kalshi_strike - poly_strike) < 100:  # $100 tolerance
                    mapping = MarketMapping(
                        polymarket_id=poly.get('condition_id', ''),
                        kalshi_id=kalshi.get('ticker', ''),
                        category=MarketCategory.CRYPTO_PRICE,
                        description=f"BTC ${poly_strike:,.0f}",
                        resolution_source="Coinbase BTC-USD",
                        expiry_time=poly.get('end_date', ''),
                        confidence_score=0.95  # High confidence for exact strike match
                    )
                    mappings.append(mapping)

        return mappings

    def match_sports_markets(
        self,
        poly_markets: List[Dict],
        kalshi_markets: List[Dict]
    ) -> List[MarketMapping]:
        """
        Match sports markets (NFL, NBA, etc.)

        This is more complex because team names might vary:
        - Polymarket: "Kansas City Chiefs"
        - Kalshi: "KC Chiefs" or "Chiefs"
        """
        mappings = []

        # Team name normalization
        team_aliases = {
            "kansas city chiefs": ["kc chiefs", "chiefs", "kansas city"],
            "san francisco 49ers": ["sf 49ers", "49ers", "san francisco"],
            # Add more team aliases as needed
        }

        for poly in poly_markets:
            poly_desc = poly.get('description', '').lower()

            # Extract team names, game dates, etc.
            # This is complex and would need robust parsing
            # For now, we'll use simple keyword matching

            for kalshi in kalshi_markets:
                kalshi_desc = kalshi.get('title', '').lower()

                # Check for common keywords
                poly_words = set(poly_desc.split())
                kalshi_words = set(kalshi_desc.split())
                overlap = poly_words & kalshi_words

                # If significant overlap, it might be a match
                if len(overlap) >= 3:  # At least 3 words in common
                    mapping = MarketMapping(
                        polymarket_id=poly.get('condition_id', ''),
                        kalshi_id=kalshi.get('ticker', ''),
                        category=MarketCategory.SPORTS,
                        description=poly.get('question', ''),
                        resolution_source="ESPN",
                        expiry_time=poly.get('end_date', ''),
                        confidence_score=len(overlap) / max(len(poly_words), len(kalshi_words))
                    )
                    mappings.append(mapping)

        return mappings

    def validate_resolution_source(self, mapping: MarketMapping) -> bool:
        """
        Verify that both platforms use the same resolution source

        This is CRITICAL to avoid resolution risk where one platform
        says YES and the other says NO for the same event.
        """
        # This would require checking the actual market rules
        # For now, we return True for known safe categories
        safe_categories = [
            MarketCategory.CRYPTO_PRICE,  # Both use major exchanges
        ]

        if mapping.category in safe_categories:
            return True

        # For sports/politics, we'd need to check the specific rules
        # Return False to be conservative
        return False

    def get_all_mappings(
        self,
        poly_markets: List[Dict],
        kalshi_markets: List[Dict],
        categories: Optional[List[MarketCategory]] = None
    ) -> List[MarketMapping]:
        """
        Get all market mappings for specified categories

        Args:
            poly_markets: Polymarket data
            kalshi_markets: Kalshi data
            categories: Which categories to match (None = all)

        Returns:
            List of validated market mappings
        """
        all_mappings = []

        if not categories:
            categories = list(MarketCategory)

        if MarketCategory.CRYPTO_PRICE in categories:
            all_mappings.extend(self.match_btc_markets(poly_markets, kalshi_markets))

        if MarketCategory.SPORTS in categories:
            all_mappings.extend(self.match_sports_markets(poly_markets, kalshi_markets))

        # Filter by resolution source validation
        validated_mappings = [
            m for m in all_mappings
            if self.validate_resolution_source(m)
        ]

        return validated_mappings


# Convenience function
def create_market_mapper() -> MarketMapper:
    """Factory function to create a market mapper"""
    return MarketMapper()
