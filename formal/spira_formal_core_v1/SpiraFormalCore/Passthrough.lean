import SpiraFormalCore.Contract
import SpiraFormalCore.GateA

set_option autoImplicit false

namespace SpiraFormalCore

structure ModelExplanation where
  text : String
  deriving Repr, DecidableEq

structure Telemetry where
  decisionAuthority : Bool
  deriving Repr, DecidableEq

structure PassthroughEnvelope where
  machineContract : MachineContract
  modelExplanation : ModelExplanation
  telemetry : Telemetry
  deriving Repr, DecidableEq

def passthrough (contract : MachineContract) (explanation : ModelExplanation) : PassthroughEnvelope :=
  { machineContract := contract
    modelExplanation := explanation
    telemetry := { decisionAuthority := false } }

def executedAction (contract : MachineContract) (_explanation : ModelExplanation) : Action :=
  contract.action

def envelopeExecutedAction (envelope : PassthroughEnvelope) : Action :=
  envelope.machineContract.action

end SpiraFormalCore
