import SpiraFormalCore.Core

set_option autoImplicit false

namespace SpiraFormalCore

theorem required_unknown_decideAction_not_proceed
    {blockingItems : ExplicitList BlockingItem}
    {notEvaluated : ExplicitList NotEvaluatedItem}
    (hNoBlocking : blockingItems.isEmpty = true)
    (hUnknown : notEvaluated.isEmpty = false) :
    decideAction blockingItems notEvaluated ≠ Action.PROCEED := by
  simp [decideAction, hNoBlocking, hUnknown]

end SpiraFormalCore
