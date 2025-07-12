#!/usr/bin/env python3
"""
Security Audit Script
====================

Runs a comprehensive security audit of the cover letter agent setup.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.security import validate_secrets, get_security_manager, get_environment_config


def run_security_audit():
    """Run a comprehensive security audit."""
    print("🔒 Cover Letter Agent Security Audit")
    print("=" * 50)

    # Get security components
    security_manager = get_security_manager()
    env_config = get_environment_config()

    # Run validation
    results = validate_secrets()

    # Display results
    print(f"\n📊 Overall Security Score: {results['overall_score']}/100")

    # Environment configuration
    print("\n🔧 Environment Configuration:")
    env_results = results["environment_config"]
    if env_results["valid"]:
        print("  ✅ Environment configuration is valid")
    else:
        print("  ❌ Environment configuration has issues:")
        for issue in env_results["issues"]:
            print(f"    - {issue}")

    # File permissions
    print("\n📁 File Permissions:")
    perm_results = results["file_permissions"]
    if perm_results["secure"]:
        print("  ✅ Critical files have secure permissions")
    else:
        print("  ❌ Insecure file permissions found:")
        for issue in perm_results["issues"]:
            print(f"    - {issue}")

    # Secrets audit
    print("\n🔍 Secrets Audit:")
    audit_results = results["audit_results"]
    print(f"  📂 Files scanned: {audit_results['files_scanned']}")

    if audit_results["secrets_found"]:
        print("  ⚠️  Potential secrets found in code:")
        for secret in audit_results["secrets_found"]:
            print(f"    - {secret['type']}: {secret['value']} in {secret['file']}:{secret['line']}")
    else:
        print("  ✅ No hardcoded secrets found")

    # Recommendations
    print("\n💡 Security Recommendations:")

    if results["overall_score"] >= 90:
        print("  ✅ Excellent security posture!")
    elif results["overall_score"] >= 70:
        print("  ⚠️  Good security, but room for improvement:")
        print("    - Review any found secrets and remove them")
        print("    - Fix file permissions on critical files")
    else:
        print("  ❌ Security issues need immediate attention:")
        print("    - Remove all hardcoded secrets")
        print("    - Fix file permissions")
        print("    - Review environment configuration")

    # Environment setup guide
    print("\n📋 Environment Setup:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your OpenAI API key to .env")
    print("  3. Set secure file permissions: chmod 600 .env")
    print("  4. Run this audit again to verify")

    return results["overall_score"] >= 70


def main():
    """Main function."""
    try:
        success = run_security_audit()
        if success:
            print("\n✅ Security audit completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Security audit found issues that need attention")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Security audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
