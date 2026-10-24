import EulerPowers

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
    (parseFooter footer).toExcept "invalid canonical CENSUS footer"
  if bound != expectedBound then
    throw "footer bound does not match requested bound"
  let tuples ← rows.mapM fun row =>
    (parseTuple row).toExcept s!"malformed CERT E5v1 record: {row}"
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

end EulerPowers

def main (args : List String) : IO Unit := do
  match args with
  | [path, expected] =>
      let bound ← match EulerPowers.canonicalNat expected with
        | some n => pure n
        | none => throw <| IO.userError "noncanonical expected height"
      let content ← IO.FS.readFile path
      match EulerPowers.replay content bound with
      | .ok n => IO.println s!"Lean replay accepted {n} exact E5v1 witness(es), height ≤ {bound}; exhaustiveness not established."
      | .error problem => throw <| IO.userError s!"Lean replay refused: {problem}"
  | _ => throw <| IO.userError "usage: replay <certificate-file> <expected-height>"
