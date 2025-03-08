from pydantic import BaseModel, Field
from typing import List, Optional

class ContractClause(BaseModel):
    clause_text: str = Field(..., description="The exact text of the clause.")
    mentions_data_processing: bool = Field(False, description="True if the clause involves personal data collection or usage.")
    mentions_data_transfer: bool = Field(False, description="True if the clause involves transferring personal data, especially to third parties or across borders.")
    requires_consent: bool = Field(False, description="True if the clause explicitly states that user consent is needed for data activities.")
    specifies_purpose: bool = Field(False, description="True if the clause specifies a clear purpose for data handling or transfer.")
    mentions_safeguards: bool = Field(False, description="True if the clause mentions security measures or other safeguards for data.")

class ContractExtraction(BaseModel):
    vendor_name: Optional[str] = Field(None, description="The vendor's name if identifiable.")
    effective_date: Optional[str] = Field(None, description="The effective date of the agreement, if available.")
    governing_law: Optional[str] = Field(None, description="The governing law of the contract, if stated.")
    clauses: List[ContractClause] = Field(..., description="List of extracted clauses and their relevant indicators.") 