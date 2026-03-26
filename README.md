# TCGPlayer Price Lookup System

Browser automation system for looking up Magic: The Gathering card prices on TCGPlayer using Hermes Agent browser tools.

## Overview

This system uses Hermes' built-in browser automation capabilities to:
- Navigate to TCGPlayer search pages
- Extract price information from search results
- Support set-specific lookups (e.g., "Black Lotus LEA")
- Parse multiple price points (market price, low price, etc.)

## Features

- **No API Key Required** - Uses public-facing website, no authentication needed
- **Set-Specific Lookups** - Filter by set code for accurate pricing
- **Multiple Price Extraction** - Captures market price, low price, and list prices
- **Hermes Integration** - Works with Hermes browser tools natively

## Installation

```bash
cd ~/Documents/ObsidianVault/Pocket-Shop/Source/tcgplayer-pricing
```

No additional Python packages required - uses Hermes built-in tools.

## Usage

### Command Line

```bash
# Basic search
python3 tcgplayer_lookup.py "Lightning Bolt"

# Set-specific search
python3 tcgplayer_lookup.py "Black Lotus" LEA

# Search with spaces in name
python3 tcgplayer_lookup.py "Thassa's Oracle"
```

### Programmatic Usage

```python
from tcgplayer_lookup import TCGPlayerPriceLookup

client = TCGPlayerPriceLookup()

# Search for a card
results = client.search_and_extract_prices("Lightning Bolt", "M15")

print(f"Found {len(results['prices'])} price points")
for p in results['prices']:
    print(f"  - ${p['price']:.2f}")
```

## Hermes Browser Tools Used

| Tool | Purpose |
|------|--------|
| `browser_navigate` | Navigate to TCGPlayer search page |
| `browser_snapshot` | Get text-based page representation |
| `browser_click` | Click on elements (e.g., filter buttons) |
| `browser_type` | Type into search box |
| `browser_press` | Press Enter to submit search |
| `browser_scroll` | Scroll for more results |
| `browser_close` | Clean up browser session |

## Output Format

The system returns a dictionary with:

```json
{
  "card_name": "Lightning Bolt",
  "set_code": "M15",
  "prices": [
    {
      "type": "market_price",
      "price": 1.25,
      "raw_text": "Market Price: $1.25"
    }
  ],
  "set_specific_price": {
    "card_name": "Lightning Bolt",
    "set_code": "M15",
    "price": 0.99
  }
}
```

## Integration with Pocket-Shop

This module integrates into the larger Pocket-Shop system:

```python
from tcgplayer_lookup import TCGPlayerPriceLookup

def get_card_price(card_name: str, set_code: str = None) -> float:
    """Get market price for a card."""
    client = TCGPlayerPriceLookup()
    results = client.search_and_extract_prices(card_name, set_code)
    
    # Prefer set-specific price
    if results.get('set_specific_price'):
        return results['set_specific_price']['price']
    
    # Fall back to first detected price
    if results.get('prices'):
        return results['prices'][0]['price']
    
    return 0.0
```

## Notes

- TCGPlayer pages load dynamically; includes delay for page rendering
- Price patterns may change as TCGPlayer updates their site
- For best results, use specific set codes when available
