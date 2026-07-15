import SpiraFormalCore.Policy
import SpiraFormalCore.Domain3.Evidence

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain3

def policy (schemaVersion : SchemaVersion) : PolicyContext :=
  { policyId := "FORMAL_CORE_V1_DOMAIN3_POLICY"
    schemaVersion := schemaVersion
    requiredClaims := ExplicitList.empty
    blockingRules := { items := [blockingResourceChange, blockingNotApplyable, blockingErrored] }
    notClaimedRules :=
      { items :=
          [ "APPLY_SUCCESS"
          , "INFRASTRUCTURE_COMPLIANCE"
          , "INFRASTRUCTURE_CORRECTNESS"
          , "INFRASTRUCTURE_COST"
          , "INFRASTRUCTURE_SECURITY"
          , "LIVE_STATE_FRESHNESS" ] }
    requiredEvidenceRefs := ExplicitList.empty
    requiredProofRefs := ExplicitList.empty }

end Domain3
end SpiraFormalCore
