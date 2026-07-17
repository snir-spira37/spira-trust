import SpiraFormalCore.Domain4.Proofs

set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain4

def allExecutionMeta : List ExecutionMeta :=
  [ ExecutionMeta.PARSED_OK
  , ExecutionMeta.INPUT_MALFORMED
  , ExecutionMeta.TOOL_ERROR
  ]

def jsonField (name value : String) : String :=
  "\"" ++ name ++ "\":\"" ++ value ++ "\""

def tupleJsonFields (tuple : OutcomeTuple) : String :=
  String.intercalate ","
    [ jsonField "schema" tuple.schema.asString
    , jsonField "evidence" tuple.evidence.asString
    , jsonField "hash" tuple.hash.asString
    , jsonField "path" tuple.path.asString
    , jsonField "symlink" tuple.symlink.asString
    , jsonField "duplicate" tuple.duplicate.asString
    , jsonField "directory" tuple.directory.asString
    , jsonField "context" tuple.context.asString
    , jsonField "temporal" tuple.temporal.asString
    ]

def contractJsonFields (contract : MachineContract) : String :=
  String.intercalate ","
    [ jsonField "status" contract.status.asString
    , jsonField "action" contract.action.asString
    , "\"stop\":true"
    ]

def dumpLine (kind : ArtifactKind) (execMeta : ExecutionMeta) (tuple : OutcomeTuple) : String :=
  let contract := NesiraCoreV2 kind execMeta tuple defaultPolicy
  "{" ++
    String.intercalate ","
      [ jsonField "artifact_kind" kind.asString
      , jsonField "execution_meta" execMeta.asString
      , "\"tuple\":{" ++ tupleJsonFields tuple ++ "}"
      , "\"contract\":{" ++ contractJsonFields contract ++ "}"
      ] ++
  "}"

def dumpLines : List String :=
  allArtifactKinds.flatMap fun kind =>
  allExecutionMeta.flatMap fun execMeta =>
  allOutcomeTuples.map fun tuple =>
    dumpLine kind execMeta tuple

def expectedDumpLineCount : Nat := 118098

def actualDumpLineCount : Nat := dumpLines.length

def main : IO Unit := do
  for line in dumpLines do
    IO.println line

end Domain4
end SpiraFormalCore
