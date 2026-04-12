#!/usr/bin/env python3
"""Test the fixed vulnerability scanner."""

import json
from pathlib import Path
from deepseek_code.dependencies.analyzer import DependencyAnalyzer
from deepseek_code.dependencies.security_fixed import FixedVulnerabilityScanner


def main():
    print("🔍 Testing Fixed Vulnerability Scanner")
    print("=" * 60)
    
    # Analyze dependencies
    analyzer = DependencyAnalyzer(Path.cwd())
    report = analyzer.analyze_python()
    deps = report.dependencies
    
    print(f"Found {len(deps)} Python dependencies")
    
    # Scan for vulnerabilities with fixed scanner
    scanner = FixedVulnerabilityScanner()
    result = scanner.scan_dependencies(deps)
    
    print(f"\n📊 Scan Results:")
    print(f"  Dependencies scanned: {result.dependencies_scanned}")
    print(f"  Vulnerabilities found: {result.vulnerabilities_found}")
    print(f"  Critical: {result.critical_vulnerabilities}")
    print(f"  High: {result.high_vulnerabilities}")
    print(f"  Medium: {result.medium_vulnerabilities}")
    print(f"  Low: {result.low_vulnerabilities}")
    
    if result.vulnerabilities_found > 0:
        print(f"\n⚠️  Vulnerabilities found:")
        for dep_name, vulns in result.vulnerabilities_by_dependency.items():
            if vulns:
                print(f"\n  {dep_name}:")
                for vuln in vulns:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(vuln.severity, "⚪")
                    
                    print(f"    {severity_emoji} {vuln.id} ({vuln.severity})")
                    print(f"      Description: {vuln.description[:150]}...")
                    if vuln.affected_versions != "Unknown":
                        print(f"      Affected: {vuln.affected_versions}")
    else:
        print("\n✅ No vulnerabilities found!")
    
    # Compare with old scanner
    print("\n" + "=" * 60)
    print("🔄 Comparison with old scanner:")
    
    try:
        from deepseek_code.dependencies.security import VulnerabilityScanner
        
        old_scanner = VulnerabilityScanner()
        old_result = old_scanner.scan_dependencies(deps)
        
        print(f"  Old scanner found: {old_result.vulnerabilities_found} vulnerabilities")
        print(f"  Fixed scanner found: {result.vulnerabilities_found} vulnerabilities")
        
        if old_result.vulnerabilities_found > result.vulnerabilities_found:
            reduction = ((old_result.vulnerabilities_found - result.vulnerabilities_found) / 
                        old_result.vulnerabilities_found * 100)
            print(f"  ✅ False positives reduced by: {reduction:.1f}%")
        else:
            print(f"  ⚠️  No reduction in false positives")
            
    except Exception as e:
        print(f"  Could not compare with old scanner: {e}")
    
    # Test with specific packages
    print("\n" + "=" * 60)
    print("🧪 Testing specific packages:")
    
    test_packages = ["requests", "pyyaml", "pydantic", "black", "openai"]
    
    for package in test_packages:
        # Find the dependency
        dep = next((d for d in deps if d.name == package), None)
        if dep:
            vulns = scanner._scan_dependency(dep)
            if vulns:
                print(f"  {package}: {len(vulns)} vulnerabilities")
                for vuln in vulns[:2]:  # Show first 2
                    print(f"    - {vuln.id}: {vuln.severity}")
            else:
                print(f"  {package}: No vulnerabilities")
        else:
            print(f"  {package}: Not found in dependencies")
    
    print("\n" + "=" * 60)
    print("✅ Fixed scanner test completed!")


if __name__ == "__main__":
    main()