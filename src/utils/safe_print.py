"""
Safe Print Utility for Cross-Platform Console Output

Handles Unicode emoji encoding issues on Windows console (cp1252 codec).
Provides fallback ASCII representations when Unicode characters fail.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Emoji to ASCII fallback mapping
EMOJI_FALLBACK = {
    '🧠': '[CORTEX]',
    '🔧': '[MAINT]',
    '📊': '[STATS]',
    '✅': '[OK]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '💾': '[SAVE]',
    '📄': '[FILE]',
    '🔍': '[SCAN]',
    '📂': '[DIR]',
    '🔎': '[SEARCH]',
    '💬': '[RESP]',
    '🎯': '[TARGET]',
    '⚡': '[FAST]',
    '🗑️': '[DELETE]',
    '🔄': '[UPDATE]',
    '📁': '[FOLDER]',
    '🧹': '[CLEAN]',
    '💡': '[INFO]',
    '🚀': '[LAUNCH]',
    '🏭': '[BUILD]',
    '⏳': '[WAIT]',
    '⏭️': '[SKIP]',
}


def safe_print(message: str, fallback_emoji: bool = True, file=None) -> None:
    """
    Print message with emoji fallback for Windows console.
    
    Args:
        message: Message to print (may contain emojis)
        fallback_emoji: If True, replace emojis with ASCII on encoding errors
        file: Output file (default: sys.stdout)
    
    Example:
        safe_print("✅ Test passed")  # Prints "[OK] Test passed" on Windows
    """
    if file is None:
        file = sys.stdout
    
    try:
        print(message, file=file)
    except UnicodeEncodeError:
        if fallback_emoji:
            # Replace emojis with ASCII equivalents
            safe_message = message
            for emoji, ascii_rep in EMOJI_FALLBACK.items():
                safe_message = safe_message.replace(emoji, ascii_rep)
            
            try:
                print(safe_message, file=file)
            except Exception as e:
                # Last resort: strip all non-ASCII
                ascii_only = ''.join(char for char in message if ord(char) < 128)
                print(f"[ENCODING ERROR] {ascii_only}", file=file)
                logger.debug(f"Failed to print message: {e}")
        else:
            # Strip emojis entirely
            ascii_only = ''.join(char for char in message if ord(char) < 128)
            print(ascii_only, file=file)


def supports_unicode() -> bool:
    """
    Check if current console supports Unicode emojis.
    
    Returns:
        True if Unicode emojis are supported, False otherwise
    """
    try:
        # Try encoding a test emoji
        test = "✅"
        sys.stdout.buffer.write(test.encode(sys.stdout.encoding))
        return True
    except (UnicodeEncodeError, AttributeError):
        return False


def get_emoji_style() -> str:
    """
    Get emoji style based on console support.
    
    Returns:
        'unicode' if emojis supported, 'ascii' otherwise
    """
    return 'unicode' if supports_unicode() else 'ascii'


def format_status(status: str, use_emoji: Optional[bool] = None) -> str:
    """
    Format status with appropriate symbol.
    
    Args:
        status: Status string ('success', 'error', 'warning', 'info')
        use_emoji: Force emoji usage (None = auto-detect)
    
    Returns:
        Formatted status with symbol prefix
    """
    if use_emoji is None:
        use_emoji = supports_unicode()
    
    if use_emoji:
        symbols = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': '💡',
            'processing': '⏳',
        }
    else:
        symbols = {
            'success': '[OK]',
            'error': '[FAIL]',
            'warning': '[WARN]',
            'info': '[INFO]',
            'processing': '[WAIT]',
        }
    
    symbol = symbols.get(status.lower(), '[?]')
    return f"{symbol} {status}"


__all__ = ['safe_print', 'supports_unicode', 'get_emoji_style', 'format_status', 'EMOJI_FALLBACK']
