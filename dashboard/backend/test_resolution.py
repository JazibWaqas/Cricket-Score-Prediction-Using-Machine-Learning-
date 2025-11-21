import re

def resolve_model_identifier(identifier, available_keys):
    print(f"Resolving: '{identifier}'")
    if not identifier:
        return identifier
        
    lookup = identifier.lower().replace(' ', '_')
    print(f"  Lookup: '{lookup}'")
    
    for key in available_keys:
        # Original logic from app.py
        # re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower().replace(' ', '_')
        
        step1 = re.sub(r'(?<!^)(?=[A-Z])', '_', key)
        step2 = step1.lower()
        key_normalized = step2.replace(' ', '_')
        
        print(f"  Checking key '{key}':")
        print(f"    Step 1 (Regex): '{step1}'")
        print(f"    Step 2 (Lower): '{step2}'")
        print(f"    Normalized:     '{key_normalized}'")
        
        if key_normalized == lookup:
            print(f"  MATCH FOUND: '{key}'")
            return key
            
    print("  NO MATCH. Returning original.")
    return identifier

keys = ['XGBoost', 'Random Forest']
print("--- Test 1: random_forest ---")
resolve_model_identifier('random_forest', keys)

print("\n--- Test 2: xgboost ---")
resolve_model_identifier('xgboost', keys)
