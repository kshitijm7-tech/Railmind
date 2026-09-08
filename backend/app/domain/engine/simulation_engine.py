from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta
import heapq
import uuid

from app.domain.models.simulation import (
    SimulationRun, SimulationResult, SimulationEvent, EventType,
    SimulationStatus, SimulationMetric
)
from app.domain.models.planning import Plan, Block
from app.domain.models.operations import TrainPath, PathSegment
from app.domain.models.maintenance import MaintenanceTask
from app.domain.enums import DataState, DataSource
from app.domain.models.common import Provenance

class SimEvent:
    def __init__(self, time: datetime, event_type: EventType, priority: int, data: Dict[str, Any]):
        self.time = time
        self.event_type = event_type
        self.priority = priority
        self.data = data
        self.id = uuid.uuid4().hex[:8]

    def __lt__(self, other):
        if self.time == other.time:
            return self.priority < other.priority
        return self.time < other.time

class DeterministicDiscreteEventSimulator:
    def __init__(self):
        self.engine_version = "0.1.0"
        self.engine_name = "RailMindDiscreteEventSimulator"

    def simulate(
        self,
        scenario_id: str,
        plan: Plan,
        train_paths: List[TrainPath],
        tasks: List[MaintenanceTask],
        data_state: str = DataState.MOCKED.value
    ) -> SimulationResult:
        
        sim_run_id = f"SIM-{uuid.uuid4().hex[:6].upper()}"
        start_time = datetime.now(timezone.utc)
        
        # Priority Queue for events
        pq: List[SimEvent] = []
        
        # State tracking
        section_blocked_until: Dict[str, datetime] = {}
        train_delays: Dict[str, timedelta] = {p.train_id: timedelta(0) for p in train_paths}
        train_current_segment_idx: Dict[str, int] = {p.train_id: 0 for p in train_paths}
        
        completed_tasks = set()
        incomplete_tasks = set()
        affected_sections = set()
        blocked_trains = set()
        
        recorded_events: List[SimulationEvent] = []
        
        def add_event(t: datetime, etype: EventType, prio: int, data: Dict[str, Any]):
            heapq.heappush(pq, SimEvent(t, etype, prio, data))
            
        def record(t: datetime, etype: EventType, desc: str, entity: str = None, meta: Dict = None):
            recorded_events.append(SimulationEvent(
                event_id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
                event_time=t,
                event_type=etype,
                entity_id=entity,
                description=desc,
                metadata=meta or {}
            ))

        record(start_time, EventType.SIMULATION_STARTED, "Simulation initialized")

        # 1. Schedule Block Activations & Releases
        task_map = {t.task_id: t for t in tasks}
        for block in plan.blocks:
            add_event(block.interval.start, EventType.BLOCK_ACTIVATED, 1, {"block": block})
            add_event(block.interval.end, EventType.BLOCK_RELEASED, 1, {"block": block})

        # 2. Schedule Initial Train Entries
        for path in train_paths:
            if not path.segments:
                continue
            first_seg = path.segments[0]
            add_event(first_seg.interval.start, EventType.TRAIN_ENTERED_SECTION, 5, {
                "train_id": path.train_id,
                "path": path,
                "segment_idx": 0
            })

        # Process Events
        current_time = start_time
        while pq:
            evt = heapq.heappop(pq)
            current_time = evt.time
            
            if evt.event_type == EventType.BLOCK_ACTIVATED:
                b: Block = evt.data["block"]
                section_blocked_until[b.section_id] = b.interval.end
                affected_sections.add(b.section_id)
                record(current_time, evt.event_type, f"Block {b.block_id} activated on {b.section_id}", b.block_id)
                
                # Check task completions
                for tid in b.tasks:
                    if tid in task_map:
                        t = task_map[tid]
                        # If block duration >= task duration, it completes
                        bdur = (b.interval.end - b.interval.start).total_seconds() / 60.0
                        if bdur >= t.duration.expected:
                            add_event(b.interval.start + timedelta(minutes=t.duration.expected), 
                                      EventType.MAINTENANCE_COMPLETED, 2, {"task_id": tid, "block_id": b.block_id})
                            record(current_time, EventType.MAINTENANCE_STARTED, f"Task {tid} started", tid)
                        else:
                            incomplete_tasks.add(tid)

            elif evt.event_type == EventType.MAINTENANCE_COMPLETED:
                tid = evt.data["task_id"]
                completed_tasks.add(tid)
                record(current_time, evt.event_type, f"Task {tid} completed", tid)

            elif evt.event_type == EventType.BLOCK_RELEASED:
                b: Block = evt.data["block"]
                record(current_time, evt.event_type, f"Block {b.block_id} released on {b.section_id}", b.block_id)

            elif evt.event_type == EventType.TRAIN_ENTERED_SECTION:
                tid = evt.data["train_id"]
                path: TrainPath = evt.data["path"]
                idx = evt.data["segment_idx"]
                seg = path.segments[idx]
                
                # Is section blocked?
                block_end = section_blocked_until.get(seg.section_id)
                if block_end and block_end > current_time:
                    # Train is blocked
                    blocked_trains.add(tid)
                    delay = block_end - current_time
                    train_delays[tid] += delay
                    record(current_time, EventType.TRAIN_BLOCKED, f"Train {tid} blocked at {seg.section_id} until {block_end.strftime('%H:%M')}", tid)
                    
                    # Reschedule entry when block released
                    add_event(block_end, EventType.TRAIN_ENTERED_SECTION, 5, evt.data)
                else:
                    record(current_time, evt.event_type, f"Train {tid} entered {seg.section_id}", tid)
                    # Schedule exit
                    duration = seg.interval.end - seg.interval.start
                    exit_t = current_time + duration
                    add_event(exit_t, EventType.TRAIN_EXITED_SECTION, 5, evt.data)

            elif evt.event_type == EventType.TRAIN_EXITED_SECTION:
                tid = evt.data["train_id"]
                path: TrainPath = evt.data["path"]
                idx = evt.data["segment_idx"]
                seg = path.segments[idx]
                
                record(current_time, evt.event_type, f"Train {tid} exited {seg.section_id}", tid)
                
                # Next segment
                if idx + 1 < len(path.segments):
                    next_seg = path.segments[idx+1]
                    # original wait time before next segment (if any scheduled wait)
                    orig_wait = max(timedelta(0), next_seg.interval.start - seg.interval.end)
                    next_entry = current_time + orig_wait
                    add_event(next_entry, EventType.TRAIN_ENTERED_SECTION, 5, {
                        "train_id": tid,
                        "path": path,
                        "segment_idx": idx + 1
                    })

        record(current_time, EventType.SIMULATION_COMPLETED, "Simulation completed deterministically")
        
        # Calculate Metrics
        total_delay_min = sum(d.total_seconds() for d in train_delays.values()) / 60.0
        max_delay_min = max([d.total_seconds() for d in train_delays.values()] + [0]) / 60.0
        avg_delay = total_delay_min / len(train_paths) if train_paths else 0.0
        
        prov = Provenance(
            state=data_state,
            source=DataSource.SYSTEM.value,
            generatedAt=datetime.now(timezone.utc),
            generatorVersion=self.engine_version
        )
        
        exp = f"Simulation complete. {len(blocked_trains)} trains blocked, total delay {total_delay_min} mins."
        
        res = SimulationResult(
            simulation_run_id=sim_run_id,
            status=SimulationStatus.COMPLETED,
            duration_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
            affected_trains=len([d for d in train_delays.values() if d.total_seconds() > 0]),
            total_delay_minutes=total_delay_min,
            maximum_delay_minutes=max_delay_min,
            average_delay_minutes=avg_delay,
            completed_maintenance_tasks=len(completed_tasks),
            incomplete_maintenance_tasks=len(incomplete_tasks),
            blocked_trains=len(blocked_trains),
            affected_sections=list(affected_sections),
            block_utilization=100.0 if completed_tasks else 0.0,
            operational_impact_score=total_delay_min * 1.5,
            events=recorded_events,
            explanation=exp,
            provenance=prov
        )
        return res