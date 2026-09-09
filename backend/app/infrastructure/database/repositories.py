from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.repositories import PlanRepository
from app.domain.models.planning import Plan
from app.infrastructure.database.models import PlanORM, BlockORM
from app.infrastructure.database.mappers import to_plan_orm, to_plan_domain

class PostgresPlanRepository(PlanRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_all(self, page: int, page_size: int) -> tuple[List[Plan], int]:
        db: Session = next(self.session_factory())
        try:
            total = db.query(PlanORM).count()
            records = db.query(PlanORM).offset((page - 1) * page_size).limit(page_size).all()
            return [to_plan_domain(r) for r in records], total
        finally:
            db.close()

    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        db: Session = next(self.session_factory())
        try:
            record = db.query(PlanORM).filter(PlanORM.plan_id == plan_id).first()
            if record:
                return to_plan_domain(record)
            return None
        finally:
            db.close()

    def save(self, plan: Plan) -> None:
        db: Session = next(self.session_factory())
        try:
            orm_obj = to_plan_orm(plan)
            
            # Delete existing plan and cascade its blocks, then insert
            existing = db.query(PlanORM).filter(PlanORM.plan_id == plan.plan_id).first()
            if existing:
                db.delete(existing)
                
            db.add(orm_obj)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()