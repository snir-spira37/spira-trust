import SpiraFormalCore.Core
import SpiraFormalCore.GateA
import SpiraFormalCore.Passthrough

set_option autoImplicit false

namespace SpiraFormalCore

def eqBool {α : Type} [DecidableEq α] (left right : α) : Bool :=
  if left = right then true else false

def evaluateTypedEvidence (evidence : TypedEvidence) (policy : PolicyContext) : CoreResult :=
  core evidence policy

def evaluateContract (evidence : TypedEvidence) (policy : PolicyContext) : MachineContract :=
  (evaluateTypedEvidence evidence policy).contract

def referenceAction (evidence : TypedEvidence) (policy : PolicyContext) : Action :=
  (evaluateTypedEvidence evidence policy).action

def referenceStop (evidence : TypedEvidence) (policy : PolicyContext) : Bool :=
  (evaluateTypedEvidence evidence policy).stop

structure ReferenceCheck where
  name : String
  passed : Bool
  deriving Repr

def ReferenceCheck.render (check : ReferenceCheck) : String :=
  check.name ++ ": " ++ (if check.passed then "PASS" else "FAIL")

def allPassed (checks : List ReferenceCheck) : Bool :=
  checks.all (fun check => check.passed)

end SpiraFormalCore
