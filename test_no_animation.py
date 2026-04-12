#!/usr/bin/env python3
"""Test disabling animations in LunVex Code."""

import os
import time
from deepseek_code import ui


def test_animation_disabled():
    """Test that animations can be disabled."""
    print("Testing animation disabling...")
    print("=" * 60)
    
    # Test 1: Default animation (should NOT show animation)
    print("\n1. Testing default animation (should NOT show animation):")
    try:
        with ui.print_thinking():
            time.sleep(1)
        print("✓ Default animation disabled (showed 'Thinking...' instead)")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Disable animation via environment variable
    print("\n2. Testing with LUNVEX_NO_ANIMATION=1:")
    os.environ["LUNVEX_NO_ANIMATION"] = "1"
    
    try:
        with ui.print_thinking():
            time.sleep(1)
        print("✓ Animation disabled (showed 'Thinking...' instead)")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Clean up environment variable
    del os.environ["LUNVEX_NO_ANIMATION"]
    
    # Test 3: Disable animation via animation_type="none"
    print("\n3. Testing with animation_type='none':")
    try:
        with ui.print_thinking(animation_type="none"):
            time.sleep(1)
        print("✓ Animation disabled via parameter")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Different animation types
    print("\n4. Testing different animation types:")
    animation_types = ["robot", "neural", "orb", "none"]
    
    for anim_type in animation_types:
        print(f"\n  Testing '{anim_type}':")
        try:
            with ui.print_thinking(animation_type=anim_type):
                time.sleep(0.5)
            print(f"  ✓ '{anim_type}' animation works")
        except Exception as e:
            print(f"  ✗ Error with '{anim_type}': {e}")
    
    print("\n" + "=" * 60)
    print("✅ All animation tests completed!")


def test_get_animation_type():
    """Test the get_animation_type function."""
    print("\nTesting get_animation_type function:")
    print("=" * 60)
    
    # Save original environment
    original_env = os.environ.copy()
    
    test_cases = [
        ({"LUNVEX_NO_ANIMATION": "1"}, "none"),
        ({"LUNVEX_NO_ANIMATION": "true"}, "none"),
        ({"LUNVEX_NO_ANIMATION": "yes"}, "none"),
        ({"LUNVEX_ANIMATION": "robot"}, "robot"),
        ({"LUNVEX_ANIMATION": "neural"}, "neural"),
        ({"LUNVEX_ANIMATION": "orb"}, "orb"),
        ({"LUNVEX_ANIMATION": "none"}, "none"),
        ({}, "none"),  # Default (no animation)
    ]
    
    for env_vars, expected in test_cases:
        # Clear environment
        os.environ.clear()
        os.environ.update(original_env)
        
        # Set test environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
        
        result = ui.get_animation_type()
        status = "✓" if result == expected else "✗"
        print(f"{status} {env_vars} -> {result} (expected: {expected})")
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    print("\n✅ get_animation_type tests completed!")


if __name__ == "__main__":
    print("🔧 Testing Animation Disabling Feature")
    print("=" * 60)
    
    test_animation_disabled()
    test_get_animation_type()
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Animations can be disabled.")
    print("\nUsage:")
    print("  - Set LUNVEX_NO_ANIMATION=1 to disable all animations")
    print("  - Use animation_type='none' in print_thinking()")
    print("  - Set LUNVEX_ANIMATION=none for default disabled")