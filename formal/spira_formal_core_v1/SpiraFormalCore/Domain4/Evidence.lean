import SpiraFormalCore.Domain4.Meta

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain4

inductive ArtifactKind where
  | SEVERANCE_AUTHORIZATION
  | LEGACY_ISOLATION_RESULT
  deriving Repr, DecidableEq

inductive SchemaOutcome where
  | SCHEMA_OK
  | SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION
  | SCHEMA_STRUCTURAL_VIOLATION
  deriving Repr, DecidableEq

inductive EvidencePresenceOutcome where
  | EVIDENCE_OK
  | EVIDENCE_MISSING
  | EVIDENCE_NOT_APPLICABLE
  deriving Repr, DecidableEq

inductive HashOutcome where
  | HASH_OK
  | HASH_MISMATCH
  | HASH_NOT_APPLICABLE
  deriving Repr, DecidableEq

inductive PathOutcome where
  | PATH_OK
  | PATH_UNSAFE
  | PATH_NOT_APPLICABLE
  deriving Repr, DecidableEq

inductive SymlinkOutcome where
  | SYMLINK_OK
  | SYMLINK_ESCAPE
  | SYMLINK_NOT_APPLICABLE
  deriving Repr, DecidableEq

inductive DuplicateOutcome where
  | DUP_OK
  | DUP_PRESENT
  | DUP_NOT_APPLICABLE
  deriving Repr, DecidableEq

inductive DirectoryEvidenceOutcome where
  | DIR_OK
  | DIR_AS_FILE
  | DIR_NOT_APPLICABLE
  deriving Repr, DecidableEq

inductive ContextOutcome where
  | CONTEXT_OK
  | CONTEXT_EXPECTED_MISSING
  | CONTEXT_MISMATCH
  deriving Repr, DecidableEq

inductive TemporalOutcome where
  | TEMPORAL_OK
  | TEMPORAL_VIOLATION
  | TEMPORAL_NOT_APPLICABLE
  deriving Repr, DecidableEq

structure OutcomeTuple where
  schema : SchemaOutcome
  evidence : EvidencePresenceOutcome
  hash : HashOutcome
  path : PathOutcome
  symlink : SymlinkOutcome
  duplicate : DuplicateOutcome
  directory : DirectoryEvidenceOutcome
  context : ContextOutcome
  temporal : TemporalOutcome
  deriving Repr, DecidableEq

def ArtifactKind.asString : ArtifactKind -> String
  | ArtifactKind.SEVERANCE_AUTHORIZATION => "SEVERANCE_AUTHORIZATION"
  | ArtifactKind.LEGACY_ISOLATION_RESULT => "LEGACY_ISOLATION_RESULT"

def SchemaOutcome.asString : SchemaOutcome -> String
  | SchemaOutcome.SCHEMA_OK => "SCHEMA_OK"
  | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION => "SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION"
  | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION => "SCHEMA_STRUCTURAL_VIOLATION"

def EvidencePresenceOutcome.asString : EvidencePresenceOutcome -> String
  | EvidencePresenceOutcome.EVIDENCE_OK => "EVIDENCE_OK"
  | EvidencePresenceOutcome.EVIDENCE_MISSING => "EVIDENCE_MISSING"
  | EvidencePresenceOutcome.EVIDENCE_NOT_APPLICABLE => "EVIDENCE_NOT_APPLICABLE"

def HashOutcome.asString : HashOutcome -> String
  | HashOutcome.HASH_OK => "HASH_OK"
  | HashOutcome.HASH_MISMATCH => "HASH_MISMATCH"
  | HashOutcome.HASH_NOT_APPLICABLE => "HASH_NOT_APPLICABLE"

def PathOutcome.asString : PathOutcome -> String
  | PathOutcome.PATH_OK => "PATH_OK"
  | PathOutcome.PATH_UNSAFE => "PATH_UNSAFE"
  | PathOutcome.PATH_NOT_APPLICABLE => "PATH_NOT_APPLICABLE"

def SymlinkOutcome.asString : SymlinkOutcome -> String
  | SymlinkOutcome.SYMLINK_OK => "SYMLINK_OK"
  | SymlinkOutcome.SYMLINK_ESCAPE => "SYMLINK_ESCAPE"
  | SymlinkOutcome.SYMLINK_NOT_APPLICABLE => "SYMLINK_NOT_APPLICABLE"

def DuplicateOutcome.asString : DuplicateOutcome -> String
  | DuplicateOutcome.DUP_OK => "DUP_OK"
  | DuplicateOutcome.DUP_PRESENT => "DUP_PRESENT"
  | DuplicateOutcome.DUP_NOT_APPLICABLE => "DUP_NOT_APPLICABLE"

