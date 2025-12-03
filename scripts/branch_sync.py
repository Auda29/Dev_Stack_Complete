#!/usr/bin/env python3
"""
Branch Sync - Automatically fetch new feature branches from origin

This script periodically fetches from origin so your local Git
repository knows about feature branches created by the DevOps agent.

Usage:
    python scripts/branch_sync.py [--interval 60]
    
Or run once:
    python scripts/branch_sync.py --once
"""

import subprocess
import time
import argparse
from datetime import datetime


def fetch_branches():
    """Fetch all branches from origin."""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Fetching from origin...")
        
        result = subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if new branches were fetched
        if result.stderr:  # Git fetch outputs to stderr
            print(result.stderr.strip())
        else:
            print("✅ Up to date")
        
        # List all remote feature branches
        result = subprocess.run(
            ["git", "branch", "-r", "--list", "origin/feature/*"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            branches = result.stdout.strip().split('\n')
            print(f"\n📋 Available feature branches ({len(branches)}):")
            for branch in branches[:5]:  # Show first 5
                print(f"   {branch.strip()}")
            if len(branches) > 5:
                print(f"   ... and {len(branches) - 5} more")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error fetching: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sync feature branches from origin")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Fetch interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Fetch once and exit"
    )
    
    args = parser.parse_args()
    
    if args.once:
        fetch_branches()
        return
    
    print(f"🔄 Branch Sync started (fetching every {args.interval}s)")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            fetch_branches()
            print(f"\n💤 Sleeping for {args.interval}s...\n")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\n👋 Branch Sync stopped")


if __name__ == "__main__":
    main()
