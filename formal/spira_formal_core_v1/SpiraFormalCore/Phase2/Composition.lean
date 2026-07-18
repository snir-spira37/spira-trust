import SpiraFormalCore.Phase2.Assumptions

set_option autoImplicit false

namespace SpiraFormalCore
namespace Phase2

structure AssessmentContract where
  verdict : Phase2Assessment
  carriedAssumptions : AssumptionSet
  breakdown : SubVerdicts
  executionMarker : String
  deriving Repr, DecidableEq

def isSufficient : Phase2Assessment -> Bool
  | Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS => true
  | Phase2Assessment.TRUST_INSUFFICIENT => false
  | Phase2Assessment.TRUST_NOT_EVALUATED => false

def isInsufficient : Phase2Assessment -> Bool
  | Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS => false
  | Phase2Assessment.TRUST_INSUFFICIENT => true
  | Phase2Assessment.TRUST_NOT_EVALUATED => false

def isEvaluated : Phase2Assessment -> Bool
  | Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS => true
  | Phase2Assessment.TRUST_INSUFFICIENT => true
  | Phase2Assessment.TRUST_NOT_EVALUATED => false

def allSufficient (sv : SubVerdicts) : Bool :=
  isSufficient sv.signature &&
  isSufficient sv.identity &&
  isSufficient sv.authority &&
  isSufficient sv.isolation

def anyInsufficient (sv : SubVerdicts) : Bool :=
  isInsufficient sv.signature ||
  isInsufficient sv.identity ||
  isInsufficient sv.authority ||
  isInsufficient sv.isolation

def verdictOf (sv : SubVerdicts) : Phase2Assessment :=
  if allSufficient sv then
    Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  else if anyInsufficient sv then
    Phase2Assessment.TRUST_INSUFFICIENT
  else
    Phase2Assessment.TRUST_NOT_EVALUATED

def domainAssumptions (verdict : Phase2Assessment) (assumptions : AssumptionSet) : AssumptionSet :=
  if isEvaluated verdict then assumptions else emptyAssumptions

def carriedAssumptionsOf (sv : SubVerdicts) : AssumptionSet :=
  ((((floorAssumptions.union (domainAssumptions sv.signature signatureAssumptions)).union
    (domainAssumptions sv.identity identityAssumptions)).union
    (domainAssumptions sv.authority authorityAssumptions)).union
    (domainAssumptions sv.isolation isolationAssumptions))

def compose (sv : SubVerdicts) : AssessmentContract :=
  { verdict := verdictOf sv
    carriedAssumptions := carriedAssumptionsOf sv
    breakdown := sv
    executionMarker := executionMarker }

end Phase2
end SpiraFormalCore
