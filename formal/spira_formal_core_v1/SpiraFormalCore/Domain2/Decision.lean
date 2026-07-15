import SpiraFormalCore.Core
import SpiraFormalCore.Domain2.Evidence
import SpiraFormalCore.Domain2.Policy

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain2

def requiredUnknownClaims : List NotEvaluatedItem -> List TypedClaim
  | [] => []
  | item :: rest => TypedClaim.notEvaluated item :: requiredUnknownClaims rest

def notClaimedClaims : List NotClaimedItem -> List TypedClaim
  | [] => []
  | item :: rest => TypedClaim.notClaimed item :: notClaimedClaims rest

def baseClaims (evidence : PytestEvidence) : List TypedClaim :=
  if evidence.noteOnly then
    [TypedClaim.reason reasonTestNotes]
  else if evidence.testsPassed then
    [TypedClaim.reason reasonTestsPassed]
  else
    []

def blockingClaims (evidence : PytestEvidence) : List TypedClaim :=
  if evidence.failedTestCount > 0 then
    [TypedClaim.reason reasonTestFailure, TypedClaim.blocking blockingFailedTest]
  else if !evidence.collectionSucceeded || evidence.executionError then
    [TypedClaim.reason reasonTestFailure, TypedClaim.blocking blockingCollectionOrExecution]
  else
    []

def domainClaims (evidence : PytestEvidence) : ExplicitList TypedClaim :=
  { items :=
      baseClaims evidence ++
      blockingClaims evidence ++
      requiredUnknownClaims evidence.requiredUnknown.items }

def validity (evidence : PytestEvidence) : EvidenceValidity :=
  if evidence.versionIncompatible then
    EvidenceValidity.versionIncompatible
  else if evidence.malformedEvidence then
    EvidenceValidity.invalid
  else if evidence.conflictPresent then
    EvidenceValidity.conflicting
  else
    EvidenceValidity.valid

def toTypedEvidence (evidence : PytestEvidence) : TypedEvidence :=
  { domainId := domainId
    subjectId := evidence.subjectId
    schemaVersion := evidence.schemaVersion
    producerId := evidence.producerId
    validity := validity evidence
    claims := domainClaims evidence
    evidenceRefs := evidence.evidenceRefs
    proofRefs := evidence.proofRefs }

def evaluate (evidence : PytestEvidence) : CoreResult :=
  core (toTypedEvidence evidence) (policy evidence.schemaVersion)

def contract (evidence : PytestEvidence) : MachineContract :=
  { (evaluate evidence).contract with notClaimed := evidence.notClaimed }

def formalAction (evidence : PytestEvidence) : Action :=
  if evidence.versionIncompatible then
    Action.REPORT_NOT_EVALUATED
  else if evidence.conflictPresent then
    Action.RERUN_REQUIRED
  else if evidence.malformedEvidence then
    Action.STOP_BLOCKED
  else if evidence.failedTestCount > 0 || !evidence.collectionSucceeded || evidence.executionError then
    Action.STOP_BLOCKED
  else if !evidence.requiredUnknown.isEmpty then
    Action.REPORT_NOT_EVALUATED
  else
    Action.PROCEED

def formalReasonCodes (evidence : PytestEvidence) : ExplicitList ReasonCode :=
  if evidence.versionIncompatible then
    ExplicitList.singleton reasonVersionIncompatible
  else if evidence.malformedEvidence then
    ExplicitList.singleton reasonMalformed
  else if evidence.conflictPresent then
    ExplicitList.singleton reasonConflict
  else if evidence.failedTestCount > 0 || !evidence.collectionSucceeded || evidence.executionError then
    ExplicitList.singleton reasonTestFailure
  else if evidence.noteOnly then
    ExplicitList.singleton reasonTestNotes
  else if evidence.testsPassed then
    ExplicitList.singleton reasonTestsPassed
  else
    ExplicitList.empty

def formalNotClaimed (evidence : PytestEvidence) : ExplicitList NotClaimedItem :=
  evidence.notClaimed

end Domain2
end SpiraFormalCore
