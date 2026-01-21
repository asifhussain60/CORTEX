#!/usr/bin/env python3
"""Rollback script for folder structure migration."""

def rollback():
    """Rollback migration (no-op - structure is intentional)."""
    print("Migration structure is intentional. No rollback needed.")
    print("cortex_brain/ preserved as Tier0/1/2/3 governance structure.")
    return True

if __name__ == "__main__":
    rollback()
