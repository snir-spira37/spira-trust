import SpiraFormalCore.Action
import SpiraFormalCore.Contract
import SpiraFormalCore.Errors
import SpiraFormalCore.Evidence
import SpiraFormalCore.Policy

set_option autoImplicit false

namespace SpiraFormalCore

def validateTypedEvidence (evidence : TypedEvidence) (policy : PolicyContext) : Option CoreError :=
  match evidence.validity with
  | EvidenceValidity.valid =>
      if evidence.schemaVersion == policy.schemaVersion then
        none
      else
        some CoreError.incompatibleVersion
  | EvidenceValidity.invalid => some CoreError.invalidTypedEvidence
  | EvidenceValidity.incomplete => some CoreError.incompleteTypedEvidence
  | EvidenceValidity.conflicting => some CoreError.conflictingTypedEvidence
  | EvidenceValidity.versionIncompatible => some CoreError.incompatibleVersion
  | EvidenceValidity.internalFailure => some CoreError.internalValidationFailure

def aggregateClaims (evidence : TypedEvidence) : ExplicitList TypedClaim :=
  evidence.claims

def deriveReasonCodes (claims : ExplicitList TypedClaim) : ExplicitList ReasonCode :=
  { items := claims.items.filterMap (fun claim =>
      match claim with
      | TypedClaim.reason reason => some reason
      | _ => none) }

def deriveBlockingItems (claims : ExplicitList TypedClaim) : ExplicitList BlockingItem :=
  { items := claims.items.filterMap (fun claim =>
      match claim with
      | TypedClaim.blocking item => some item
      | _ => none) }

def deriveNotEvaluated (claims : ExplicitList TypedClaim) : ExplicitList NotEvaluatedItem :=
  { items := claims.items.filterMap (fun claim =>
      match claim with
      | TypedClaim.notEvaluated item => some item
      | _ => none) }

def deriveNotClaimed (claims : ExplicitList TypedClaim) : ExplicitList NotClaimedItem :=
  { items := claims.items.filterMap (fun claim =>
      match claim with
      | TypedClaim.notClaimed item => some item
      | _ => none) }

def deriveEvidenceRefs (claims : ExplicitList TypedClaim) (evidence : TypedEvidence) : ExplicitList EvidenceRef :=
  evidence.evidenceRefs.append
    { items := claims.items.filterMap (fun claim =>
        match claim with
        | TypedClaim.evidenceRef ref => some ref
        | _ => none) }

def deriveProofRefs (claims : ExplicitList TypedClaim) (evidence : TypedEvidence) : ExplicitList ProofRef :=
  evidence.proofRefs.append
    { items := claims.items.filterMap (fun claim =>
        match claim with
        | TypedClaim.proofRef ref => some ref
        | _ => none) }

def decideAction
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem) : Action :=
  if !blockingItems.isEmpty then
    Action.STOP_BLOCKED
  else if !notEvaluated.isEmpty then
    Action.REPORT_NOT_EVALUATED
  else
    Action.PROCEED

def failClosedReason (error : CoreError) : ReasonCode :=
  match error with
  | CoreError.invalidTypedEvidence => "INVALID_TYPED_EVIDENCE"
  | CoreError.incompleteTypedEvidence => "INCOMPLETE_TYPED_EVIDENCE"
  | CoreError.conflictingTypedEvidence => "CONFLICTING_TYPED_EVIDENCE"
  | CoreError.incompatibleVersion => "INCOMPATIBLE_VERSION"
  | CoreError.internalValidationFailure => "INTERNAL_VALIDATION_FAILURE"

def failClosedAction (error : CoreError) : Action :=
  match error with
  | CoreError.incompleteTypedEvidence => Action.REPORT_NOT_EVALUATED
  | CoreError.incompatibleVersion => Action.REPORT_NOT_EVALUATED
  | _ => Action.STOP_BLOCKED

def assembleContract
    (evidence : TypedEvidence)
    (policy : PolicyContext)
    (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) : MachineContract :=
  { domainId := evidence.domainId
    subjectId := evidence.subjectId
    policyId := policy.policyId
    schemaVersion := policy.schemaVersion
    producerId := evidence.producerId
    contractId := defaultContractId
    action := action
    stop := action.stop
    reasonCodes := reasonCodes
    blockingItems := blockingItems
    notEvaluated := notEvaluated
    notClaimed := notClaimed
    evidenceRefs := evidenceRefs
    proofRefs := proofRefs }

def assembleFailClosedContract
    (evidence : TypedEvidence)
    (policy : PolicyContext)
    (error : CoreError) : MachineContract :=
  let action := failClosedAction error
  assembleContract evidence policy action
    (ExplicitList.singleton (failClosedReason error))
    ExplicitList.empty
    (match error with
      | CoreError.incompleteTypedEvidence => ExplicitList.singleton "required information unavailable"
      | CoreError.incompatibleVersion => ExplicitList.singleton "schema version incompatible"
      | _ => ExplicitList.empty)
    policy.notClaimedRules
    evidence.evidenceRefs
    evidence.proofRefs

def core (evidence : TypedEvidence) (policy : PolicyContext) : CoreResult :=
  match validateTypedEvidence evidence policy with
  | some error => CoreResult.error error (assembleFailClosedContract evidence policy error)
  | none =>
      let claims := aggregateClaims evidence
      let reasonCodes := deriveReasonCodes claims
      let blockingItems := deriveBlockingItems claims
      let notEvaluated := deriveNotEvaluated claims
      let notClaimed := deriveNotClaimed claims
      let evidenceRefs := deriveEvidenceRefs claims evidence
      let proofRefs := deriveProofRefs claims evidence
      let action := decideAction blockingItems notEvaluated
      CoreResult.ok
        (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
          notClaimed evidenceRefs proofRefs)

end SpiraFormalCore
