import SpiraFormalCore.Core

set_option autoImplicit false

namespace SpiraFormalCore

theorem failClosedAction_not_proceed (error : CoreError) :
    failClosedAction error ≠ Action.PROCEED := by
  cases error <;> simp [failClosedAction]

theorem assembleFailClosedContract_stop_true
    (evidence : TypedEvidence) (policy : PolicyContext) (error : CoreError) :
    (assembleFailClosedContract evidence policy error).stop = true := by
  cases error <;>
    simp [assembleFailClosedContract, assembleContract, failClosedAction,
      Action.stop, Action.nonProceeding]

end SpiraFormalCore
