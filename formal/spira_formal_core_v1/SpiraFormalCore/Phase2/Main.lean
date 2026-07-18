import SpiraFormalCore.Phase2.Proofs

set_option autoImplicit false

namespace SpiraFormalCore
namespace Phase2

def jsonField (name value : String) : String :=
  "\"" ++ name ++ "\":\"" ++ value ++ "\""

def jsonArray (items : List String) : String :=
  "[" ++ String.intercalate "," (items.map fun item => "\"" ++ item ++ "\"") ++ "]"

def assumptionIdsJson (assumptions : AssumptionSet) : String :=
  jsonArray assumptions.idStrings

def sourcesForDomain (name : String) (verdict : Phase2Assessment) : List String :=
  if isEvaluated verdict then [name ++ "_sub.assumptions"] else []

def rootsForDomain (name : String) (verdict : Phase2Assessment) : List String :=
  if isEvaluated verdict then [name ++ "_sub.trust_roots_used"] else []

def sourceNames (sv : SubVerdicts) : List String :=
  sourcesForDomain "signature" sv.signature ++
  sourcesForDomain "identity" sv.identity ++
  sourcesForDomain "authority" sv.authority ++
  sourcesForDomain "isolation" sv.isolation

def rootNames (sv : SubVerdicts) : List String :=
  rootsForDomain "signature" sv.signature ++
  rootsForDomain "identity" sv.identity ++
  rootsForDomain "authority" sv.authority ++
  rootsForDomain "isolation" sv.isolation

def rowId (idx : Nat) : String :=
  if idx < 10 then
    "NESIRA-P2-ASSESS-00" ++ toString idx
  else if idx < 100 then
    "NESIRA-P2-ASSESS-0" ++ toString idx
  else
    "NESIRA-P2-ASSESS-" ++ toString idx

def subVerdictsJsonFields (sv : SubVerdicts) : String :=
  String.intercalate ","
    [ jsonField "signature_sub" sv.signature.asString
    , jsonField "identity_sub" sv.identity.asString
    , jsonField "authority_sub" sv.authority.asString
    , jsonField "isolation_sub" sv.isolation.asString
    ]

def breakdownJsonFields (sv : SubVerdicts) : String :=
  String.intercalate ","
    [ jsonField "signature" sv.signature.asString
    , jsonField "identity" sv.identity.asString
    , jsonField "authority" sv.authority.asString
    , jsonField "isolation" sv.isolation.asString
    ]

def dumpLine (idx : Nat) (sv : SubVerdicts) : String :=
  let contract := compose sv
  "{" ++
    String.intercalate ","
      [ jsonField "row_id" (rowId idx)
      , "\"inputs\":{" ++ subVerdictsJsonFields sv ++ "}"
      , jsonField "composite_verdict" contract.verdict.asString
      , "\"carried_assumptions\":" ++ assumptionIdsJson contract.carriedAssumptions
      , "\"per_domain_breakdown\":{" ++ breakdownJsonFields contract.breakdown ++ "}"
      , "\"trust_roots_used_sources\":" ++ jsonArray (rootNames sv)
      , "\"sub_assumption_sources_included\":" ++ jsonArray (sourceNames sv)
      , jsonField "execution_marker" contract.executionMarker
      ] ++
  "}"

def enumerateFrom : Nat -> List SubVerdicts -> List (Prod Nat SubVerdicts)
  | _, [] => []
  | idx, sv :: rest => (idx, sv) :: enumerateFrom (idx + 1) rest

def dumpLines : List String :=
  (enumerateFrom 1 allSubVerdicts).map fun pair => dumpLine pair.fst pair.snd

def expectedDumpLineCount : Nat := 81

def actualDumpLineCount : Nat := dumpLines.length

def main : IO Unit := do
  for line in dumpLines do
    IO.println line

end Phase2
end SpiraFormalCore

def main : IO Unit :=
  SpiraFormalCore.Phase2.main
