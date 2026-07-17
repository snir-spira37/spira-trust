set_option autoImplicit false

namespace SpiraFormalCore
namespace Domain4

inductive ExecutionMeta where
  | PARSED_OK
  | INPUT_MALFORMED
  | TOOL_ERROR
  deriving Repr, DecidableEq

def ExecutionMeta.asString : ExecutionMeta -> String
  | ExecutionMeta.PARSED_OK => "PARSED_OK"
  | ExecutionMeta.INPUT_MALFORMED => "INPUT_MALFORMED"
  | ExecutionMeta.TOOL_ERROR => "TOOL_ERROR"

end Domain4
end SpiraFormalCore
