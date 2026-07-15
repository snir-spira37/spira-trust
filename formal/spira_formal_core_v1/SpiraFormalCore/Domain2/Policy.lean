import SpiraFormalCore.Policy
import SpiraFormalCore.Domain2.Evidence

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain2

def policy (schemaVersion : SchemaVersion) : PolicyContext :=
  { policyId := "FORMAL_CORE_V1_DOMAIN2_POLICY"
    schemaVersion := schemaVersion
    requiredClaims := ExplicitList.empty
    blockingRules := ExplicitList.singleton blockingFailedTest
    notClaimedRules := { items := ["software_safety", "producer_correctness"] }
    requiredEvidenceRefs := ExplicitList.empty
    requiredProofRefs := ExplicitList.empty }

end Domain2
end SpiraFormalCore
