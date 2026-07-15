import SpiraFormalCore.Core

set_option autoImplicit false

namespace SpiraFormalCore

theorem core_extensional_determinism
    {e1 e2 : TypedEvidence} {p1 p2 : PolicyContext}
    (he : e1 = e2) (hp : p1 = p2) :
    core e1 p1 = core e2 p2 := by
  cases he
  cases hp
  rfl

end SpiraFormalCore
