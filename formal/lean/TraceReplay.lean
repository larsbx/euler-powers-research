import SignedLowerBound

/-!
# Independently executable Lean replay of actual Mojo lower-bound traces

This verifier uses exact signed integers to check each observed pivot and
every state transition of the shared production Mojo lower-bound function.
It rejects reordered, omitted, forged, out-of-bounds and truncated steps.

No proof of general Mojo machine-code equivalence follows from these
finite traces. The case inputs and the emitted transcript are runtime
observations, not an independently authenticated hardware trace.
-/

namespace EulerPowers

def traceNat (s : String) : Option Nat := do
  let n ← s.toNat?
  if toString n == s then some n else none

def traceInt (s : String) : Option Int := do
  let n ← s.toInt?
  if toString n == s then some n else none

def traceRequire {α : Type} (x : Option α) (msg : String) :
    Except String α :=
  match x with
  | some v => .ok v
  | none => .error msg

def inInt64 (v : Int) : Bool :=
  decide (-(9223372036854775808 : Int) ≤ v ∧
    v ≤ (9223372036854775807 : Int))

def readValues : Nat → List String → Except String (List Int × List String)
  | 0, rest => .ok ([], rest)
  | _ + 1, [] => .error "truncated VALUE section"
  | n + 1, row :: rest => do
      let v ← match row.splitOn " " with
        | ["VAL", token] => traceRequire (traceInt token) "invalid VAL integer"
        | _ => throw "invalid VAL line"
      if !inInt64 v then
        throw "VAL outside signed Int64 range"
      let (tail, remaining) ← readValues n rest
      return (v :: tail, remaining)

def readSteps (values : Array Int) (target : Int) (lo hi : Nat) :
    Nat → List String → Except String (List String)
  | 0, _ => .error "search exceeded permitted finite step count"
  | fuel + 1, rows => do
      if lo < hi then
        let (row, rest) ← match rows with
          | head :: tail => .ok (head, tail)
          | [] => .error "truncated search STEP section"
        let (oldLo, oldHi, reportedMid, reportedPivot) ←
          match row.splitOn " " with
          | ["STEP", loText, hiText, midText, pivotText] => do
              pure (← traceRequire (traceNat loText) "invalid STEP lo",
                ← traceRequire (traceNat hiText) "invalid STEP hi",
                ← traceRequire (traceNat midText) "invalid STEP mid",
                ← traceRequire (traceInt pivotText) "invalid STEP pivot")
          | _ => throw "invalid STEP line"
        let mid := lo + (hi - lo) / 2
        let actual ← traceRequire values[mid]? "midpoint outside input"
        if oldLo != lo || oldHi != hi || reportedMid != mid ||
            reportedPivot != actual then
          throw "STEP diverged from actual signed lower-bound transition"
        if actual < target then
          readSteps values target (mid + 1) hi fuel rest
        else
          readSteps values target lo mid fuel rest
      else
        let (stopLine, resultLine, afterStop) ← match rows with
          | stop :: result :: marker :: rest =>
              if marker == "END" then .ok (stop, result, rest)
              else .error "missing END marker"
          | _ => .error "truncated terminal section"
        let stopPos ← match stopLine.splitOn " " with
          | ["STOP", token] =>
              traceRequire (traceNat token) "invalid STOP index"
          | _ => throw "invalid STOP line"
        let (resultPos, resultBit) ← match resultLine.splitOn " " with
          | ["RESULT", posText, flag] => do
              pure (← traceRequire (traceNat posText) "invalid RESULT index",
                ← traceRequire (traceNat flag) "invalid RESULT bit")
          | _ => throw "invalid RESULT line"
        if stopPos != lo || resultPos != lo || resultBit > 1 then
          throw "terminal lower-bound index mismatch"
        let expectedBit := if values[lo]? == some target then 1 else 0
        if resultBit != expectedBit then
          throw "RESULT does not match index and target"
        if ((resultBit == 1) != values.toList.contains target) then
          throw "lower-bound result is not exact list membership"
        if hSorted : values.toList.Pairwise (· ≤ ·) then
          let oracle := signedLowerBound values.toList target 0
            values.size hSorted (signedInitial values.toList target)
          if oracle.1 != lo then
            throw "observed native terminal index differs from certified Lean signed lower bound"
        else
          throw "input lacks the signed sorted-list proof"
        let leftPart := values.toList.take lo
        let suffix := values.toList.drop lo
        if !(leftPart.all (fun v => decide (v < target))) ||
            !(suffix.all (fun v => decide (target ≤ v))) then
          throw "terminal index violates lower-bound partition invariant"
        return afterStop

def readCases (index : Nat) : Nat → List String → Except String Nat
  | 0, [] => .ok index
  | 0, _ => .error "extra cases after expected transcript"
  | _ + 1, [] => .error "missing expected CASE"
  | fuel + 1, row :: rest => do
      let (caseId, target, count) ← match row.splitOn " " with
        | ["CASE", idText, targetText, countText] => do
            pure (← traceRequire (traceNat idText) "invalid CASE id",
              ← traceRequire (traceInt targetText) "invalid CASE target",
              ← traceRequire (traceNat countText) "invalid CASE count")
        | _ => throw "invalid CASE header"
      if caseId != index || !inInt64 target || count > 1000 then
        throw "CASE sequence, target range, or size invalid"
      let (values, nextRows) ← readValues count rest
      if !(values.toArray.size == count) then
        throw "input length mismatch"
      let rec sorted : List Int → Bool
        | [] => true
        | [_] => true
        | x :: y :: tail => decide (x ≤ y) && sorted (y :: tail)
      if !sorted values then
        throw "input is not sorted"
      let remaining ← readSteps values.toArray target 0 count
        (count + 1) nextRows
      readCases (index + 1) fuel remaining

def replayTrace (input : String) : Except String Nat := do
  let rows ← match (input.splitOn "\n").reverse with
    | "" :: rest => .ok rest.reverse
    | _ => .error "trace must end with exactly one newline"
  readCases 0 21 rows

end EulerPowers

def main (args : List String) : IO Unit := do
  match args with
  | [path] =>
      let content ← IO.FS.readFile path
      match EulerPowers.replayTrace content with
      | .ok count => IO.println s!"Lean replayed {count} native lower-bound cases with exact signed transitions and membership agreement."
      | .error problem => throw <| IO.userError s!"Lean rejected native lower-bound trace: {problem}"
  | _ => throw <| IO.userError "usage: trace-replay <mojo-trace-file>"
