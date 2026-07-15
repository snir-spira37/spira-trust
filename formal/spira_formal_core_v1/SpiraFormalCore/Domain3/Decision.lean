import SpiraFormalCore.Action
import SpiraFormalCore.Contract
import SpiraFormalCore.Domain3.Evidence
import SpiraFormalCore.Domain3.Policy

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain3

def formalAction (evidence : TerraformPlanEvidence) : Action :=
  if evidence.malformedJson then
    Action.RERUN_REQUIRED
  else if evidence.unsupportedFormat || !evidence.complete then
    Action.REPORT_NOT_EVALUATED
  else if evidence.erroredPlan then
    Action.STOP_BLOCKED
  else if !evidence.applyable && evidence.effectiveChanges then
    Action.STOP_BLOCKED
  else if evidence.effectiveChanges then
    Action.STOP_BLOCKED
  else
    Action.PROCEED

def formalReasonCodes (evidence : TerraformPlanEvidence) : ExplicitList ReasonCode :=
  if evidence.malformedJson then
    ExplicitList.singleton reasonJsonInvalid
  else if evidence.unsupportedFormat then
    ExplicitList.singleton reasonUnsupportedFormat
  else if !evidence.complete then
    ExplicitList.singleton reasonIncomplete
  else if evidence.erroredPlan then
    ExplicitList.singleton reasonErrored
  else if !evidence.applyable && evidence.effectiveChanges then
    ExplicitList.singleton reasonNotApplyable
  else if evidence.effectiveChanges then
    ExplicitList.singleton reasonResourceChangeBlocked
  else
    ExplicitList.singleton reasonNoChanges

def formalNotEvaluated (evidence : TerraformPlanEvidence) : ExplicitList NotEvaluatedItem :=
  evidence.notEvaluatedItems

def formalNotClaimed (evidence : TerraformPlanEvidence) : ExplicitList NotClaimedItem :=
  evidence.notClaimed

def formalContract (evidence : TerraformPlanEvidence) : MachineContract :=
  { domainId := domainId
    subjectId := evidence.subjectId
    policyId := (policy evidence.schemaVersion).policyId
    schemaVersion := evidence.schemaVersion
    producerId := evidence.producerId
    contractId := defaultContractId
    action := formalAction evidence
    stop := (formalAction evidence).stop
    reasonCodes := formalReasonCodes evidence
    blockingItems :=
      if (formalAction evidence) == Action.STOP_BLOCKED then
        if evidence.erroredPlan then ExplicitList.singleton blockingErrored
        else if !evidence.applyable && evidence.effectiveChanges then ExplicitList.singleton blockingNotApplyable
        else ExplicitList.singleton blockingResourceChange
      else ExplicitList.empty
    notEvaluated := evidence.notEvaluatedItems
    notClaimed := evidence.notClaimed
    evidenceRefs := evidence.evidenceRefs
    proofRefs := evidence.proofRefs }

end Domain3
end SpiraFormalCore
