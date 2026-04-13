#!/usr/bin/env python3
"""Simple test to verify the configuration."""

import os

import tomli

print("Testing LunVex Code async default configuration...")
print("=" * 60)

# 1. Check pyproject.toml
print("\n1. Checking pyproject.toml...")
with open("pyproject.toml", "rb") as f:
    config = tomli.load(f)

scripts = config.get("project", {}).get("scripts", {})
print(f"   Found scripts: {list(scripts.keys())}")

if "lunvex-code" in scripts:
    entry_point = scripts["lunvex-code"]
    print(f"   lunvex-code entry point: {entry_point}")

    if "main:main" in entry_point:
        print("   ✓ Entry point correctly points to main.py (async version)")
    else:
        print(f"   ✗ Entry point should point to main.py, but points to: {entry_point}")
else:
    print("   ✗ lunvex-code script not found in pyproject.toml")

# 2. Check if main.py exists
print("\n2. Checking if main.py exists...")
if os.path.exists("lunvex_code/main.py"):
    print("   ✓ main.py exists")

    # Check if it's the async version
    with open("lunvex_code/main.py", "r") as f:
        content = f.read()
        if "async def main()" in content and "AsyncAgent" in content:
            print("   ✓ main.py contains async implementation")
        else:
            print("   ✗ main.py doesn't appear to be async")
else:
    print("   ✗ main.py not found")

# 3. Check async_agent.py for planning default
print("\n3. Checking async_agent.py for planning default...")
if os.path.exists("lunvex_code/async_agent.py"):
    with open("lunvex_code/async_agent.py", "r") as f:
        content = f.read()
        if "use_planning: bool = True" in content:
            print("   ✓ async_agent.run() has use_planning=True by default")
        else:
            print("   ✗ async_agent.run() doesn't have use_planning=True by default")

        if "In async mode, planning is always used by default" in content:
            print("   ✓ Comment confirms planning is default in async mode")
        else:
            print("   ✗ Missing comment about planning default")
else:
    print("   ✗ async_agent.py not found")

# 4. Check task_planner.py for async optimizations
print("\n4. Checking task_planner.py for async optimizations...")
if os.path.exists("lunvex_code/task_planner.py"):
    with open("lunvex_code/task_planner.py", "r") as f:
        content = f.read()
        if "execute_plan_async" in content:
            print("   ✓ execute_plan_async method exists")

            # Check for parallel execution
            if "asyncio.wait" in content and "FIRST_COMPLETED" in content:
                print("   ✓ Supports parallel execution of independent subtasks")
            else:
                print("   ✗ Doesn't appear to support parallel execution")
        else:
            print("   ✗ execute_plan_async method not found")
else:
    print("   ✗ task_planner.py not found")

print("\n" + "=" * 60)
print("Summary: Async mode with automatic subtask planning should now be the default.")
print("Run: lunvex-code --help to see new options")
print("=" * 60)
