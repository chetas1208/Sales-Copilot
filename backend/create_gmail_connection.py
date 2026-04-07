#!/usr/bin/env python3
"""
Create Gmail Connection for a Specific User
Generates authorization link for Gmail integration
"""

import os
import sys
from dotenv import load_dotenv
from scalekit import ScalekitClient

# Load environment variables
load_dotenv()

def main():
    print("=" * 70)
    print("Meetstream AI - Gmail Connection Setup")
    print("=" * 70)
    print()

    # Get user identifier
    print("Enter the identifier for this Gmail connection.")
    print("This could be:")
    print("  - Your email address (e.g., jeet@example.com)")
    print("  - A user ID from your database (e.g., user_123)")
    print("  - Any unique identifier for this user")
    print()

    identifier = input("Identifier: ").strip()

    if not identifier:
        print("❌ ERROR: Identifier cannot be empty")
        sys.exit(1)

    print()
    print(f"Creating Gmail connection for: {identifier}")
    print()

    # Load credentials
    env_url = os.getenv("SCALEKIT_ENVIRONMENT_URL")
    client_id = os.getenv("SCALEKIT_CLIENT_ID")
    client_secret = os.getenv("SCALEKIT_CLIENT_SECRET")

    if not all([env_url, client_id, client_secret]):
        print("❌ ERROR: Missing Scalekit credentials in .env file")
        sys.exit(1)

    # Initialize Scalekit client
    print("Initializing Scalekit client...")
    try:
        client = ScalekitClient(
            env_url=env_url,
            client_id=client_id,
            client_secret=client_secret
        )
        print("✓ Scalekit client initialized")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)
    print()

    # Create or get connected account
    connection_name = "gmail"
    print(f"Getting or creating connected account...")
    try:
        response = client.actions.get_or_create_connected_account(
            connection_name=connection_name,
            identifier=identifier
        )

        connected_account = response.connected_account
        print(f"✓ Connected account created/retrieved")
        print(f"  Account ID: {connected_account.id}")
        print(f"  Status: {connected_account.status}")
        print()

        # Check if already active
        if connected_account.status == "ACTIVE":
            print("=" * 70)
            print("✅ This account is already authorized!")
            print("=" * 70)
            print()
            print("Your Gmail is already connected and ready to use.")
            print("You can now integrate this into your agentic flow.")
            sys.exit(0)

        # Get authorization link
        print("Generating authorization link...")
        try:
            magic_link_response = client.actions.get_authorization_link(
                connection_name=connection_name,
                identifier=identifier
            )
            auth_url = magic_link_response.link
        except Exception as e:
            print(f"❌ ERROR generating link: {str(e)}")
            sys.exit(1)

        print()
        print("=" * 70)
        print("🔗 AUTHORIZATION LINK GENERATED")
        print("=" * 70)
        print()
        print("Click the link below to authorize Gmail access:")
        print()
        print(f"👉 {auth_url}")
        print()
        print("Steps:")
        print("1. Click the link above (Command+Click in most terminals)")
        print("2. Sign in with the Gmail account you want to connect")
        print("3. Review and grant the requested permissions")
        print("4. After authorization, run this script again to verify")
        print()
        print(f"To verify later, run:")
        print(f"  python3 test_scalekit_tool_proxy.py")
        print()
        print("=" * 70)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
