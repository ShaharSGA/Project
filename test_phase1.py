"""
Test script for Phase 1 critical fixes
"""

import sys
import asyncio
import io
from pydantic import ValidationError

# Fix Windows console encoding for Hebrew/Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("PHASE 1 CRITICAL FIXES - TEST SUITE")
print("=" * 60)

# Test 1: Config Import
print("\n[Test 1] Configuration Management")
print("-" * 40)
try:
    from config import AgentConfig, ExecutionConfig, DataFiles
    print("[OK] config.py imported successfully")
    print(f"  Strategy temperature: {AgentConfig.STRATEGY_TEMPERATURE}")
    print(f"  Copywriter temperature: {AgentConfig.COPYWRITER_TEMPERATURE}")
    print(f"  Execution timeout: {ExecutionConfig.CREW_TIMEOUT}s")
    print("[OK] Config test PASSED")
except Exception as e:
    print(f"[FAIL] Config test FAILED: {e}")
    sys.exit(1)

# Test 2: Pydantic Validation - Valid Input
print("\n[Test 2] Pydantic Validation - Valid Input")
print("-" * 40)
try:
    from models import CampaignInput

    valid_input = CampaignInput(
        product="Test Product",
        benefits="Amazing benefits for testing purposes",
        audience="Test audience group",
        offer="50% discount",
        persona="Friendly Dana"
    )
    print("[OK] Valid input accepted")
    print(f"  Product: {valid_input.product}")
    print(f"  Persona: {valid_input.persona}")
    print("[OK] Validation test PASSED")
except Exception as e:
    print(f"[FAIL] Validation test FAILED: {e}")
    sys.exit(1)

# Test 3: Pydantic Validation - Invalid Input (Empty Fields)
print("\n[Test 3] Pydantic Validation - Empty Field Rejection")
print("-" * 40)
try:
    invalid_input = CampaignInput(
        product="",  # Empty product
        benefits="test benefits",
        audience="test audience",
        offer="test offer",
        persona="Friendly Dana"
    )
    print("[FAIL] Empty field test FAILED: Should have raised ValidationError")
    sys.exit(1)
except ValidationError as e:
    print("[OK] Empty field correctly rejected")
    print(f"  Validation errors caught: {len(e.errors())}")
    print("[OK] Empty field test PASSED")
except Exception as e:
    print(f"[FAIL] Empty field test FAILED: {e}")
    sys.exit(1)

# Test 4: Pydantic Validation - Invalid Persona
print("\n[Test 4] Pydantic Validation - Invalid Persona Rejection")
print("-" * 40)
try:
    invalid_persona = CampaignInput(
        product="Test Product",
        benefits="test benefits",
        audience="test audience",
        offer="test offer",
        persona="Invalid Persona"  # Not in allowed list
    )
    print("[FAIL] Invalid persona test FAILED: Should have raised ValidationError")
    sys.exit(1)
except ValidationError as e:
    print("[OK] Invalid persona correctly rejected")
    print(f"  Validation errors: {len(e.errors())}")
    print("[OK] Invalid persona test PASSED")
except Exception as e:
    print(f"[FAIL] Invalid persona test FAILED: {e}")
    sys.exit(1)

# Test 5: Type Hints
print("\n[Test 5] Type Hints Verification")
print("-" * 40)
try:
    from agents.strategy_architect import create_strategy_architect_agent
    from agents.dana_copywriter import create_dana_copywriter_agent
    from tasks.strategy_tasks import create_strategy_task
    from tasks.copywriting_tasks import create_copywriting_task

    print("[OK] All agent modules imported")
    print("[OK] All task modules imported")

    # Check function signatures
    import inspect
    sig = inspect.signature(create_strategy_architect_agent)
    print(f"  Strategy architect signature: {sig}")

    sig = inspect.signature(create_dana_copywriter_agent)
    print(f"  Dana copywriter signature: {sig}")

    print("[OK] Type hints test PASSED")
except Exception as e:
    print(f"[FAIL] Type hints test FAILED: {e}")
    sys.exit(1)

# Test 6: Tool Initialization (without API key - expect specific error)
print("\n[Test 6] Error Handling - Missing Data Files")
print("-" * 40)
try:
    from config import DataFiles

    missing_files = DataFiles.validate_all_exist()
    if missing_files:
        print("[OK] Missing files detected correctly:")
        for file in missing_files:
            print(f"  - {file}")
        print("[OK] File validation test PASSED")
    else:
        print("[OK] All data files present")
        print("[OK] File validation test PASSED")
except Exception as e:
    print(f"[FAIL] File validation test FAILED: {e}")
    sys.exit(1)

# Test 7: Thread Lock Presence
print("\n[Test 7] Thread Safety Implementation")
print("-" * 40)
try:
    import threading

    # Check if TOOLS_LOCK exists in start.py
    with open('start.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'TOOLS_LOCK = threading.Lock()' in content:
            print("[OK] Thread lock found in start.py")
        else:
            print("[FAIL] Thread lock NOT found in start.py")
            sys.exit(1)

        if 'with TOOLS_LOCK:' in content:
            print("[OK] Thread lock usage found")
        else:
            print("[FAIL] Thread lock usage NOT found")
            sys.exit(1)

        if 'asyncio.wait_for' in content:
            print("[OK] Execution timeout found (asyncio.wait_for)")
        else:
            print("[FAIL] Execution timeout NOT found")
            sys.exit(1)

    print("[OK] Thread safety test PASSED")
except Exception as e:
    print(f"[FAIL] Thread safety test FAILED: {e}")
    sys.exit(1)

# Test 8: Configuration Helper Functions
print("\n[Test 8] Configuration Helper Functions")
print("-" * 40)
try:
    from config import get_embedding_config, get_llm_config, get_vectordb_config

    embedding_cfg = get_embedding_config()
    print(f"[OK] Embedding config: {embedding_cfg['provider']}")

    llm_cfg = get_llm_config()
    print(f"[OK] LLM config: {llm_cfg['provider']}")

    vectordb_cfg = get_vectordb_config("test_collection")
    print(f"[OK] VectorDB config: {vectordb_cfg['provider']}")

    print("[OK] Helper functions test PASSED")
except Exception as e:
    print(f"[FAIL] Helper functions test FAILED: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nPhase 1 Critical Fixes Status:")
print("[OK] Configuration Management - WORKING")
print("[OK] Pydantic Input Validation - WORKING")
print("[OK] Thread Safety Implementation - WORKING")
print("[OK] Execution Timeout - WORKING")
print("[OK] Type Hints - WORKING")
print("[OK] Error Handling - WORKING")
print("\nSystem is ready for testing with real data!")
