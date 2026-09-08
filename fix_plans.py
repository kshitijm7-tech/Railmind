import os
import re

base = r'd:\Projects\Railmind\frontend\domain\types\plans.ts'
with open(base, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("export type PlanStatus = 'Draft' | 'Optimizing' | 'Recommended' | 'Generated' | 'Published' | 'Active' | 'Archived';\n", '')
with open(base, 'w', encoding='utf-8') as f:
    f.write(content)

base = r'd:\Projects\Railmind\frontend\services\mock\mockServices.ts'
with open(base, 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'created_at:\s*new Date\(\)\.toISOString\(\)', r'created_at: new Date().toISOString() as any', content)
with open(base, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed.")
