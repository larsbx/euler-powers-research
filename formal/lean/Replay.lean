import ShardPlan

/-!
# E5v1 certificate replay at a Lean-controlled acceptance boundary

This executable parses the exact whitespace-delimited Mojo census format,
rejects malformed, duplicate, out-of-bound, nonprimitive or false identities,
and independently recomputes all integer arithmetic using Lean `Nat`.
It verifies **each reported witness**, not the completeness of the census.
-/

namespace EulerPowers

/-- Canonical ASCII decimal: no signs, spaces or leading zeroes. -/
def canonicalNat (token : String) : Option Nat := do
  let n ← token.toNat?
  if toString n == token then some n else none

def requireSome {α : Type} (value : Option α) (reason : String) : Except String α :=
  match value with
  | some v => .ok v
  | none => .error reason

def parseTuple (line : String) : Option Quintuple := do
  match line.splitOn " " with
  | ["CERT", "E5v1", a, b, c, d, e] =>
      pure ⟨← canonicalNat a, ← canonicalNat b, ← canonicalNat c,
            ← canonicalNat d, ← canonicalNat e⟩
  | _ => none

def parseFooter (line : String) : Option (Nat × Nat) := do
  match line.splitOn " " with
  | ["CENSUS", bound, count] =>
      pure (← canonicalNat bound, ← canonicalNat count)
  | _ => none

/-- Check the canonical file and its individual witnesses.
    The count is a *claim* checked only against the provided record count. -/
def replay (content : String) (expectedBound : Nat) : Except String Nat := do
  let lines := content.splitOn "\n"
  let (footer, rows) ← match lines.reverse with
    | "" :: footer :: revRows => .ok (footer, revRows.reverse)
    | _ => .error "missing final newline or census footer"
  let (bound, claimed) ←
    requireSome (parseFooter footer) "invalid canonical CENSUS footer"
  if bound != expectedBound then
    throw "footer bound does not match requested bound"
  let tuples ← rows.mapM fun row =>
    requireSome (parseTuple row) s!"malformed CERT E5v1 record: {row}"
  if tuples.length != claimed then
    throw "footer count does not match records"
  if !(decide tuples.Nodup) then
    throw "duplicate certificate"
  for tuple in tuples do
    if !check tuple then
      throw "certificate violates exact primitive positive E5 predicate"
    if !(decide (tuple.e ≤ bound)) then
      throw "certificate exceeds declared bound"
  return tuples.length

/-- A height-shard footer has a canonical start, end, and record count. -/
def parseShardFooter (line : String) : Option (Nat × Nat × Nat) := do
  match line.splitOn " " with
  | ["CENSUS", lo, hi, count] =>
      pure (← canonicalNat lo, ← canonicalNat hi, ← canonicalNat count)
  | _ => none

/-- Replay the exact Mojo shard syntax. Unlike full census replay,
the claimed interval is checked at *both* endpoints. -/
def replayShard (content : String) (expectedLo expectedHi : Nat) :
    Except String Nat := do
  if expectedLo < 2 || expectedHi < expectedLo then
    throw "invalid expected shard interval"
  let lines := content.splitOn "\n"
  let (footer, rows) ← match lines.reverse with
    | "" :: footer :: revRows => .ok (footer, revRows.reverse)
    | _ => .error "missing final newline or shard footer"
  let (lo, hi, claimed) ←
    requireSome (parseShardFooter footer) "invalid canonical shard footer"
  if lo != expectedLo || hi != expectedHi then
    throw "shard footer disagrees with declared interval"
  let tuples ← rows.mapM fun row =>
    requireSome (parseTuple row) s!"malformed CERT E5v1 record: {row}"
  if tuples.length != claimed then
    throw "shard footer count does not match records"
  if !(decide tuples.Nodup) then
    throw "duplicate certificate within shard"
  for tuple in tuples do
    if !check tuple then
      throw "shard witness violates primitive positive E5 predicate"
    if tuple.e < lo || hi < tuple.e then
      throw "certificate target outside its declared shard"
  return tuples.length

/-- Canonical pairs for the executable contiguous-plan verifier. -/
def parseIntervals : List String → Option (List (Nat × Nat))
  | [] => some []
  | lo :: hi :: rest => do
      let lower ← canonicalNat lo
      let upper ← canonicalNat hi
      let tail ← parseIntervals rest
      pure ((lower, upper) :: tail)
  | _ => none

end EulerPowers

def main (args : List String) : IO Unit := do
  match args with
  | ["shard", path, lo, hi] =>
      let lower ← match EulerPowers.canonicalNat lo with
        | some n => pure n
        | none => throw <| IO.userError "noncanonical shard start"
      let upper ← match EulerPowers.canonicalNat hi with
        | some n => pure n
        | none => throw <| IO.userError "noncanonical shard end"
      let content ← IO.FS.readFile path
      match EulerPowers.replayShard content lower upper with
      | .ok n => IO.println s!"Lean shard replay accepted {n} exact witness(es) in [{lower},{upper}]; completeness requires plan and search verification."
      | .error problem => throw <| IO.userError s!"Lean shard replay refused: {problem}"
  | "plan" :: bound :: rangeTokens =>
      let upper ← match EulerPowers.canonicalNat bound with
        | some n => pure n
        | none => throw <| IO.userError "noncanonical plan bound"
      let intervals ← match EulerPowers.parseIntervals rangeTokens with
        | some pairs => pure pairs
        | none => throw <| IO.userError "invalid canonical interval pairs"
      if EulerPowers.validPlan upper intervals then
        IO.println s!"Lean accepted contiguous plan through height {upper}; individual shard completeness remains separate."
      else
        throw <| IO.userError "gap, overlap, invalid interval, or incorrect plan endpoints"
  | [path, expected] =>
      let bound ← match EulerPowers.canonicalNat expected with
        | some n => pure n
        | none => throw <| IO.userError "noncanonical expected height"
      let content ← IO.FS.readFile path
      match EulerPowers.replay content bound with
      | .ok n => IO.println s!"Lean replay accepted {n} exact E5v1 witness(es), height ≤ {bound}; exhaustiveness not established."
      | .error problem => throw <| IO.userError s!"Lean replay refused: {problem}"
  | _ => throw <| IO.userError "usage: replay <file> <bound> | shard <file> <lo> <hi> | plan <bound> <lo1> <hi1> ..."
