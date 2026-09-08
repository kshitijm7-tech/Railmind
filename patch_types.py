import re
import os

files_to_patch = {
    "network.ts": [
        (r"export type Criticality = 'LOW' \| 'MEDIUM' \| 'HIGH' \| 'CRITICAL';\n\nexport type Department = 'Engineering' \| 'S&T' \| 'TRD' \| 'OHE';\n", "import { Criticality, Department } from '../../contracts/common/enums';\nimport { ISOTimestamp } from '../../contracts/common/ids';\nexport { Criticality, Department };\n"),
        (r"last_inspected: string;", "last_inspected: ISOTimestamp;"),
        (r"next_due: string;", "next_due: ISOTimestamp;")
    ],
    "maintenance.ts": [
        (r"export type TaskType = 'PREVENTIVE' \| 'CORRECTIVE' \| 'INSPECTION' \| 'EMERGENCY';\n\nexport type TaskStatus = 'PENDING' \| 'SCHEDULED' \| 'IN_PROGRESS' \| 'COMPLETED' \| 'CANCELLED';\n", "import { TaskType, TaskStatus } from '../../contracts/maintenance/maintenance-task';\nimport { ISOTimestamp } from '../../contracts/common/ids';\nexport { TaskType, TaskStatus };\n"),
        (r"import \{ Criticality, Department \} from '\./network';", "import { Criticality, Department } from '../../contracts/common/enums';"),
        (r"requested_start: string;", "requested_start: ISOTimestamp;"),
        (r"requested_end: string;", "requested_end: ISOTimestamp;"),
        (r"actual_start\?: string;", "actual_start?: ISOTimestamp;"),
        (r"actual_end\?: string;", "actual_end?: ISOTimestamp;"),
    ],
    "trains.ts": [
        (r"import \{ Criticality \} from '\./network';", "import { Criticality } from '../../contracts/common/enums';\nimport { ISOTimestamp } from '../../contracts/common/ids';"),
        (r"scheduled_arrival: string;", "scheduled_arrival: ISOTimestamp;"),
        (r"scheduled_departure: string;", "scheduled_departure: ISOTimestamp;"),
        (r"actual_arrival\?: string;", "actual_arrival?: ISOTimestamp;"),
        (r"actual_departure\?: string;", "actual_departure?: ISOTimestamp;")
    ],
    "blocks.ts": [
        (r"export type BlockStatus = 'DRAFT' \| 'REQUESTED' \| 'APPROVED' \| 'ACTIVE' \| 'COMPLETED' \| 'CANCELLED';\n", "import { BlockStatus } from '../../contracts/planning/block';\nimport { ISOTimestamp } from '../../contracts/common/ids';\nexport { BlockStatus };\n"),
        (r"import \{ TaskType \} from '\./maintenance';", "import { TaskType } from '../../contracts/maintenance/maintenance-task';"),
        (r"start_time: string;", "start_time: ISOTimestamp;"),
        (r"end_time: string;", "end_time: ISOTimestamp;"),
        (r"requested_start: string;", "requested_start: ISOTimestamp;"),
        (r"requested_end: string;", "requested_end: ISOTimestamp;"),
        (r"approved_start\?: string;", "approved_start?: ISOTimestamp;"),
        (r"approved_end\?: string;", "approved_end?: ISOTimestamp;"),
        (r"actual_start\?: string;", "actual_start?: ISOTimestamp;"),
        (r"actual_end\?: string;", "actual_end?: ISOTimestamp;"),
    ],
    "plans.ts": [
        (r"export type PlanStatus = 'DRAFT' \| 'PROPOSED' \| 'APPROVED' \| 'ACTIVE' \| 'ARCHIVED' \| 'REJECTED';\n", "import { PlanStatus } from '../../contracts/planning/plan';\nimport { ISOTimestamp } from '../../contracts/common/ids';\nexport { PlanStatus };\n"),
        (r"import \{ Block \} from '\./blocks';", "import { Block } from './blocks';"),
        (r"horizon_start: string;", "horizon_start: ISOTimestamp;"),
        (r"horizon_end: string;", "horizon_end: ISOTimestamp;"),
        (r"created_at: string;", "created_at: ISOTimestamp;"),
        (r"updated_at: string;", "updated_at: ISOTimestamp;"),
    ],
    "disruptions.ts": [
        (r"export type DisruptionType = 'ASSET_FAILURE' \| 'WEATHER' \| 'CREW_SHORTAGE' \| 'POWER_OUTAGE' \| 'ACCIDENT' \| 'OTHER';\n\nexport type IncidentStatus = 'REPORTED' \| 'VERIFIED' \| 'UNDER_REPAIR' \| 'RESOLVED' \| 'CLOSED';\n", "import { DisruptionType, IncidentStatus } from '../../contracts/disruption/disruption';\nimport { ISOTimestamp } from '../../contracts/common/ids';\nexport { DisruptionType, IncidentStatus };\n"),
        (r"import \{ Criticality \} from '\./network';", "import { Criticality } from '../../contracts/common/enums';"),
        (r"reported_at: string;", "reported_at: ISOTimestamp;"),
        (r"estimated_resolution\?: string;", "estimated_resolution?: ISOTimestamp;"),
        (r"actual_resolution\?: string;", "actual_resolution?: ISOTimestamp;"),
    ],
    "decisions.ts": [
        (r"import \{ AuditEvent \} from '\.\.\/\.\.\/types\/audit';\n", "import { ISOTimestamp } from '../../contracts/common/ids';\n"),
        (r"timestamp: string;", "timestamp: ISOTimestamp;"),
    ],
    "recommendations.ts": [
        (r"import \{ PlanMetrics \} from '\./plans';", "import { PlanMetrics } from './plans';\nimport { ISOTimestamp } from '../../contracts/common/ids';"),
        (r"generated_at: string;", "generated_at: ISOTimestamp;"),
    ]
}

base_dir = r"d:\Projects\Railmind\frontend\domain\types"

for file_name, replacements in files_to_patch.items():
    full_path = os.path.join(base_dir, file_name)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        for old, new in replacements:
            content = re.sub(old, new, content, count=1)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

print("Patched types.")
