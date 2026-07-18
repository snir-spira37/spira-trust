import SpiraFormalCore.Phase2.Composition

set_option autoImplicit false

namespace SpiraFormalCore
namespace Phase2

theorem composition_strict_and (sv : SubVerdicts) :
    (compose sv).verdict =
      if allSufficient sv then
        Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
      else if anyInsufficient sv then
        Phase2Assessment.TRUST_INSUFFICIENT
      else
        Phase2Assessment.TRUST_NOT_EVALUATED := by
  rfl

theorem insufficient_dominates_not_evaluated
    (sv : SubVerdicts)
    (h : anyInsufficient sv = true) :
    (compose sv).verdict = Phase2Assessment.TRUST_INSUFFICIENT := by
  cases sv with
  | mk signature identity authority isolation =>
      cases signature <;> cases identity <;> cases authority <;> cases isolation <;>
        simp_all [compose, verdictOf, allSufficient, anyInsufficient, isSufficient, isInsufficient]

theorem otherwise_not_evaluated
    (sv : SubVerdicts)
    (hNoInsufficient : anyInsufficient sv = false)
    (hNotAllSufficient : allSufficient sv = false) :
    (compose sv).verdict = Phase2Assessment.TRUST_NOT_EVALUATED := by
  cases sv with
  | mk signature identity authority isolation =>
      cases signature <;> cases identity <;> cases authority <;> cases isolation <;>
        simp_all [compose, verdictOf, allSufficient, anyInsufficient, isSufficient, isInsufficient]

theorem composition_total (sv : SubVerdicts) :
    (compose sv).verdict = verdictOf sv := by
  rfl

theorem composition_deterministic (sv : SubVerdicts) :
    compose sv = compose sv := by
  rfl

theorem floor_always_carried (sv : SubVerdicts) :
    floorCarried (compose sv).carriedAssumptions = true := by
  cases sv with
  | mk signature identity authority isolation =>
      cases signature <;> cases identity <;> cases authority <;> cases isolation <;>
        simp [compose, carriedAssumptionsOf, domainAssumptions, isEvaluated,
          AssumptionSet.union, floorAssumptions, emptyAssumptions, floorCarried, AssumptionSet.has]

theorem sufficient_carries_full_union
    (sv : SubVerdicts)
    (h : (compose sv).verdict = Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS) :
    fullUnionCarried (compose sv).carriedAssumptions = true := by
  cases sv with
  | mk signature identity authority isolation =>
      cases signature <;> cases identity <;> cases authority <;> cases isolation <;>
        simp_all [compose, verdictOf, allSufficient, anyInsufficient, isSufficient, isInsufficient,
          carriedAssumptionsOf, domainAssumptions, isEvaluated, AssumptionSet.union,
          floorAssumptions, signatureAssumptions, identityAssumptions, authorityAssumptions,
          isolationAssumptions, emptyAssumptions, fullUnionCarried, floorCarried, AssumptionSet.has]

theorem isolation_caveat_inherited
    (signature identity authority isolation : Phase2Assessment)
    (h : isEvaluated isolation = true) :
    (compose
      { signature := signature
        identity := identity
        authority := authority
        isolation := isolation }).carriedAssumptions.has AssumptionId.PT_ISOLATION_01 =
        true := by
  cases signature <;> cases identity <;> cases authority <;> cases isolation <;>
    simp_all [compose, carriedAssumptionsOf, domainAssumptions, isEvaluated, AssumptionSet.union,
      floorAssumptions, signatureAssumptions, identityAssumptions, authorityAssumptions,
      isolationAssumptions, emptyAssumptions, AssumptionSet.has]

theorem sufficient_is_not_assumption_free
    (sv : SubVerdicts)
    (_h : (compose sv).verdict = Phase2Assessment.TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS) :
    (compose sv).carriedAssumptions.has AssumptionId.PT_CRYPTO_01 = true := by
  cases sv with
  | mk signature identity authority isolation =>
      cases signature <;> cases identity <;> cases authority <;> cases isolation <;>
        simp [compose, carriedAssumptionsOf, domainAssumptions, isEvaluated, AssumptionSet.union,
          floorAssumptions, signatureAssumptions, identityAssumptions, authorityAssumptions,
          isolationAssumptions, emptyAssumptions, AssumptionSet.has]

theorem execution_marker_constant (sv : SubVerdicts) :
    (compose sv).executionMarker = executionMarker := by
  rfl

end Phase2
end SpiraFormalCore
