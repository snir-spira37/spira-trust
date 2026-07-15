set_option autoImplicit false

namespace SpiraFormalCore

abbrev DomainId := String
abbrev SubjectId := String
abbrev PolicyId := String
abbrev SchemaVersion := String
abbrev ProducerId := String
abbrev ContractId := String
abbrev UnifiedWrapperId := String

abbrev EvidenceRef := String
abbrev ProofRef := String
abbrev ReasonCode := String
abbrev BlockingItem := String
abbrev NotEvaluatedItem := String
abbrev NotClaimedItem := String

def defaultContractId : ContractId := "FORMAL_CORE_V1_CONTRACT"
def defaultUnifiedWrapperId : UnifiedWrapperId := "FORMAL_CORE_V1_GATE_A"

end SpiraFormalCore