def DirectoryEvidenceOutcome.asString : DirectoryEvidenceOutcome -> String
  | DirectoryEvidenceOutcome.DIR_OK => "DIR_OK"
  | DirectoryEvidenceOutcome.DIR_AS_FILE => "DIR_AS_FILE"
  | DirectoryEvidenceOutcome.DIR_NOT_APPLICABLE => "DIR_NOT_APPLICABLE"

def ContextOutcome.asString : ContextOutcome -> String
  | ContextOutcome.CONTEXT_OK => "CONTEXT_OK"
  | ContextOutcome.CONTEXT_EXPECTED_MISSING => "CONTEXT_EXPECTED_MISSING"
  | ContextOutcome.CONTEXT_MISMATCH => "CONTEXT_MISMATCH"

def TemporalOutcome.asString : TemporalOutcome -> String
  | TemporalOutcome.TEMPORAL_OK => "TEMPORAL_OK"
  | TemporalOutcome.TEMPORAL_VIOLATION => "TEMPORAL_VIOLATION"
  | TemporalOutcome.TEMPORAL_NOT_APPLICABLE => "TEMPORAL_NOT_APPLICABLE"

def allArtifactKinds : List ArtifactKind :=
  [ ArtifactKind.SEVERANCE_AUTHORIZATION
  , ArtifactKind.LEGACY_ISOLATION_RESULT
  ]

def allSchemaOutcomes : List SchemaOutcome :=
  [ SchemaOutcome.SCHEMA_OK
  , SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION
  , SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION
  ]

def allEvidencePresenceOutcomes : List EvidencePresenceOutcome :=
  [ EvidencePresenceOutcome.EVIDENCE_OK
  , EvidencePresenceOutcome.EVIDENCE_MISSING
  , EvidencePresenceOutcome.EVIDENCE_NOT_APPLICABLE
  ]

def allHashOutcomes : List HashOutcome :=
  [ HashOutcome.HASH_OK
  , HashOutcome.HASH_MISMATCH
  , HashOutcome.HASH_NOT_APPLICABLE
  ]

def allPathOutcomes : List PathOutcome :=
  [ PathOutcome.PATH_OK
  , PathOutcome.PATH_UNSAFE
  , PathOutcome.PATH_NOT_APPLICABLE
  ]

def allSymlinkOutcomes : List SymlinkOutcome :=
  [ SymlinkOutcome.SYMLINK_OK
  , SymlinkOutcome.SYMLINK_ESCAPE
  , SymlinkOutcome.SYMLINK_NOT_APPLICABLE
  ]

def allDuplicateOutcomes : List DuplicateOutcome :=
  [ DuplicateOutcome.DUP_OK
  , DuplicateOutcome.DUP_PRESENT
  , DuplicateOutcome.DUP_NOT_APPLICABLE
  ]

def allDirectoryEvidenceOutcomes : List DirectoryEvidenceOutcome :=
  [ DirectoryEvidenceOutcome.DIR_OK
  , DirectoryEvidenceOutcome.DIR_AS_FILE
  , DirectoryEvidenceOutcome.DIR_NOT_APPLICABLE
  ]

def allContextOutcomes : List ContextOutcome :=
  [ ContextOutcome.CONTEXT_OK
  , ContextOutcome.CONTEXT_EXPECTED_MISSING
  , ContextOutcome.CONTEXT_MISMATCH
  ]

def allTemporalOutcomes : List TemporalOutcome :=
  [ TemporalOutcome.TEMPORAL_OK
  , TemporalOutcome.TEMPORAL_VIOLATION
  , TemporalOutcome.TEMPORAL_NOT_APPLICABLE
  ]

def allOutcomeTuples : List OutcomeTuple :=
  allSchemaOutcomes.flatMap fun schema =>
  allEvidencePresenceOutcomes.flatMap fun evidence =>
  allHashOutcomes.flatMap fun hash =>
  allPathOutcomes.flatMap fun path =>
  allSymlinkOutcomes.flatMap fun symlink =>
  allDuplicateOutcomes.flatMap fun duplicate =>
  allDirectoryEvidenceOutcomes.flatMap fun directory =>
  allContextOutcomes.flatMap fun context =>
  allTemporalOutcomes.map fun temporal =>
    { schema := schema
      evidence := evidence
      hash := hash
      path := path
      symlink := symlink
      duplicate := duplicate
      directory := directory
      context := context
      temporal := temporal }

end Domain4
end SpiraFormalCore
