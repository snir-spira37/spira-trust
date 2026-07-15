import SpiraFormalCore.GateA

set_option autoImplicit false

namespace SpiraFormalCore

theorem gateA_project_preserves_contract (contract : MachineContract) :
    projectDomainContract (gateAWrap contract) = contract := by
  rfl

end SpiraFormalCore
