import SpiraFormalCore.Basic
import SpiraFormalCore.ExplicitList

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain1

inductive LegacyAction where
  | PROCEED
  | ASK_HUMAN
  | STOP_BLOCKED
  | REPORT_NOT_EVALUATED
  deriving Repr, DecidableEq

inductive WorstClaimStatus where
  | OK
  | NOTE
  | WARN
  | NOT_EVALUATED
  | RERUN_REQUIRED
  | BLOCK
  deriving Repr, DecidableEq

structure PythonArtifactEvidence where
  artifactId : SubjectId
  subjectId : SubjectId
  schemaVersion : SchemaVersion
  producerId : ProducerId
  legacyAction : LegacyAction
  worstClaimStatus : WorstClaimStatus
  reasonCodes : ExplicitList ReasonCode
  notEvaluatedItems : ExplicitList NotEvaluatedItem
  notClaimed : ExplicitList NotClaimedItem
  artifactIdentityRef : EvidenceRef
  claimsIdentityRef : EvidenceRef
  contextIdentityRef : EvidenceRef
  decisionIdentityRef : EvidenceRef
  compactReferenceRef : ProofRef
  proofIdentityRef : ProofRef
  deriving Repr, DecidableEq

def domainId : DomainId := "DOMAIN_1_PYTHON_ARTIFACT"

def producerId : ProducerId := "SPIRA_DOMAIN1_IDENTITY_BASELINE"

def reasonHumanReviewRequired : ReasonCode := "HUMAN_REVIEW_REQUIRED"

def reasonReportNotEvaluated : ReasonCode := "REPORT_NOT_EVALUATED"

def reasonBlockingFindings : ReasonCode := "BLOCKING_FINDINGS"

def requiredArtifactCheck : NotEvaluatedItem := "target_environment"

end Domain1
end SpiraFormalCore
