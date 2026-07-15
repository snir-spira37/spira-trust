import SpiraFormalCore.Core

set_option autoImplicit false

namespace SpiraFormalCore

theorem blocking_decideAction_not_proceed
    {blockingItems : ExplicitList BlockingItem}
    {notEvaluated : ExplicitList NotEvaluatedItem}
    (hBlocking : blockingItems.isEmpty = false) :
    decideAction blockingItems notEvaluated ≠ Action.PROCEED := by
  simp [decideAction, hBlocking]

end SpiraFormalCore
