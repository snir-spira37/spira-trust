import SpiraFormalCore.Basic
import SpiraFormalCore.ExplicitList

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain3

structure TerraformPlanEvidence where
  subjectId : SubjectId
  schemaVersion : SchemaVersion
  producerId : ProducerId
  malformedJson : Bool
  unsupportedFormat : Bool
  erroredPlan : Bool
  complete : Bool
  applyable : Bool
  effectiveChanges : Bool
  notEvaluatedItems : ExplicitList NotEvaluatedItem
  notClaimed : ExplicitList NotClaimedItem
  evidenceRefs : ExplicitList EvidenceRef
  proofRefs : ExplicitList ProofRef
  deriving Repr, DecidableEq

def domainId : DomainId := "DOMAIN_3_TERRAFORM_PLAN"

def producerId : ProducerId := "SPIRA_DOMAIN3_TERRAFORM_PLAN_PRODUCER"

def reasonNoChanges : ReasonCode := "TERRAFORM_PLAN_NO_CHANGES"

def reasonResourceChangeBlocked : ReasonCode := "TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"

def reasonNotApplyable : ReasonCode := "TERRAFORM_PLAN_NOT_APPLYABLE"

def reasonErrored : ReasonCode := "TERRAFORM_PLAN_ERRORED"

def reasonIncomplete : ReasonCode := "TERRAFORM_PLAN_INCOMPLETE"

def reasonUnsupportedFormat : ReasonCode := "TERRAFORM_PLAN_FORMAT_UNSUPPORTED"

def reasonJsonInvalid : ReasonCode := "TERRAFORM_PLAN_JSON_INVALID"

def blockingResourceChange : BlockingItem := "terraform_plan_effective_resource_change"

def blockingNotApplyable : BlockingItem := "terraform_plan_not_applyable"

def blockingErrored : BlockingItem := "terraform_plan_errored"

end Domain3
end SpiraFormalCore
