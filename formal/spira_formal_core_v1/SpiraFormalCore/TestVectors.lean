import SpiraFormalCore.Reference

set_option autoImplicit false

namespace SpiraFormalCore

def vectorPolicy : PolicyContext :=
  { policyId := "FORMAL_CORE_V1_POLICY"
    schemaVersion := "FORMAL_CORE_V1_SCHEMA"
    requiredClaims := ExplicitList.empty
    blockingRules := ExplicitList.empty
    notClaimedRules := { items := ["software_safety"] }
    requiredEvidenceRefs := ExplicitList.empty
    requiredProofRefs := ExplicitList.empty }

def vectorEvidence
    (validity : EvidenceValidity)
    (schemaVersion : SchemaVersion)
    (claims : ExplicitList TypedClaim) : TypedEvidence :=
  { domainId := "reference"
    subjectId := "typed-vector"
    schemaVersion := schemaVersion
    producerId := "formal-reference"
    validity := validity
    claims := claims
    evidenceRefs := { items := ["evidence:typed-vector"] }
    proofRefs := { items := ["proof:typed-vector"] } }

def validProceedEvidence : TypedEvidence :=
  vectorEvidence EvidenceValidity.valid vectorPolicy.schemaVersion
    { items := [TypedClaim.reason "TESTS_PASSED"] }

def blockingEvidence : TypedEvidence :=
  vectorEvidence EvidenceValidity.valid vectorPolicy.schemaVersion
    { items := [TypedClaim.reason "BLOCKING_FINDING", TypedClaim.blocking "failing_test"] }

def requiredUnknownEvidence : TypedEvidence :=
  vectorEvidence EvidenceValidity.valid vectorPolicy.schemaVersion
    { items := [TypedClaim.reason "REQUIRED_UNKNOWN",
        TypedClaim.notEvaluated "required_test_result_missing"] }

def conflictingEvidence : TypedEvidence :=
  vectorEvidence EvidenceValidity.conflicting vectorPolicy.schemaVersion
    { items := [TypedClaim.reason "CONFLICTING_EVIDENCE"] }

def invalidEvidence : TypedEvidence :=
  vectorEvidence EvidenceValidity.invalid vectorPolicy.schemaVersion
    { items := [TypedClaim.reason "INVALID_EVIDENCE"] }

def incompatibleEvidence : TypedEvidence :=
  vectorEvidence EvidenceValidity.valid "OTHER_SCHEMA"
    { items := [TypedClaim.reason "VERSION_MISMATCH"] }

def proceedVectorCheck : ReferenceCheck :=
  { name := "valid proceed vector"
    passed := eqBool (referenceAction validProceedEvidence vectorPolicy) Action.PROCEED }

def blockingVectorCheck : ReferenceCheck :=
  { name := "blocking vector"
    passed := eqBool (referenceAction blockingEvidence vectorPolicy) Action.STOP_BLOCKED }

def requiredUnknownVectorCheck : ReferenceCheck :=
  { name := "required unknown vector"
    passed := eqBool (referenceAction requiredUnknownEvidence vectorPolicy)
      Action.REPORT_NOT_EVALUATED }

def conflictingVectorCheck : ReferenceCheck :=
  { name := "conflicting evidence vector"
    passed := eqBool (referenceAction conflictingEvidence vectorPolicy) Action.STOP_BLOCKED }

def invalidVectorCheck : ReferenceCheck :=
  { name := "invalid evidence vector"
    passed := eqBool (referenceAction invalidEvidence vectorPolicy) Action.STOP_BLOCKED }

def incompatibleVectorCheck : ReferenceCheck :=
  { name := "version-incompatible vector"
    passed := eqBool (referenceAction incompatibleEvidence vectorPolicy)
      Action.REPORT_NOT_EVALUATED }

def gateAPreservationVectorCheck : ReferenceCheck :=
  let contract := evaluateContract validProceedEvidence vectorPolicy
  { name := "Gate A preservation vector"
    passed := eqBool (projectDomainContract (gateAWrap contract)) contract }

def modelNonAuthorityVectorCheck : ReferenceCheck :=
  let contract := evaluateContract blockingEvidence vectorPolicy
  let explanation : ModelExplanation := { text := "The model asks to proceed, but this is non-authoritative." }
  { name := "model-non-authority vector"
    passed := eqBool (executedAction contract explanation) contract.action }

def referenceChecks : List ReferenceCheck :=
  [ proceedVectorCheck
  , blockingVectorCheck
  , requiredUnknownVectorCheck
  , conflictingVectorCheck
  , invalidVectorCheck
  , incompatibleVectorCheck
  , gateAPreservationVectorCheck
  , modelNonAuthorityVectorCheck
  ]

end SpiraFormalCore
