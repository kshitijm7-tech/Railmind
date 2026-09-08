export interface HardConstraint {
  readonly id: string;
  readonly name: string;
  readonly description: string;
}

export interface SoftConstraint {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly weight: number;
}

export interface ConstraintResult {
  readonly constraint_id: string;
  readonly is_satisfied: boolean;
  readonly violation_degree?: number;
  readonly description: string;
}
