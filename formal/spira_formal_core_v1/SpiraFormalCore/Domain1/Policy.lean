import SpiraFormalCore.Policy
import SpiraFormalCore.Domain1.Evidence

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain1

def policy (schemaVersion : SchemaVersion) : PolicyContext :=
  { policyId := "SPIRA_FORMAL_CORE_V1_DOMAIN1_POLICY"
    schemaVersion := schemaVersion
    requiredClaims := ExplicitList.singleton requiredArtifactCheck
    blockingRules := ExplicitList.singleton "blocking_artifact_finding"
    notClaimedRules := ExplicitList.empty
    requiredEvidenceRefs := ExplicitList.empty
    requiredProofRefs := ExplicitList.empty }

end Domain1
end SpiraFormalCore
