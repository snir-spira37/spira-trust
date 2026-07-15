import SpiraFormalCore.TestVectors

set_option autoImplicit false

namespace SpiraFormalCore

def renderChecks (checks : List ReferenceCheck) : String :=
  String.intercalate "\n" (checks.map ReferenceCheck.render)

def main : IO Unit := do
  IO.println (renderChecks referenceChecks)
  if allPassed referenceChecks then
    IO.println "SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_PASS"
  else
    IO.println "SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_FAIL"

end SpiraFormalCore

def main : IO Unit :=
  SpiraFormalCore.main
