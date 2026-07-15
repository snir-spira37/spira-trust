import SpiraFormalCore.Domain2.Decision

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain2

theorem failed_tests_prevent_proceed
    (evidence : PytestEvidence)
    (h : evidence.failedTestCount > 0)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = false)
    (hConflict : evidence.conflictPresent = false) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hVersion, hMalformed, hConflict, h]

theorem collection_or_execution_error_prevents_proceed
    (evidence : PytestEvidence)
    (hFailed : evidence.failedTestCount = 0)
    (hProblem : (!evidence.collectionSucceeded || evidence.executionError) = true)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = false)
    (hConflict : evidence.conflictPresent = false) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hVersion, hMalformed, hConflict, hFailed, hProblem]

theorem required_unknown_prevents_proceed
    (evidence : PytestEvidence)
    (hUnknown : evidence.requiredUnknown.isEmpty = false)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = false)
    (hConflict : evidence.conflictPresent = false)
    (hFailed : evidence.failedTestCount = 0)
    (hCollection : evidence.collectionSucceeded = true)
    (hExecution : evidence.executionError = false) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hVersion, hMalformed, hConflict, hFailed, hCollection,
    hExecution, hUnknown]

theorem clean_success_produces_proceed
    (evidence : PytestEvidence)
    (hUnknown : evidence.requiredUnknown.isEmpty = true)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = false)
    (hConflict : evidence.conflictPresent = false)
    (hFailed : evidence.failedTestCount = 0)
    (hCollection : evidence.collectionSucceeded = true)
    (hExecution : evidence.executionError = false) :
    formalAction evidence = Action.PROCEED := by
  simp [formalAction, hVersion, hMalformed, hConflict, hFailed, hCollection,
    hExecution, hUnknown]

theorem note_only_produces_proceed
    (evidence : PytestEvidence)
    (_hNote : evidence.noteOnly = true)
    (hUnknown : evidence.requiredUnknown.isEmpty = true)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = false)
    (hConflict : evidence.conflictPresent = false)
    (hFailed : evidence.failedTestCount = 0)
    (hCollection : evidence.collectionSucceeded = true)
    (hExecution : evidence.executionError = false) :
    formalAction evidence = Action.PROCEED := by
  simp [formalAction, hVersion, hMalformed, hConflict, hFailed, hCollection,
    hExecution, hUnknown]

theorem note_only_preserves_test_notes
    (evidence : PytestEvidence)
    (hNote : evidence.noteOnly = true)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = false)
    (hConflict : evidence.conflictPresent = false)
    (hFailed : evidence.failedTestCount = 0)
    (hCollection : evidence.collectionSucceeded = true)
    (hExecution : evidence.executionError = false) :
    (formalReasonCodes evidence).items = [reasonTestNotes] := by
  simp [formalReasonCodes, hVersion, hMalformed, hConflict, hFailed, hCollection,
    hExecution, hNote, ExplicitList.singleton]

theorem not_claimed_boundaries_preserved
    (evidence : PytestEvidence) :
    formalNotClaimed evidence = evidence.notClaimed := by
  simp [formalNotClaimed]

theorem malformed_fails_closed
    (evidence : PytestEvidence)
    (hVersion : evidence.versionIncompatible = false)
    (hMalformed : evidence.malformedEvidence = true) :
    formalAction evidence != Action.PROCEED := by
  cases hConflict : evidence.conflictPresent <;>
    simp [formalAction, hVersion, hMalformed, hConflict]

theorem version_incompatible_fails_closed
    (evidence : PytestEvidence)
    (hVersion : evidence.versionIncompatible = true) :
    formalAction evidence != Action.PROCEED := by
  simp [formalAction, hVersion]

end Domain2
end SpiraFormalCore
