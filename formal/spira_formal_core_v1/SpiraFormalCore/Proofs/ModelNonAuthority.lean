import SpiraFormalCore.Passthrough

set_option autoImplicit false

namespace SpiraFormalCore

theorem executedAction_model_non_authority
    (contract : MachineContract) (explanation : ModelExplanation) :
    executedAction contract explanation = contract.action := by
  rfl

theorem passthrough_preserves_machine_action
    (contract : MachineContract) (explanation : ModelExplanation) :
    (passthrough contract explanation).machineContract.action = contract.action := by
  rfl

end SpiraFormalCore
