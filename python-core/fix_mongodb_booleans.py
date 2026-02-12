#!/usr/bin/env python3
"""
Fix MongoDB boolean checks in Stage 4 modules.
Replaces unsafe 'if not obj:' with 'if obj is None:' for MongoDB objects.
"""

import os
import re

files_to_fix = [
    "e:\\Projects\\ELIXI AI\\python-core\\automation\\custom_commands.py",
    "e:\\Projects\\ELIXI AI\\python-core\\automation\\workflows.py",
    "e:\\Projects\\ELIXI AI\\python-core\\automation\\habit_learning.py",
    "e:\\Projects\\ELIXI AI\\python-core\\automation\\suggestion_engine.py",
]

replacements = [
    (r'if not collection:', 'if collection is None:'),
    (r'if not db:', 'if db is None:'),
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✓ Fixed {os.path.basename(filepath)}")
        else:
            print(f"- No changes needed for {os.path.basename(filepath)}")
    else:
        print(f"✗ File not found: {filepath}")

print("\nAll MongoDB boolean checks fixed!")
