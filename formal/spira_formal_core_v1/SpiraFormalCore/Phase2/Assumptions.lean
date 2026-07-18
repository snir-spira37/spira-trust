import SpiraFormalCore.Phase2.Assessment

set_option autoImplicit false

namespace SpiraFormalCore
namespace Phase2

inductive AssumptionId where
  | PT_CRYPTO_01
  | PT_CRYPTO_02
  | PT_CRYPTO_03
  | PT_KEYLEGIT_01
  | PT_KEYLEGIT_02
  | PT_IDENTITY_01
  | PT_IDENTITY_02
  | PT_AUTHORITY_01
  | PT_AUTHORITY_02
  | PT_AUTHORITY_03
  | PT_REVOKE_01
  | PT_REVOKE_02
  | PT_REVOKE_03
  | PT_CLOCK_01
  | PT_CLOCK_02
  | PT_ISOLATION_01
  | PT_ISOLATION_02
  | PT_ISOLATION_03
  | PT_META_01
  | PT_META_02
  | PT_META_03
  | PT_META_04
  deriving Repr, DecidableEq

structure AssumptionSet where
  ptCrypto01 : Bool
  ptCrypto02 : Bool
  ptCrypto03 : Bool
  ptKeylegit01 : Bool
  ptKeylegit02 : Bool
  ptIdentity01 : Bool
  ptIdentity02 : Bool
  ptAuthority01 : Bool
  ptAuthority02 : Bool
  ptAuthority03 : Bool
  ptRevoke01 : Bool
  ptRevoke02 : Bool
  ptRevoke03 : Bool
  ptClock01 : Bool
  ptClock02 : Bool
  ptIsolation01 : Bool
  ptIsolation02 : Bool
  ptIsolation03 : Bool
  ptMeta01 : Bool
  ptMeta02 : Bool
  ptMeta03 : Bool
  ptMeta04 : Bool
  deriving Repr, DecidableEq

def AssumptionId.asString : AssumptionId -> String
  | AssumptionId.PT_CRYPTO_01 => "PT-CRYPTO-01"
  | AssumptionId.PT_CRYPTO_02 => "PT-CRYPTO-02"
  | AssumptionId.PT_CRYPTO_03 => "PT-CRYPTO-03"
  | AssumptionId.PT_KEYLEGIT_01 => "PT-KEYLEGIT-01"
  | AssumptionId.PT_KEYLEGIT_02 => "PT-KEYLEGIT-02"
  | AssumptionId.PT_IDENTITY_01 => "PT-IDENTITY-01"
  | AssumptionId.PT_IDENTITY_02 => "PT-IDENTITY-02"
  | AssumptionId.PT_AUTHORITY_01 => "PT-AUTHORITY-01"
  | AssumptionId.PT_AUTHORITY_02 => "PT-AUTHORITY-02"
  | AssumptionId.PT_AUTHORITY_03 => "PT-AUTHORITY-03"
  | AssumptionId.PT_REVOKE_01 => "PT-REVOKE-01"
  | AssumptionId.PT_REVOKE_02 => "PT-REVOKE-02"
  | AssumptionId.PT_REVOKE_03 => "PT-REVOKE-03"
  | AssumptionId.PT_CLOCK_01 => "PT-CLOCK-01"
  | AssumptionId.PT_CLOCK_02 => "PT-CLOCK-02"
  | AssumptionId.PT_ISOLATION_01 => "PT-ISOLATION-01"
  | AssumptionId.PT_ISOLATION_02 => "PT-ISOLATION-02"
  | AssumptionId.PT_ISOLATION_03 => "PT-ISOLATION-03"
  | AssumptionId.PT_META_01 => "PT-META-01"
  | AssumptionId.PT_META_02 => "PT-META-02"
  | AssumptionId.PT_META_03 => "PT-META-03"
  | AssumptionId.PT_META_04 => "PT-META-04"

