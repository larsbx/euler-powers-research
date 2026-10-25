import Lean
import EulerPowers
import Modular
import PairIndex
import SortedIndex
import BinarySearch
import LowerBoundInvariant
import Reconstruction
import CertifiedLowerBound
import ShardPlan
import Int64Bounds
import SignedLowerBound
import PairPartition
import PairTraversal
import PackedPairIndex
import PrimePowerSieve
import DigitSumPruning

/-! Audit all EulerPowers theorems for additional axioms and opaque holes. -/
open Lean Elab Command in
#eval show CommandElabM Unit from do
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let mut checked := 0
  let mut bad : Array (Name × Name) := #[]
  for (n, ci) in (← getEnv).constants.toList do
    if (`EulerPowers).isPrefixOf n && ci matches .thmInfo _ then
      checked := checked + 1
      for a in ← liftCoreM (collectAxioms n) do
        unless allowed.contains a do bad := bad.push (n, a)
  if checked < 7 then
    throwError m!"axiom audit: expected at least seven theorems, got {checked}"
  else if bad.isEmpty then
    logInfo m!"axiom audit: {checked} kernel-checked theorems, no nonstandard axioms"
  else
    throwError m!"axiom audit failed: {bad.toList}"
