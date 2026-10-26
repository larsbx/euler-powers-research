import ShardPlan

/-!
Formal source-level contract for complete BigZ shard plans.

The native positive BigZ executor accepts at most four consecutive
heights per shard. A plan that starts at 2, has no gaps or overlaps,
and terminates at the declared B covers each requested height.
This proves mathematical interval coverage, not binary execution,
independent oracle conformance, or authenticated receipt provenance.
-/

namespace EulerPowers

def bigzPlan16 : List (Nat × Nat) :=
  [(2,5), (6,9), (10,13), (14,16)]

def bigzPlan12 : List (Nat × Nat) :=
  [(2,5), (6,9), (10,12)]

/-- The complete small Mojo CI plan spans precisely 2..12. -/
theorem bigzPlan12_valid : validPlan 12 bigzPlan12 = true := by decide

theorem bigzPlan16_valid : validPlan 16 bigzPlan16 = true := by decide

/-- Every shard is inside the four-height intake of the Mojo worker. -/
theorem bigzPlan16_width :
    bigzPlan16.all (fun p => decide (p.2 - p.1 < 4)) = true := by decide

theorem bigzPlan12_width :
    bigzPlan12.all (fun p => decide (p.2 - p.1 < 4)) = true := by decide

/-- All heights in the accepted planning interval belong to some shard. -/
theorem bigzPlan16_covers (e : Nat) (hlo : 2 ≤ e) (hhi : e ≤ 16) :
    ∃ lo hi, (lo,hi) ∈ bigzPlan16 ∧ lo ≤ e ∧ e ≤ hi := by
  exact validPlan_covers 16 bigzPlan16 bigzPlan16_valid e hlo hhi

theorem bigzPlan12_covers (e : Nat) (hlo : 2 ≤ e) (hhi : e ≤ 12) :
    ∃ lo hi, (lo,hi) ∈ bigzPlan12 ∧ lo ≤ e ∧ e ≤ hi := by
  exact validPlan_covers 12 bigzPlan12 bigzPlan12_valid e hlo hhi

theorem bigzPlan12_gap_refused :
    validPlan 12 [(2,5),(7,9),(10,12)] = false := by decide

theorem bigzPlan12_overlap_refused :
    validPlan 12 [(2,5),(5,9),(10,12)] = false := by decide

theorem bigzPlan12_missing_tail_refused :
    validPlan 12 [(2,5),(6,9)] = false := by decide

theorem bigzPlan12_excess_refused :
    validPlan 12 [(2,5),(6,9),(10,13)] = false := by decide

end EulerPowers
