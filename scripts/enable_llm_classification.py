#!/usr/bin/env python3
"""
CORTEX LLM Intent Classification - Quick Activation Script

Enables LLM-based intent classification by updating cortex.config.json.
Verifies API key is set before enabling.

Usage:
    python scripts/enable_llm_classification.py
    python scripts/enable_llm_classification.py --disable
    python scripts/enable_llm_classification.py --provider anthropic
"""

import json
import os
import sys
from pathlib import Path


def check_api_key(provider: str) -> bool:
    """Check if API key is set in environment."""
    if provider == 'openai':
        key = os.getenv('OPENAI_API_KEY')
        env_var = 'OPENAI_API_KEY'
    elif provider == 'anthropic':
        key = os.getenv('ANTHROPIC_API_KEY')
        env_var = 'ANTHROPIC_API_KEY'
    else:
        print(f"❌ Unknown provider: {provider}")
        return False
    
    if not key:
        print(f"❌ {env_var} not set in environment")
        print(f"\nTo fix:")
        print(f"  export {env_var}='your-api-key-here'")
        return False
    
    print(f"✅ {env_var} found: {key[:10]}...")
    return True


def update_config(enable: bool, provider: str = 'openai'):
    """Update cortex.config.json to enable/disable LLM intent routing."""
    config_path = Path('cortex.config.json')
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    # Ensure llm_intent_routing section exists
    if 'llm_intent_routing' not in config:
        print("❌ llm_intent_routing section not found in config")
        print("   Run: git pull  # to get latest config")
        return False
    
    # Update settings
    old_enabled = config['llm_intent_routing'].get('enabled', False)
    old_provider = config['llm_intent_routing'].get('provider', 'openai')
    
    config['llm_intent_routing']['enabled'] = enable
    if enable:
        config['llm_intent_routing']['provider'] = provider
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Print status
    print(f"\n{'='*60}")
    if enable:
        print(f"✅ LLM Intent Classification ENABLED")
        print(f"   Provider: {provider}")
        print(f"   Model: {config['llm_intent_routing'].get('model', 'unknown')}")
        if old_provider != provider:
            print(f"   Changed: {old_provider} → {provider}")
    else:
        print(f"⚠️  LLM Intent Classification DISABLED")
        print(f"   Falling back to regex-based classification")
    print(f"{'='*60}\n")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enable/disable LLM intent classification'
    )
    parser.add_argument(
        '--disable',
        action='store_true',
        help='Disable LLM classification (use regex fallback)'
    )
    parser.add_argument(
        '--provider',
        choices=['openai', 'anthropic'],
        default='openai',
        help='LLM provider (default: openai)'
    )
    
    args = parser.parse_args()
    
    print("🧠 CORTEX LLM Intent Classification Setup")
    print(f"Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX\n")
    
    if args.disable:
        # Disable LLM
        if update_config(enable=False):
            print("ℹ️  To re-enable: python scripts/enable_llm_classification.py")
            return 0
        return 1
    
    # Enable LLM
    print(f"Provider: {args.provider}")
    
    # Check API key
    if not check_api_key(args.provider):
        print("\nSee: cortex-brain/documents/implementation-guides/LLM-INTENT-SETUP.md")
        return 1
    
    # Update config
    if update_config(enable=True, provider=args.provider):
        print("📊 Performance:")
        print("   - Keyword matches: <10ms (40% of requests)")
        print("   - Cache hits: <50ms (30% of requests)")
        print("   - LLM calls: 100-500ms (30% of requests)")
        print(f"\n💰 Cost: ~$6.30/month (GPT-3.5) or ~$3.30/month (Claude)")
        print(f"\n📖 Docs: cortex-brain/documents/implementation-guides/LLM-INTENT-SETUP.md")
        return 0
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
