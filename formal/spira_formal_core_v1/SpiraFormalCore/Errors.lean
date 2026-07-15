import SpiraFormalCore.Action
import SpiraFormalCore.Contract

set_option autoImplicit false

namespace SpiraFormalCore

inductive CoreError where
  | invalidTypedEvidence
  | incompleteTypedEvidence
  | conflictingTypedEvidence
  | incompatibleVersion
  | internalValidationFailure
  deriving Repr, DecidableEq

inductive CoreResult where
  | ok : MachineContract -> CoreResult
  | error : CoreError -> MachineContract -> CoreResult
  deriving Repr, DecidableEq

def CoreResult.contract : CoreResult -> MachineContract
  | CoreResult.ok contract => contract
  | CoreResult.error _ contract => contract

def CoreResult.action (result : CoreResult) : Action :=
  result.contract.action

def CoreResult.stop (result : CoreResult) : Bool :=
  result.contract.stop

end SpiraFormalCore
