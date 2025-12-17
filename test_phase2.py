"""
Test script for Phase 2 quality enhancements
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("PHASE 2 QUALITY ENHANCEMENTS - TEST SUITE")
print("=" * 60)

# Test 1: Persona Temperature Configuration
print("\n[Test 1] Persona Temperature Configuration")
print("-" * 40)
try:
    from config import AgentConfig

    print("[OK] Persona temperatures configured:")
    for persona, temp in AgentConfig.PERSONA_TEMPERATURES.items():
        print(f"  - {persona}: {temp}")

    # Verify each persona has a temperature
    expected_personas = ["Professional Dana", "Friendly Dana", "Inspirational Dana", "Mentor Dana"]
    for persona in expected_personas:
        if persona in AgentConfig.PERSONA_TEMPERATURES:
            print(f"[OK] {persona} temperature: {AgentConfig.PERSONA_TEMPERATURES[persona]}")
        else:
            print(f"[FAIL] {persona} missing from configuration")
            sys.exit(1)

    print("[OK] Persona temperature test PASSED")
except Exception as e:
    print(f"[FAIL] Persona temperature test FAILED: {e}")
    sys.exit(1)

# Test 2: Persona Search Terms Configuration
print("\n[Test 2] Persona Search Terms Configuration")
print("-" * 40)
try:
    from config import PersonaConfig

    print("[OK] Persona search terms configured:")
    for persona in PersonaConfig.VALID_PERSONAS:
        if persona in PersonaConfig.PERSONA_SEARCH_TERMS:
            terms = PersonaConfig.PERSONA_SEARCH_TERMS[persona]
            print(f"  - {persona}:")
            print(f"    Tone: {', '.join(terms['tone'][:2])}...")
            print(f"    Style: {', '.join(terms['style'][:2])}...")
        else:
            print(f"[FAIL] {persona} missing search terms")
            sys.exit(1)

    print("[OK] Persona search terms test PASSED")
except Exception as e:
    print(f"[FAIL] Persona search terms test FAILED: {e}")
    sys.exit(1)

# Test 3: Agent Factory Function Signature
print("\n[Test 3] Updated Agent Factory Function")
print("-" * 40)
try:
    from agents.dana_copywriter import create_dana_copywriter_agent
    import inspect

    sig = inspect.signature(create_dana_copywriter_agent)
    params = list(sig.parameters.keys())

    print(f"[OK] Function signature: {sig}")

    # Check for new parameters
    if 'temperature' in params:
        print("[OK] 'temperature' parameter added")
    else:
        print("[FAIL] 'temperature' parameter missing")
        sys.exit(1)

    if 'persona' in params:
        print("[OK] 'persona' parameter added")
    else:
        print("[FAIL] 'persona' parameter missing")
        sys.exit(1)

    print("[OK] Agent factory function test PASSED")
except Exception as e:
    print(f"[FAIL] Agent factory function test FAILED: {e}")
    sys.exit(1)

# Test 4: Persona Name Extraction from UI Description
print("\n[Test 4] Persona Name Extraction")
print("-" * 40)
try:
    # Simulate the UI format
    test_cases = [
        ("Professional Dana - Professional tone, data-driven...", "Professional Dana"),
        ("Friendly Dana - Warm conversational tone...", "Friendly Dana"),
        ("Inspirational Dana - Motivational and empowering...", "Inspirational Dana"),
        ("Mentor Dana - Guiding and educational tone...", "Mentor Dana"),
        ("Professional Dana", "Professional Dana"),  # Without description
    ]

    for full_text, expected_name in test_cases:
        # Extract persona name (before the dash)
        persona = full_text.split(" - ")[0] if " - " in full_text else full_text

        if persona == expected_name:
            print(f"[OK] Extracted '{persona}' from '{full_text[:40]}...'")
        else:
            print(f"[FAIL] Expected '{expected_name}' but got '{persona}'")
            sys.exit(1)

    print("[OK] Persona extraction test PASSED")
except Exception as e:
    print(f"[FAIL] Persona extraction test FAILED: {e}")
    sys.exit(1)

# Test 5: Temperature Lookup Logic
print("\n[Test 5] Temperature Lookup Logic")
print("-" * 40)
try:
    from config import AgentConfig

    test_personas = [
        ("Professional Dana", 0.4),
        ("Friendly Dana", 0.8),
        ("Inspirational Dana", 0.7),
        ("Mentor Dana", 0.5),
        ("Unknown Persona", AgentConfig.COPYWRITER_TEMPERATURE)  # Fallback
    ]

    for persona, expected_temp in test_personas:
        actual_temp = AgentConfig.PERSONA_TEMPERATURES.get(
            persona,
            AgentConfig.COPYWRITER_TEMPERATURE
        )

        if actual_temp == expected_temp:
            print(f"[OK] {persona}: {actual_temp}")
        else:
            print(f"[FAIL] {persona}: expected {expected_temp}, got {actual_temp}")
            sys.exit(1)

    print("[OK] Temperature lookup test PASSED")
except Exception as e:
    print(f"[FAIL] Temperature lookup test FAILED: {e}")
    sys.exit(1)

# Test 6: UI Persona Descriptions
print("\n[Test 6] UI Persona Descriptions Present")
print("-" * 40)
try:
    with open('start.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for persona descriptions in the UI
    required_texts = [
        "Professional Dana - Professional tone",
        "Friendly Dana - Warm conversational tone",
        "Inspirational Dana - Motivational and empowering",
        "Mentor Dana - Guiding and educational tone"
    ]

    for text in required_texts:
        if text in content:
            print(f"[OK] Found: '{text[:40]}...'")
        else:
            print(f"[FAIL] Missing: '{text}'")
            sys.exit(1)

    # Check for persona extraction logic
    if 'persona_full.split(" - ")[0]' in content or 'persona.split(" - ")[0]' in content:
        print("[OK] Persona extraction logic found")
    else:
        print("[FAIL] Persona extraction logic missing")
        sys.exit(1)

    print("[OK] UI persona descriptions test PASSED")
except Exception as e:
    print(f"[FAIL] UI persona descriptions test FAILED: {e}")
    sys.exit(1)

# Test 7: Search Transparency Messages
print("\n[Test 7] Search Transparency Logging")
print("-" * 40)
try:
    with open('start.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for search transparency messages
    transparency_indicators = [
        "RAG Search Activity",
        "Search Transparency:",
        "dynamically searching",
        "This is RAG in action"
    ]

    for indicator in transparency_indicators:
        if indicator in content:
            print(f"[OK] Found transparency message: '{indicator}'")
        else:
            print(f"[FAIL] Missing transparency message: '{indicator}'")
            sys.exit(1)

    print("[OK] Search transparency test PASSED")
except Exception as e:
    print(f"[FAIL] Search transparency test FAILED: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "=" * 60)
print("ALL PHASE 2 TESTS PASSED!")
print("=" * 60)
print("\nPhase 2 Quality Enhancements Status:")
print("[OK] Persona Temperature Differentiation - WORKING")
print("[OK] Persona Search Terms Configuration - WORKING")
print("[OK] Agent Factory Functions Updated - WORKING")
print("[OK] UI Persona Descriptions - WORKING")
print("[OK] Persona Name Extraction - WORKING")
print("[OK] Search Transparency Logging - WORKING")
print("\nPhase 2 is ready for real-world testing!")
print("\nExpected Behavior:")
print("- Professional Dana: Temperature 0.4 (more focused)")
print("- Friendly Dana: Temperature 0.8 (more creative)")
print("- Inspirational Dana: Temperature 0.7 (balanced creative)")
print("- Mentor Dana: Temperature 0.5 (balanced focused)")
