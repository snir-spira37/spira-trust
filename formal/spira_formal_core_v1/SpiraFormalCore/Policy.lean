import SpiraFormalCore.Basic
import SpiraFormalCore.ExplicitList

set_option autoImplicit false

namespace SpiraFormalCore

structure PolicyContext where
  policyId : PolicyId
  schemaVersion : SchemaVersion
  requiredClaims : ExplicitList NotEvaluatedItem
  blockingRules : ExplicitList BlockingItem
  notClaimedRules : ExplicitList NotClaimedItem
  requiredEvidenceRefs : ExplicitList EvidenceRef
  requiredProofRefs : ExplicitList ProofRef
  deriving Repr, DecidableEq

end SpiraFormalCore
