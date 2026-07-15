import SpiraFormalCore.Contract

set_option autoImplicit false

namespace SpiraFormalCore

structure UnifiedContract where
  wrapperId : UnifiedWrapperId
  machineContract : MachineContract
  deriving Repr, DecidableEq

def gateAWrap (contract : MachineContract) : UnifiedContract :=
  { wrapperId := defaultUnifiedWrapperId
    machineContract := contract }

def projectDomainContract (unified : UnifiedContract) : MachineContract :=
  unified.machineContract

end SpiraFormalCore
