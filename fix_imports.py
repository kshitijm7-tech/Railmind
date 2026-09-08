import os

base_dir = r"d:\Projects\Railmind\frontend\domain\types"

# Fix network.ts
with open(os.path.join(base_dir, "network.ts"), "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("export { Criticality, Department };", "export type { Criticality, Department };")
with open(os.path.join(base_dir, "network.ts"), "w", encoding="utf-8") as f:
    f.write(content)

# Fix maintenance.ts
with open(os.path.join(base_dir, "maintenance.ts"), "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("export { TaskType, TaskStatus };", "export type { TaskType, TaskStatus };")
with open(os.path.join(base_dir, "maintenance.ts"), "w", encoding="utf-8") as f:
    f.write(content)

# Fix disruptions.ts
with open(os.path.join(base_dir, "disruptions.ts"), "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("export { DisruptionType, IncidentStatus };", "export type { DisruptionType, IncidentStatus };")
with open(os.path.join(base_dir, "disruptions.ts"), "w", encoding="utf-8") as f:
    f.write(content)

# Blocks.ts
with open(os.path.join(base_dir, "blocks.ts"), "r", encoding="utf-8") as f:
    content = f.read()
if "import { ISOTimestamp }" not in content:
    content = "import { ISOTimestamp } from '../../contracts/common/ids';\nimport { BlockStatus } from '../../contracts/planning/block';\n" + content
    content = content.replace("export type BlockStatus = 'Requested' | 'Approved' | 'Active' | 'Completed' | 'Overrun' | 'Cancelled';", "")
with open(os.path.join(base_dir, "blocks.ts"), "w", encoding="utf-8") as f:
    f.write(content)

# Decisions.ts
with open(os.path.join(base_dir, "decisions.ts"), "r", encoding="utf-8") as f:
    content = f.read()
if "import { ISOTimestamp }" not in content:
    content = "import { ISOTimestamp } from '../../contracts/common/ids';\n" + content
with open(os.path.join(base_dir, "decisions.ts"), "w", encoding="utf-8") as f:
    f.write(content)

# Plans.ts
with open(os.path.join(base_dir, "plans.ts"), "r", encoding="utf-8") as f:
    content = f.read()
if "import { ISOTimestamp }" not in content:
    content = "import { ISOTimestamp } from '../../contracts/common/ids';\nimport { PlanStatus } from '../../contracts/planning/plan';\n" + content
    content = content.replace("export type PlanStatus = 'Draft' | 'Optimizing' | 'Published' | 'Active' | 'Archived';", "")
with open(os.path.join(base_dir, "plans.ts"), "w", encoding="utf-8") as f:
    f.write(content)
