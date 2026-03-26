"""TCGPlayer Price Lookup System

A browser automation system for looking up Magic: The Gathering card prices
on TCGPlayer using Hermes browser tools.

Usage:
    python3 tcgplayer_lookup.py "Black Lotus" LEA
    python3 tcgplayer_lookup.py "Lightning Bolt"
"""

import sys
import time
import json
from typing import Dict, Optional, List, Any


class TCGPlayerPriceLookup:
    """Browser automation client for TCGPlayer price lookups."""
    
    BASE_URL = "https://tcgplayer.com"
    
    def __init__(self):
        self.session_active = False
        self.current_url = None
        
    def navigate_to_search(self, card_name: str, set_code: str = None) -> Dict[str, Any]:
        """
        Navigate to TCGPlayer search page for a card.
        
        Args:
            card_name: Name of the card to search
            set_code: Optional set code filter (e.g., 'LEA', 'MH3')
            
        Returns:
            Dict with navigation status and URL
        """
        # Build search query
        query = card_name
        if set_code:
            query += f" {set_code}"
        
        # Encode URL properly
        encoded_query = query.replace(' ', '+').replace('&', '%26')
        url = f"{self.BASE_URL}/products/search?q={encoded_query}"
        
        print(f"[NAVIGATE] Going to: {url}")
        
        # Use Hermes browser_navigate tool
        result = browser_navigate(url=url)
        
        self.session_active = True
        self.current_url = url
        
        return {
            "status": "success",
            "url": url,
            "query": query,
            "card_name": card_name,
            "set_code": set_code
        }
    
    def get_page_snapshot(self, full: bool = False) -> str:
        """
        Get text-based snapshot of current page.
        
        Args:
            full: If True, return complete page content; otherwise compact view
            
        Returns:
            Text representation of page with interactive element refs
        """
        print(f"[SNAPSHOT] Getting {'full' if full else 'compact'} snapshot...")
        
        # Use Hermes browser_snapshot tool
        result = browser_snapshot(full=full)
        
        return str(result)
    
    def click_element(self, ref: str) -> Dict[str, Any]:
        """
        Click on an element identified by its ref ID.
        
        Args:
            ref: Element reference (e.g., '@e1', '@e2')
            
        Returns:
            Status of click operation
        """
        print(f"[CLICK] Clicking element: {ref}")
        
        # Use Hermes browser_click tool
        result = browser_click(ref=ref)
        
        return {
            "status": "success",
            "clicked_ref": ref
        }
    
    def scroll_page(self, direction: str = "down") -> Dict[str, Any]:
        """
        Scroll the page to reveal more content.
        
        Args:
            direction: 'up' or 'down'
            
        Returns:
            Status of scroll operation
        """
        print(f"[SCROLL] Scrolling {direction}...")
        
        # Use Hermes browser_scroll tool
        result = browser_scroll(direction=direction)
        
        return {
            "status": "success",
            "direction": direction
        }
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """
        Press a keyboard key (e.g., 'Enter' to submit search).
        
        Args:
            key: Key name (e.g., 'Enter', 'Tab', 'Escape')
            
        Returns:
            Status of press operation
        """
        print(f"[PRESS] Pressing key: {key}")
        
        # Use Hermes browser_press tool
        result = browser_press(key=key)
        
        return {
            "status": "success",
            "key": key
        }
    
    def type_text(self, ref: str, text: str) -> Dict[str, Any]:
        """
        Type text into an input field.
        
        Args:
            ref: Input field reference (e.g., '@e1')
            text: Text to type
            
        Returns:
            Status of typing operation
        """
        print(f"[TYPE] Typing '{text}' into {ref}")
        
        # Use Hermes browser_type tool
        result = browser_type(ref=ref, text=text)
        
        return {
            "status": "success",
            "ref": ref,
            "text": text
        }
    
    def close_browser(self) -> Dict[str, Any]:
        """
        Close the browser session.
        
        Returns:
            Status of close operation
        """
        print("[CLOSE] Closing browser session...")
        
        # Use Hermes browser_close tool
        result = browser_close()
        
        self.session_active = False
        
        return {
            "status": "success",
            "session_closed": True
        }
    
    def search_and_extract_prices(self, card_name: str, set_code: str = None) -> Dict[str, Any]:
        """
        Complete workflow: search for a card and extract price information.
        
        Args:
            card_name: Name of the card to search
            set_code: Optional set code filter
            
        Returns:
            Dict containing:
                - card_info: Card name and set
                - prices: Extracted price data
                - raw_snapshot: Page content for debugging
        """
        result = {
            "card_name": card_name,
            "set_code": set_code,
            "prices": [],
            "error": None
        }
        
        try:
            # Step 1: Navigate to search page
            nav_result = self.navigate_to_search(card_name, set_code)
            print(f"\nNavigation result: {json.dumps(nav_result, indent=2)}")
            
            # Wait for page to load
            time.sleep(2)
            
            # Step 2: Get compact snapshot first
            compact_snapshot = self.get_page_snapshot(full=False)
            print(f"\n--- COMPACT SNAPSHOT ---")
            print(compact_snapshot[:3000] if len(compact_snapshot) > 3000 else compact_snapshot)
            
            # Step 3: Get full snapshot for detailed parsing
            full_snapshot = self.get_page_snapshot(full=True)
            
            # Step 4: Parse prices from snapshot
            prices = self._parse_prices_from_snapshot(full_snapshot, card_name)
            result["prices"] = prices
            
            # Step 5: Try to identify the specific card if set code provided
            if set_code:
                print(f"\n[FILTER] Looking for {card_name} from set {set_code}...")
                filtered_price = self._find_set_specific_price(
                    full_snapshot, card_name, set_code
                )
                if filtered_price:
                    result["set_specific_price"] = filtered_price
            
        except Exception as e:
            result["error"] = str(e)
            print(f"[ERROR] {e}")
        
        return result
    
    def _parse_prices_from_snapshot(self, snapshot: str, card_name: str) -> List[Dict]:
        """
        Extract price information from page snapshot.
        
        Args:
            snapshot: Full page content as text
            card_name: Name of the card being searched
            
        Returns:
            List of dicts with card name, set, and prices
        """
        import re
        
        prices = []
        
        # Pattern 1: Look for price elements with ref IDs
        # e.g., "@e5 $24.99" or "Price: @e3 $15.00"
        price_pattern = r'(@\d+)\s*\$([\d,]+\.\d{2})'
        price_matches = re.findall(price_pattern, snapshot)
        
        for ref, price_str in price_matches:
            prices.append({
                "ref": ref,
                "price": float(price_str.replace(',', '')),
                "type": "detected_price"
            })
        
        # Pattern 2: Look for market price text
        market_pattern = r'(Market Price|Low Price|Average Price)\s*[\$]?([\d,]+\.\d{2})'
        market_matches = re.findall(market_pattern, snapshot)
        
        for price_type, price_str in market_matches:
            prices.append({
                "type": price_type.lower().replace(' ', '_'),
                "price": float(price_str.replace(',', '')),
                "raw_text": f"{price_type}: ${price_str}"
            })
        
        # Pattern 3: Look for card entries with prices
        # TCGPlayer search results typically have format like:
        # "Card Name - Set Name @eX $XX.XX"
        card_entry_pattern = r'(.+?)\s*-\s*(.+?)\s*(@\d+)\s*\$([\d,]+\.\d{2})'
        card_matches = re.findall(card_entry_pattern, snapshot)
        
        for entry in card_matches:
            entry_card_name = entry[0].strip()
            entry_set_name = entry[1].strip()
            entry_ref = entry[2]
            entry_price = float(entry[3].replace(',', ''))
            
            # Check if this matches our search
            if card_name.lower() in entry_card_name.lower():
                prices.append({
                    "card_name": entry_card_name,
                    "set_name": entry_set_name,
                    "ref": entry_ref,
                    "price": entry_price,
                    "type": "search_result"
                })
        
        return prices
    
    def _find_set_specific_price(
        self, 
        snapshot: str, 
        card_name: str, 
        set_code: str
    ) -> Optional[Dict]:
        """
        Find price for a specific card/set combination.
        
        Args:
            snapshot: Full page content
            card_name: Card name
            set_code: Set code (e.g., 'LEA', 'MH3')
            
        Returns:
            Dict with price info or None if not found
        """
        # Look for the set code in the snapshot and extract nearby price
        import re
        
        # Pattern to find set code followed by price within ~100 characters
        pattern = rf'{set_code}[\s\-\.]*[\S\s]{{0,200}}\$([\d,]+\.\d{{2}})'
        match = re.search(pattern, snapshot)
        
        if match:
            price_str = match.group(1)
            return {
                "card_name": card_name,
                "set_code": set_code,
                "price": float(price_str.replace(',', '')),
                "source": "set_code_match"
            }
        
        return None
    
    def format_results(self, results: Dict) -> str:
        """
        Format lookup results as readable text.
        
        Args:
            results: Results dict from search_and_extract_prices
            
        Returns:
            Formatted string for display
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"TCGPlayer Price Lookup Results")
        lines.append("=" * 60)
        lines.append("")
        
        # Card info
        card_info = f"{results.get('card_name', 'Unknown')}"
        if results.get('set_code'):
            card_info += f" ({results.get('set_code')})"
        lines.append(f"Searching for: {card_info}")
        lines.append("")
        
        # Set-specific price
        if 'set_specific_price' in results:
            sp = results['set_specific_price']
            lines.append(f"Set-Specific Price ({sp.get('set_code')}): ${sp.get('price'):.2f}")
            lines.append("")
        
        # All detected prices
        prices = results.get('prices', [])
        if prices:
            lines.append("Detected Prices:")
            for i, p in enumerate(prices[:10], 1):  # Limit to first 10
                price_info = f"  {i}. ${p.get('price', 0):.2f}"
                if 'card_name' in p:
                    price_info += f" - {p.get('card_name') or ''}"
                if 'set_name' in p and p.get('set_name'):
                    price_info += f" ({p.get('set_name')})"
                lines.append(price_info)
            lines.append("")
        else:
            lines.append("No prices detected.")
            lines.append("")
        
        # Error info
        if results.get('error'):
            lines.append(f"Error: {results.get('error')}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """Main entry point for command-line usage."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python3 tcgplayer_lookup.py <card_name> [set_code]")
        print("Example: python3 tcgplayer_lookup.py 'Black Lotus' LEA")
        sys.exit(1)
    
    card_name = sys.argv[1]
    set_code = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\n{'='*60}")
    print(f"TCGPlayer Price Lookup")
    print(f"{'='*60}")
    print(f"Card: {card_name}")
    if set_code:
        print(f"Set Code: {set_code}")
    print(f"\nStarting browser automation...\n")
    
    # Create lookup client and run search
    client = TCGPlayerPriceLookup()
    results = client.search_and_extract_prices(card_name, set_code)
    
    # Format and display results
    formatted = client.format_results(results)
    print(formatted)
    
    # Also return JSON for programmatic use
    print("\nJSON Results:")
    print(json.dumps(results, indent=2, default=str))
    
    # Close browser
    client.close_browser()
    
    return results


if __name__ == "__main__":
    main()
