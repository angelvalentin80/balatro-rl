"""
Debug utilities for timestamped print statements and debugging helpers
"""

import datetime


def timestamp() -> str:
    """
    Get current timestamp formatted as HH:MM:SS.mmm
    
    Returns:
        str: Formatted timestamp string
    """
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-3]  # Remove last 3 digits to get milliseconds


def tprint(*args, **kwargs):
    """
    Print with timestamp prefix
    
    Args:
        *args: Arguments to print
        **kwargs: Keyword arguments for print()
    """
    print(f"[{timestamp()}]", *args, **kwargs)


def dprint(prefix: str, *args, **kwargs):
    """
    Debug print with custom prefix and timestamp
    
    Args:
        prefix: Custom prefix string
        *args: Arguments to print  
        **kwargs: Keyword arguments for print()
    """
    print(f"[{timestamp()}] [{prefix}]", *args, **kwargs)