import SpiraFormalCore.Basic
import SpiraFormalCore.ExplicitList

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain2

structure PytestEvidence where
  subjectId : SubjectId
  schemaVersion : SchemaVersion
  producerId : ProducerId
  testsPassed : Bool
  failedTestCount : Nat
  collectionSucceeded : Bool
  executionError : Bool
  conflictPresent : Bool
  malformedEvidence : Bool
  versionIncompatible : Bool
  noteOnly : Bool
  requiredUnknown : ExplicitList NotEvaluatedItem
  notClaimed : ExplicitList NotClaimedItem
  evidenceRefs : ExplicitList EvidenceRef
  proofRefs : ExplicitList ProofRef
  deriving Repr, DecidableEq

def domainId : DomainId := "DOMAIN_2_PYTEST_RESULT"

def producerId : ProducerId := "SPIRA_DOMAIN2_PYTEST_PRODUCER"

def reasonTestsPassed : ReasonCode := "TESTS_PASSED"

def reasonTestFailure : ReasonCode := "TEST_FAILURE"

def reasonTestNotes : ReasonCode := "TEST_NOTES"

def reasonConflict : ReasonCode := "TEST_EVIDENCE_CONFLICT"

def reasonMalformed : ReasonCode := "MALFORMED_TEST_EVIDENCE"

def reasonVersionIncompatible : ReasonCode := "INCOMPATIBLE_VERSION"

def blockingFailedTest : BlockingItem := "failed_test"

def blockingCollectionOrExecution : BlockingItem := "collection_or_execution_error"

end Domain2
end SpiraFormalCore