def allAssumptionIds : List AssumptionId :=
  [ AssumptionId.PT_CRYPTO_01
  , AssumptionId.PT_CRYPTO_02
  , AssumptionId.PT_CRYPTO_03
  , AssumptionId.PT_KEYLEGIT_01
  , AssumptionId.PT_KEYLEGIT_02
  , AssumptionId.PT_IDENTITY_01
  , AssumptionId.PT_IDENTITY_02
  , AssumptionId.PT_AUTHORITY_01
  , AssumptionId.PT_AUTHORITY_02
  , AssumptionId.PT_AUTHORITY_03
  , AssumptionId.PT_REVOKE_01
  , AssumptionId.PT_REVOKE_02
  , AssumptionId.PT_REVOKE_03
  , AssumptionId.PT_CLOCK_01
  , AssumptionId.PT_CLOCK_02
  , AssumptionId.PT_ISOLATION_01
  , AssumptionId.PT_ISOLATION_02
  , AssumptionId.PT_ISOLATION_03
  , AssumptionId.PT_META_01
  , AssumptionId.PT_META_02
  , AssumptionId.PT_META_03
  , AssumptionId.PT_META_04
  ]

def emptyAssumptions : AssumptionSet :=
  { ptCrypto01 := false
    ptCrypto02 := false
    ptCrypto03 := false
    ptKeylegit01 := false
    ptKeylegit02 := false
    ptIdentity01 := false
    ptIdentity02 := false
    ptAuthority01 := false
    ptAuthority02 := false
    ptAuthority03 := false
    ptRevoke01 := false
    ptRevoke02 := false
    ptRevoke03 := false
    ptClock01 := false
    ptClock02 := false
    ptIsolation01 := false
    ptIsolation02 := false
    ptIsolation03 := false
    ptMeta01 := false
    ptMeta02 := false
    ptMeta03 := false
    ptMeta04 := false }

def floorAssumptions : AssumptionSet :=
  { emptyAssumptions with
    ptCrypto01 := true
    ptClock01 := true
    ptMeta01 := true
    ptMeta02 := true
    ptMeta04 := true }

def signatureAssumptions : AssumptionSet :=
  { emptyAssumptions with
    ptCrypto02 := true
    ptCrypto03 := true
    ptKeylegit01 := true
    ptKeylegit02 := true }

def identityAssumptions : AssumptionSet :=
  { emptyAssumptions with
    ptIdentity01 := true
    ptIdentity02 := true }

def authorityAssumptions : AssumptionSet :=
  { emptyAssumptions with
    ptAuthority01 := true
    ptAuthority02 := true
    ptAuthority03 := true }

def isolationAssumptions : AssumptionSet :=
  { emptyAssumptions with
    ptCrypto02 := true
    ptCrypto03 := true
    ptRevoke01 := true
    ptClock02 := true
    ptIsolation01 := true
    ptIsolation02 := true
    ptIsolation03 := true }

def AssumptionSet.union (left right : AssumptionSet) : AssumptionSet :=
  { ptCrypto01 := left.ptCrypto01 || right.ptCrypto01
    ptCrypto02 := left.ptCrypto02 || right.ptCrypto02
    ptCrypto03 := left.ptCrypto03 || right.ptCrypto03
    ptKeylegit01 := left.ptKeylegit01 || right.ptKeylegit01
    ptKeylegit02 := left.ptKeylegit02 || right.ptKeylegit02
    ptIdentity01 := left.ptIdentity01 || right.ptIdentity01
    ptIdentity02 := left.ptIdentity02 || right.ptIdentity02
    ptAuthority01 := left.ptAuthority01 || right.ptAuthority01
    ptAuthority02 := left.ptAuthority02 || right.ptAuthority02
    ptAuthority03 := left.ptAuthority03 || right.ptAuthority03
    ptRevoke01 := left.ptRevoke01 || right.ptRevoke01
    ptRevoke02 := left.ptRevoke02 || right.ptRevoke02
    ptRevoke03 := left.ptRevoke03 || right.ptRevoke03
    ptClock01 := left.ptClock01 || right.ptClock01
    ptClock02 := left.ptClock02 || right.ptClock02
    ptIsolation01 := left.ptIsolation01 || right.ptIsolation01
    ptIsolation02 := left.ptIsolation02 || right.ptIsolation02
    ptIsolation03 := left.ptIsolation03 || right.ptIsolation03
    ptMeta01 := left.ptMeta01 || right.ptMeta01
    ptMeta02 := left.ptMeta02 || right.ptMeta02
    ptMeta03 := left.ptMeta03 || right.ptMeta03
    ptMeta04 := left.ptMeta04 || right.ptMeta04 }

