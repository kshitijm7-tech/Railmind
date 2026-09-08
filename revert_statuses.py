import os

base_dir = r'd:\Projects\Railmind\frontend\domain\types'

# blocks.ts
with open(os.path.join(base_dir, 'blocks.ts'), 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("import { BlockStatus } from '../../contracts/planning/block';\n", '')
content = "export type BlockStatus = 'Requested' | 'Approved' | 'Active' | 'Completed' | 'Overrun' | 'Cancelled';\n" + content
with open(os.path.join(base_dir, 'blocks.ts'), 'w', encoding='utf-8') as f:
    f.write(content)

# plans.ts
with open(os.path.join(base_dir, 'plans.ts'), 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("import { PlanStatus } from '../../contracts/planning/plan';\n", '')
content = "export type PlanStatus = 'Draft' | 'Optimizing' | 'Recommended' | 'Generated' | 'Published' | 'Active' | 'Archived';\n" + content
with open(os.path.join(base_dir, 'plans.ts'), 'w', encoding='utf-8') as f:
    f.write(content)

print("Reverted local statuses.")
