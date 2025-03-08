from enum import Enum
from typing import Dict, Any

class ResultType(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    TEXT = "text"

class MetadataMode(str, Enum):
    ALL = "all"
    NONE = "none"
    MINIMAL = "minimal"

LLAMA_CLOUD_CONFIG: Dict[str, Any] = {
    "name": "gdpr",
    "project_name": "llamacloud_demo",
    "organization_id": "cdcb3478-1348-492e-8aa0-25f47d1a3902",
}

DEFAULT_OUTPUT_DIR = "data_out"
DEFAULT_SIMILARITY_TOP_K = 20
DEFAULT_LLM_MODEL = "gpt-4o" 