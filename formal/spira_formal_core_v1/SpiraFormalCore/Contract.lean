import SpiraFormalCore.Basic
import SpiraFormalCore.Action
import SpiraFormalCore.ExplicitList

set_option autoImplicit false

namespace SpiraFormalCore

structure MachineContract where
  domainId : DomainId
  subjectId : SubjectId
  policyId : PolicyId
  schemaVersion : SchemaVersion
  producerId : ProducerId
  contractId : ContractId
  action : Action
  stop : Bool
  reasonCodes : ExplicitList ReasonCode
  blockingItems : ExplicitList BlockingItem
  notEvaluated : ExplicitList NotEvaluatedItem
  notClaimed : ExplicitList NotClaimedItem
  evidenceRefs : ExplicitList EvidenceRef
  proofRefs : ExplicitList ProofRef
  deriving Repr, DecidableEq

def MachineContract.stopConsistent (contract : MachineContract) : Bool :=
  contract.stop == contract.action.stop

end SpiraFormalCore
