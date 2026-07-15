import SpiraFormalCore.Domain3.Decision

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain3

theorem effective_resource_changes_prevent_proceed
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = false)
    (hUnsupported : evidence.unsupportedFormat = false)
    (hComplete : evidence.complete = true)
    (hErrored : evidence.erroredPlan = false)
    (hChanges : evidence.effectiveChanges = true) :
    formalAction evidence != Action.PROCEED := by
  cases hApplyable : evidence.applyable <;>
    simp [formalAction, hMalformed, hUnsupported, hComplete, hErrored, hChanges, hApplyable]

theorem errored_plan_prevents_proceed
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = false)
    (hUnsupported : evidence.unsupportedFormat = false)
    (hComplete : evidence.complete = true)
    (hErrored : evidence.erroredPlan = true) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hMalformed, hUnsupported, hComplete, hErrored]

theorem not_applyable_with_changes_prevents_proceed
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = false)
    (hUnsupported : evidence.unsupportedFormat = false)
    (hComplete : evidence.complete = true)
    (hErrored : evidence.erroredPlan = false)
    (hApplyable : evidence.applyable = false)
    (hChanges : evidence.effectiveChanges = true) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hMalformed, hUnsupported, hComplete, hErrored, hApplyable, hChanges]

theorem malformed_json_rerun_required
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = true) :
    formalAction evidence = Action.RERUN_REQUIRED := by
  simp [formalAction, hMalformed]

theorem unsupported_format_report_not_evaluated
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = false)
    (hUnsupported : evidence.unsupportedFormat = true) :
    formalAction evidence = Action.REPORT_NOT_EVALUATED := by
  simp [formalAction, hMalformed, hUnsupported]

theorem incomplete_plan_report_not_evaluated
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = false)
    (hUnsupported : evidence.unsupportedFormat = false)
    (hComplete : evidence.complete = false) :
    formalAction evidence = Action.REPORT_NOT_EVALUATED := by
  simp [formalAction, hMalformed, hUnsupported, hComplete]

theorem valid_no_change_produces_proceed
    (evidence : TerraformPlanEvidence)
    (hMalformed : evidence.malformedJson = false)
    (hUnsupported : evidence.unsupportedFormat = false)
    (hComplete : evidence.complete = true)
    (hErrored : evidence.erroredPlan = false)
    (hApplyable : evidence.applyable = true)
    (hChanges : evidence.effectiveChanges = false) :
    formalAction evidence = Action.PROCEED := by
  simp [formalAction, hMalformed, hUnsupported, hComplete, hErrored, hApplyable, hChanges]

theorem not_claimed_boundaries_preserved
    (evidence : TerraformPlanEvidence) :
    formalNotClaimed evidence = evidence.notClaimed := by
  simp [formalNotClaimed]

theorem unknown_or_sensitive_not_evaluated_preserved
    (evidence : TerraformPlanEvidence) :
    formalNotEvaluated evidence = evidence.notEvaluatedItems := by
  simp [formalNotEvaluated]

end Domain3
end SpiraFormalCore
