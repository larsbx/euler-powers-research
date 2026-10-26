import TraceReplay

/-!
Lean independent replay of actual Mojo BigZ lower-bound observations.

Unlike TraceReplay.lean's original machine-Int64 input contract,
these canonical decimal values are arbitrary mathematical Int.
The exact same signedLowerBound proof checks each native pivot,
narrowing branch, first-hit position, and duplicate membership.
Only the independent trace *observations* bridge Mojo to Lean;
compiled binary universal correctness is not asserted.
-/

namespace EulerPowers

def bigReadValues : Nat → List String →
    Except String (List Int × List String)
  | 0, rows => .ok ([], rows)
  | _ + 1, [] => .error "truncated arbitrary-precision VAL section"
  | n + 1, row :: rows => do
      let v ← match row.splitOn " " with
        | ["VAL", token] =>
            traceRequire (traceInt token) "noncanonical exact BigZ decimal"
        | _ => throw "malformed BigZ VAL record"
      let (tail, remain) ← bigReadValues n rows
      return (v :: tail, remain)

def bigSorted : List Int → Bool
  | [] => true
  | [_] => true
  | x :: y :: tail => decide (x ≤ y) && bigSorted (y :: tail)

def bigReadCases (index : Nat) :
    Nat → List String → Except String Nat
  | 0, [] => .ok index
  | 0, _ => .error "extra BigZ search cases"
  | _ + 1, [] => .error "missing BigZ CASE"
  | fuel + 1, row :: rows => do
      let (caseId, target, count) ← match row.splitOn " " with
        | ["CASE", ident, targetText, countText] => do
            pure (← traceRequire (traceNat ident) "invalid CASE index",
                  ← traceRequire (traceInt targetText) "invalid BigZ target",
                  ← traceRequire (traceNat countText) "invalid CASE length")
        | _ => throw "malformed BigZ CASE header"
      if caseId != index || count > 100 then
        throw "BigZ case index or bounded trace-size mismatch"
      let (values, steps) ← bigReadValues count rows
      if values.length != count || !bigSorted values then
        throw "BigZ trace input not sorted or wrong length"
      let remain ← readSteps values.toArray target 0 count (count + 1) steps
      bigReadCases (index + 1) fuel remain

def replayBigzTrace (input : String) : Except String Nat := do
  let rows ← match (input.splitOn "\n").reverse with
    | "" :: rest => .ok rest.reverse
    | _ => throw "BigZ transcript requires exactly one terminal newline"
  bigReadCases 0 18 rows

end EulerPowers

def main (args : List String) : IO Unit := do
  match args with
  | [path] =>
      let input ← IO.FS.readFile path
      match EulerPowers.replayBigzTrace input with
      | .ok n => IO.println s!"Lean independently replayed {n} actual Mojo arbitrary-precision BigZ lower-bound cases."
      | .error reason => throw <| IO.userError s!"Lean rejected BigZ trace: {reason}"
  | _ => throw <| IO.userError "usage: bigz-trace-replay <native-mojo-transcript>"
