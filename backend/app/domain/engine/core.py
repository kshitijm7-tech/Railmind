from typing import List
from app.domain.engine.models import EvaluationContext, EvaluationResult, ConstraintStatus, ConstraintSeverity
from app.domain.models.planning import CandidateBlockWindow
from app.domain.engine.rules import Rule

class ConstraintEngine:
    def __init__(self, rules: List[Rule] = None):
        if rules is None:
            self.rules = []
        else:
            self.rules = rules

    def register_rule(self, rule: Rule):
        self.rules.append(rule)

    def evaluate_candidate(self, candidate: CandidateBlockWindow, context: EvaluationContext) -> EvaluationResult:
        all_violations = []
        for rule in self.rules:
            violations = rule.evaluate(candidate, context)
            all_violations.extend(violations)
            
        status = ConstraintStatus.FEASIBLE
        has_warnings = False
        
        for v in all_violations:
            if v.severity == ConstraintSeverity.HARD:
                status = ConstraintStatus.INFEASIBLE
            elif v.severity == ConstraintSeverity.SOFT and status != ConstraintStatus.INFEASIBLE:
                has_warnings = True

        if status != ConstraintStatus.INFEASIBLE and has_warnings:
            status = ConstraintStatus.FEASIBLE_WITH_WARNINGS

        return EvaluationResult(
            status=status,
            violations=all_violations
        )
