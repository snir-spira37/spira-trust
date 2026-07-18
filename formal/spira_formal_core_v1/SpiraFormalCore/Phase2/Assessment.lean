set_option autoImplicit false

namespace SpiraFormalCore
namespace Phase2

inductive Phase2Assessment where
  | TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  | TRUST_INSUFFICIENT
  | TRUST_NOT_EVALUATED
  deriving Repr, DecidableEq

structure SubVerdicts where
  signature : Phase2Assessment
  identity : Phase2Assessment
  authority : Phase2Assessment
  isolation : Phase2Assessment
  deriving Repr, DecidableEq

def executionMarker : String :=
  "ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION"

def Phase2Assessment.asString : Phase2Assessment -> String
  | Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS =>
      "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
  | Phase2Assessment.TRUST_INSUFFICIENT => "TRUST_INSUFFICIENT"
  | Phase2Assessment.TRUST_NOT_EVALUATED => "TRUST_NOT_EVALUATED"

def allPhase2Assessments : List Phase2Assessment :=
  [ Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  , Phase2Assessment.TRUST_INSUFFICIENT
  , Phase2Assessment.TRUST_NOT_EVALUATED
  ]

def allSubVerdicts : List SubVerdicts :=
  allPhase2Assessments.flatMap fun signature =>
  allPhase2Assessments.flatMap fun identity =>
  allPhase2Assessments.flatMap fun authority =>
  allPhase2Assessments.map fun isolation =>
    { signature := signature
      identity := identity
      authority := authority
      isolation := isolation }

def expectedSubVerdictCount : Nat := 81

end Phase2
end SpiraFormalCore