def AssumptionSet.has (s : AssumptionSet) : AssumptionId -> Bool
  | AssumptionId.PT_CRYPTO_01 => s.ptCrypto01
  | AssumptionId.PT_CRYPTO_02 => s.ptCrypto02
  | AssumptionId.PT_CRYPTO_03 => s.ptCrypto03
  | AssumptionId.PT_KEYLEGIT_01 => s.ptKeylegit01
  | AssumptionId.PT_KEYLEGIT_02 => s.ptKeylegit02
  | AssumptionId.PT_IDENTITY_01 => s.ptIdentity01
  | AssumptionId.PT_IDENTITY_02 => s.ptIdentity02
  | AssumptionId.PT_AUTHORITY_01 => s.ptAuthority01
  | AssumptionId.PT_AUTHORITY_02 => s.ptAuthority02
  | AssumptionId.PT_AUTHORITY_03 => s.ptAuthority03
  | AssumptionId.PT_REVOKE_01 => s.ptRevoke01
  | AssumptionId.PT_REVOKE_02 => s.ptRevoke02
  | AssumptionId.PT_REVOKE_03 => s.ptRevoke03
  | AssumptionId.PT_CLOCK_01 => s.ptClock01
  | AssumptionId.PT_CLOCK_02 => s.ptClock02
  | AssumptionId.PT_ISOLATION_01 => s.ptIsolation01
  | AssumptionId.PT_ISOLATION_02 => s.ptIsolation02
  | AssumptionId.PT_ISOLATION_03 => s.ptIsolation03
  | AssumptionId.PT_META_01 => s.ptMeta01
  | AssumptionId.PT_META_02 => s.ptMeta02
  | AssumptionId.PT_META_03 => s.ptMeta03
  | AssumptionId.PT_META_04 => s.ptMeta04

def AssumptionSet.ids (s : AssumptionSet) : List AssumptionId :=
  allAssumptionIds.filter fun id => s.has id

def AssumptionSet.idStrings (s : AssumptionSet) : List String :=
  (s.ids).map AssumptionId.asString

def floorCarried (s : AssumptionSet) : Bool :=
  s.has AssumptionId.PT_CRYPTO_01 &&
  s.has AssumptionId.PT_CLOCK_01 &&
  s.has AssumptionId.PT_META_01 &&
  s.has AssumptionId.PT_META_02 &&
  s.has AssumptionId.PT_META_04

def fullUnionCarried (s : AssumptionSet) : Bool :=
  floorCarried s &&
  s.has AssumptionId.PT_CRYPTO_02 &&
  s.has AssumptionId.PT_CRYPTO_03 &&
  s.has AssumptionId.PT_KEYLEGIT_01 &&
  s.has AssumptionId.PT_KEYLEGIT_02 &&
  s.has AssumptionId.PT_IDENTITY_01 &&
  s.has AssumptionId.PT_IDENTITY_02 &&
  s.has AssumptionId.PT_AUTHORITY_01 &&
  s.has AssumptionId.PT_AUTHORITY_02 &&
  s.has AssumptionId.PT_AUTHORITY_03 &&
  s.has AssumptionId.PT_ISOLATION_01 &&
  s.has AssumptionId.PT_ISOLATION_02 &&
  s.has AssumptionId.PT_ISOLATION_03

end Phase2
end SpiraFormalCore
