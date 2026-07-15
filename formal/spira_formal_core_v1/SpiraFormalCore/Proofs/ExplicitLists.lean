import SpiraFormalCore.Core

set_option autoImplicit false

namespace SpiraFormalCore

theorem assembleContract_preserves_reasonCodes
    (evidence : TypedEvidence) (policy : PolicyContext) (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) :
    (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
      notClaimed evidenceRefs proofRefs).reasonCodes = reasonCodes := by
  rfl

theorem assembleContract_preserves_blockingItems
    (evidence : TypedEvidence) (policy : PolicyContext) (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) :
    (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
      notClaimed evidenceRefs proofRefs).blockingItems = blockingItems := by
  rfl

theorem assembleContract_preserves_notEvaluated
    (evidence : TypedEvidence) (policy : PolicyContext) (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) :
    (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
      notClaimed evidenceRefs proofRefs).notEvaluated = notEvaluated := by
  rfl

theorem assembleContract_preserves_notClaimed
    (evidence : TypedEvidence) (policy : PolicyContext) (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) :
    (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
      notClaimed evidenceRefs proofRefs).notClaimed = notClaimed := by
  rfl

theorem assembleContract_preserves_evidenceRefs
    (evidence : TypedEvidence) (policy : PolicyContext) (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) :
    (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
      notClaimed evidenceRefs proofRefs).evidenceRefs = evidenceRefs := by
  rfl

theorem assembleContract_preserves_proofRefs
    (evidence : TypedEvidence) (policy : PolicyContext) (action : Action)
    (reasonCodes : ExplicitList ReasonCode)
    (blockingItems : ExplicitList BlockingItem)
    (notEvaluated : ExplicitList NotEvaluatedItem)
    (notClaimed : ExplicitList NotClaimedItem)
    (evidenceRefs : ExplicitList EvidenceRef)
    (proofRefs : ExplicitList ProofRef) :
    (assembleContract evidence policy action reasonCodes blockingItems notEvaluated
      notClaimed evidenceRefs proofRefs).proofRefs = proofRefs := by
  rfl

end SpiraFormalCore
