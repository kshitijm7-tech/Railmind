import os

base = r"d:\Projects\Railmind\frontend\domain\types"

files = {
    "defect.ts": """export * from '../../contracts/maintenance/defect';
""",
    "train-impact.ts": """export * from '../../contracts/operations/train-impact';
""",
    "recovery.ts": """export * from '../../contracts/disruption/recovery';
""",
    "operational-window.ts": """export * from '../../contracts/operations/operational-window';
""",
    "train-path.ts": """export * from '../../contracts/operations/train-path';
"""
}

for path, content in files.items():
    full_path = os.path.join(base, path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Created wrapper files.")
