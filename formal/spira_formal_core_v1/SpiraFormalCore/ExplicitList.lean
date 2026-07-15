set_option autoImplicit false

namespace SpiraFormalCore

structure ExplicitList (α : Type) where
  items : List α
  deriving Repr, DecidableEq

namespace ExplicitList

def empty {α : Type} : ExplicitList α :=
  { items := [] }

def singleton {α : Type} (item : α) : ExplicitList α :=
  { items := [item] }

def append {α : Type} (left right : ExplicitList α) : ExplicitList α :=
  { items := left.items ++ right.items }

def isEmpty {α : Type} (xs : ExplicitList α) : Bool :=
  match xs.items with
  | [] => true
  | _ => false

def map {α β : Type} (f : α -> β) (xs : ExplicitList α) : ExplicitList β :=
  { items := xs.items.map f }

end ExplicitList

end SpiraFormalCore
