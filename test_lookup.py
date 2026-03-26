"""Test script for TCGPlayer Price Lookup

Run this to verify the browser automation works correctly.
"""

import sys
sys.path.insert(0, '.')

from tcgplayer_lookup import TCGPlayerPriceLookup


def test_basic_search():
    """Test basic card search."""
    print("\n" + "="*60)
    print("TEST: Basic Search - Lightning Bolt")
    print("="*60 + "\n")
    
    client = TCGPlayerPriceLookup()
    results = client.search_and_extract_prices("Lightning Bolt")
    
    print(f"\nTest Results:")
    print(f"  Card searched: {results.get('card_name')}")
    print(f"  Prices found: {len(results.get('prices', []))}")
    print(f"  Error: {results.get('error', 'None')}\n")
    
    if results.get('prices'):
        print("Sample prices detected:")
        for p in results['prices'][:3]:
            print(f"    - ${p.get('price', 0):.2f}")
    
    client.close_browser()
    return 'success' if not results.get('error') else 'failed'


def test_set_specific_search():
    """Test set-specific card search."""
    print("\n" + "="*60)
    print("TEST: Set-Specific Search - Black Lotus LEA")
    print("="*60 + "\n")
    
    client = TCGPlayerPriceLookup()
    results = client.search_and_extract_prices("Black Lotus", "LEA")
    
    print(f"\nTest Results:")
    print(f"  Card searched: {results.get('card_name')}")
    print(f"  Set code: {results.get('set_code')}")
    print(f"  Prices found: {len(results.get('prices', []))}")
    
    if results.get('set_specific_price'):
        sp = results['set_specific_price']
        print(f"  Set-specific price: ${sp.get('price', 0):.2f}")
    
    client.close_browser()
    return 'success' if not results.get('error') else 'failed'


def test_formatting():
    """Test result formatting."""
    print("\n" + "="*60)
    print("TEST: Result Formatting")
    print("="*60 + "\n")
    
    client = TCGPlayerPriceLookup()
    results = {
        "card_name": "Test Card",
        "set_code": "MH3",
        "prices": [
            {"type": "market_price", "price": 1.99},
            {"type": "low_price", "price": 1.50}
        ],
        "set_specific_price": {
            "card_name": "Test Card",
            "set_code": "MH3",
            "price": 2.49
        }
    }
    
    formatted = client.format_results(results)
    print(formatted)
    return 'success'


def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("TCGPlayer Price Lookup - Test Suite")
    print("#"*60)
    
    results = {}
    
    # Run tests
    results['basic_search'] = test_basic_search()
    results['set_specific_search'] = test_set_specific_search()
    results['formatting'] = test_formatting()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, status in results.items():
        symbol = "PASS" if status == 'success' else "FAIL"
        print(f"  [{symbol}] {test_name}")
    
    print("\nAll tests completed!\n")


if __name__ == "__main__":
    main()
