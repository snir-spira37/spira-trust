import SpiraFormalCore.Basic
import SpiraFormalCore.ExplicitList

set_option autoImplicit false

namespace SpiraFormalCore

inductive EvidenceValidity where
  | valid
  | invalid
  | incomplete
  | conflicting
  | versionIncompatible
  | internalFailure
  deriving Repr, DecidableEq

inductive TypedClaim where
  | reason : ReasonCode -> TypedClaim
  | blocking : BlockingItem -> TypedClaim
  | notEvaluated : NotEvaluatedItem -> TypedClaim
  | notClaimed : NotClaimedItem -> TypedClaim
  | evidenceRef : EvidenceRef -> TypedClaim
  | proofRef : ProofRef -> TypedClaim
  deriving Repr, DecidableEq

structure TypedEvidence where
  domainId : DomainId
  subjectId : SubjectId
  schemaVersion : SchemaVersion
  producerId : ProducerId
  validity : EvidenceValidity
  claims : ExplicitList TypedClaim
  evidenceRefs : ExplicitList EvidenceRef
  proofRefs : ExplicitList ProofRef
  deriving Repr, DecidableEq

end SpiraFormalCore
