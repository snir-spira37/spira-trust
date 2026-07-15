set_option autoImplicit false

namespace SpiraFormalCore

inductive Action where
  | PROCEED
  | STOP_BLOCKED
  | RERUN_REQUIRED
  | REPORT_NOT_EVALUATED
  deriving Repr, DecidableEq

def Action.nonProceeding : Action -> Bool
  | Action.PROCEED => false
  | Action.STOP_BLOCKED => true
  | Action.RERUN_REQUIRED => true
  | Action.REPORT_NOT_EVALUATED => true

def Action.stop (action : Action) : Bool :=
  action.nonProceeding

end SpiraFormalCore
