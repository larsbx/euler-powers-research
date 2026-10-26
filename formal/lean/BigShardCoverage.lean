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

/-- Exact 36-width-four shard plan for the B144 native BigZ CI run. -/
def bigzPlan144 : List (Nat × Nat) :=
  [(2,5), (6,9), (10,13), (14,17), (18,21), (22,25), (26,29), (30,33), (34,37), (38,41), (42,45), (46,49), (50,53), (54,57), (58,61), (62,65), (66,69), (70,73), (74,77), (78,81), (82,85), (86,89), (90,93), (94,97), (98,101), (102,105), (106,109), (110,113), (114,117), (118,121), (122,125), (126,129), (130,133), (134,137), (138,141), (142,144)]

theorem bigzPlan144_valid :
    validPlan 144 bigzPlan144 = true := by decide

theorem bigzPlan144_width :
    bigzPlan144.all (fun p => decide (p.2 - p.1 < 4)) = true := by decide

theorem bigzPlan144_covers (e : Nat) (hlo : 2 ≤ e) (hhi : e ≤ 144) :
    ∃ lo hi, (lo,hi) ∈ bigzPlan144 ∧ lo ≤ e ∧ e ≤ hi := by
  exact validPlan_covers 144 bigzPlan144 bigzPlan144_valid e hlo hhi

/-- Fixed 80-shard plan for the full native BigZ 2..320 executable census. -/
def bigzPlan320 : List (Nat × Nat) :=
  [(2,5), (6,9), (10,13), (14,17), (18,21), (22,25), (26,29), (30,33), (34,37), (38,41), (42,45), (46,49), (50,53), (54,57), (58,61), (62,65), (66,69), (70,73), (74,77), (78,81), (82,85), (86,89), (90,93), (94,97), (98,101), (102,105), (106,109), (110,113), (114,117), (118,121), (122,125), (126,129), (130,133), (134,137), (138,141), (142,145), (146,149), (150,153), (154,157), (158,161), (162,165), (166,169), (170,173), (174,177), (178,181), (182,185), (186,189), (190,193), (194,197), (198,201), (202,205), (206,209), (210,213), (214,217), (218,221), (222,225), (226,229), (230,233), (234,237), (238,241), (242,245), (246,249), (250,253), (254,257), (258,261), (262,265), (266,269), (270,273), (274,277), (278,281), (282,285), (286,289), (290,293), (294,297), (298,301), (302,305), (306,309), (310,313), (314,317), (318,320)]

theorem bigzPlan320_valid :
    validPlan 320 bigzPlan320 = true := by decide

theorem bigzPlan320_width :
    bigzPlan320.all (fun p => decide (p.2 - p.1 < 4)) = true := by decide

theorem bigzPlan320_covers (e : Nat) (hlo : 2 ≤ e) (hhi : e ≤ 320) :
    ∃ lo hi, (lo,hi) ∈ bigzPlan320 ∧ lo ≤ e ∧ e ≤ hi := by
  exact validPlan_covers 320 bigzPlan320 bigzPlan320_valid e hlo hhi

end EulerPowers
