import SpiraFormalCore.Domain4.Evidence

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain4

structure Policy where
  policyId : String
  schemaVersion : String
  deriving Repr, DecidableEq

def defaultPolicy : Policy :=
  { policyId := "SPIRA_NESIRA_PHASE1_POLICY"
    schemaVersion := "SPIRA_NESIRA_DOMAIN4_FLAGS_V2" }

def consultsEvidenceChecks : ArtifactKind -> Bool
  | ArtifactKind.SEVERANCE_AUTHORIZATION => false
  | ArtifactKind.LEGACY_ISOLATION_RESULT => true

def consultsTemporalBinding : ArtifactKind -> Bool
  | ArtifactKind.SEVERANCE_AUTHORIZATION => true
  | ArtifactKind.LEGACY_ISOLATION_RESULT => false

end Domain4
end SpiraFormalCore
