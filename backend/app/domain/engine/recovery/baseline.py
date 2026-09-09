import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.domain.models.recovery import (
    Disruption, ImpactAssessment, RecoveryOption, RecoveryAssessmentRequest,
    RecoveryAction, RecoveryActionType
)
from app.domain.models.common import Provenance
from app.domain.enums import DataSource
from app.domain.engine.recovery.interfaces import ImpactAssessmentEngine, RecoveryCandidateGenerator

class DeterministicImpactAssessmentEngine(ImpactAssessmentEngine):
    def assess_impact(
        self,
        disruption: Disruption,
        raw_context: Dict[str, Any]
    ) -> ImpactAssessment:
        
        # Raw context is expected to provide plan details, section topology, etc.
        # For baseline, we extract affected elements directly mapping from the disruption's resource.
        
        impact = ImpactAssessment(
            disruption_id=disruption.disruption_id,
            description=f"Impact assessment for {disruption.type.value} on {disruption.affected_resource}"
        )
        
        # Determine direct topological and logical impacts based on disruption
        res_id = disruption.affected_resource
        res_type = disruption.affected_resource_type
        
        if res_type == "SECTION":
            impact.affected_sections.append(res_id)
            # Find blocks in this section
            blocks = raw_context.get("blocks", [])
            for b in blocks:
                # Naive time overlap check would normally go here, using a simpler heuristic
                if b.get("section_id") == res_id:
                    impact.affected_blocks.append(b.get("block_id"))
                    for task_id in b.get("tasks", []):
                        impact.affected_maintenance_tasks.append(task_id)
            
            # Find trains passing through
            train_paths = raw_context.get("train_paths", [])
            for path in train_paths:
                for seg in path.get("segments", []):
                    if seg.get("section_id") == res_id:
                        impact.affected_train_paths.append(path.get("train_id"))
                        impact.affected_trains.append(path.get("train_id"))
                        impact.delay_exposure_minutes += 30.0 # Heuristic initial delay exposure
                        
        elif res_type == "TRAIN":
            impact.affected_trains.append(res_id)
            impact.delay_exposure_minutes += 60.0
            
        elif res_type == "ASSET":
            impact.affected_assets.append(res_id)
            impact.asset_availability_exposure_score = 100.0
            # Identify tasks on this asset
            tasks = raw_context.get("maintenance_tasks", [])
            for task in tasks:
                if task.get("asset_id") == res_id:
                    impact.affected_maintenance_tasks.append(task.get("task_id"))
                    impact.maintenance_exposure_hours += 4.0

        # Deduplicate
        impact.affected_trains = list(set(impact.affected_trains))
        impact.affected_train_paths = list(set(impact.affected_train_paths))
        impact.affected_maintenance_tasks = list(set(impact.affected_maintenance_tasks))
        impact.affected_blocks = list(set(impact.affected_blocks))
        impact.affected_sections = list(set(impact.affected_sections))
        impact.affected_assets = list(set(impact.affected_assets))
        
        return impact

class DeterministicRecoveryCandidateGenerator(RecoveryCandidateGenerator):
    engine_name = "DeterministicRecovery"
    engine_version = "1.0.0"
    
    def generate_candidates(
        self,
        assessment: ImpactAssessment,
        request: RecoveryAssessmentRequest,
        raw_context: Dict[str, Any]
    ) -> List[RecoveryOption]:
        
        candidates = []
        state = request.disruption.state_mode
        
        base_prov = Provenance(
            state=state,
            source=DataSource.SYSTEM,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion=self.engine_version
        )
        
        # 1. NO_ACTION Candidate (Always considered)
        no_action = RecoveryOption(
            recovery_option_id=f"REC-NO-{uuid.uuid4().hex[:8]}",
            base_plan_id=request.base_plan_id,
            disruption_id=request.disruption.disruption_id,
            actions=[RecoveryAction(
                action_type=RecoveryActionType.NO_ACTION,
                target_entity_id=request.base_plan_id,
                target_entity_type="PLAN",
                description="Accept impact and allow plan to execute without structural changes."
            )],
            expected_tradeoffs=["Accepts operational delay", "Preserves original maintenance schedules"],
            constraint_status="FEASIBLE", # No action is trivially feasible, though maybe suboptimal
            quality="HIGH",
            provenance=base_prov
        )
        candidates.append(no_action)
        
        # 2. Shift/Defer Block Candidate (if blocks are affected)
        if assessment.affected_blocks:
            actions = []
            tradeoffs = []
            for b_id in assessment.affected_blocks:
                actions.append(RecoveryAction(
                    action_type=RecoveryActionType.SHIFT_BLOCK,
                    target_entity_id=b_id,
                    target_entity_type="BLOCK",
                    parameters={"shift_hours": 24},
                    description=f"Shift block {b_id} by 24 hours to avoid disruption window."
                ))
            tradeoffs.append(f"Delays {len(assessment.affected_blocks)} maintenance blocks by 24h")
            tradeoffs.append("Clears sections for immediate train rerouting")
            
            candidates.append(RecoveryOption(
                recovery_option_id=f"REC-SH-{uuid.uuid4().hex[:8]}",
                base_plan_id=request.base_plan_id,
                disruption_id=request.disruption.disruption_id,
                actions=actions,
                affected_entities=assessment.affected_blocks,
                expected_tradeoffs=tradeoffs,
                constraint_status="UNKNOWN", # P09 must evaluate this later
                quality="MEDIUM",
                provenance=base_prov
            ))
            
        # 3. Cancel Maintenance (if tasks are affected)
        if assessment.affected_maintenance_tasks:
            # We would normally consult P10 Priority here to see if cancellation is safe
            priority_data = raw_context.get("priorities", {})
            safe_to_cancel = True
            for t_id in assessment.affected_maintenance_tasks:
                task_prio = priority_data.get(t_id, {}).get("priority_class", "LOW")
                if task_prio == "CRITICAL":
                    safe_to_cancel = False
                    break
            
            if safe_to_cancel:
                actions = []
                for t_id in assessment.affected_maintenance_tasks:
                    actions.append(RecoveryAction(
                        action_type=RecoveryActionType.DEFER_MAINTENANCE,
                        target_entity_id=t_id,
                        target_entity_type="MAINTENANCE_TASK",
                        description=f"Cancel and defer low-priority maintenance task {t_id}."
                    ))
                candidates.append(RecoveryOption(
                    recovery_option_id=f"REC-CX-{uuid.uuid4().hex[:8]}",
                    base_plan_id=request.base_plan_id,
                    disruption_id=request.disruption.disruption_id,
                    actions=actions,
                    affected_entities=assessment.affected_maintenance_tasks,
                    expected_tradeoffs=["Improves train flow", "Increases long-term asset risk"],
                    constraint_status="UNKNOWN",
                    quality="MEDIUM",
                    provenance=base_prov
                ))

        # Sort candidates deterministically to ensure reproduceability
        # Sort by length of actions, then recovery option type prefix
        candidates.sort(key=lambda c: (len(c.actions), c.recovery_option_id[:6]))
        return candidates