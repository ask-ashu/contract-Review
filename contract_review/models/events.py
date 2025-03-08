from llama_index.core.workflow import Event
from typing import List
from .contract import ContractExtraction, ContractClause
from .compliance import ClauseComplianceCheck

class ContractExtractionEvent(Event):
    contract_extraction: ContractExtraction

class MatchGuidelineEvent(Event):
    clause: ContractClause
    vendor_name: str

class MatchGuidelineResultEvent(Event):
    result: ClauseComplianceCheck

class GenerateReportEvent(Event):
    match_results: List[ClauseComplianceCheck]

class LogEvent(Event):
    msg: str
    delta: bool = False 