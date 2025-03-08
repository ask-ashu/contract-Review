from pathlib import Path
import json
import os
from typing import Optional, List, Union
import asyncio

from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Context, Workflow, step, StopEvent, StartEvent
from llama_index.core.llms import LLM
from llama_index.core import SimpleDirectoryReader
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.schema import Document, MetadataMode
from llama_parse import LlamaParse

from ..models.events import (
    ContractExtractionEvent,
    MatchGuidelineEvent,
    MatchGuidelineResultEvent,
    GenerateReportEvent,
    LogEvent,
)
from ..models.compliance import ComplianceReport, ClauseComplianceCheck
from ..models.contract import ContractExtraction
from ..prompts.templates import (
    CONTRACT_EXTRACT_PROMPT,
    CONTRACT_MATCH_PROMPT,
    COMPLIANCE_REPORT_SYSTEM_PROMPT,
    COMPLIANCE_REPORT_USER_PROMPT,
)
from ..utils.logger import logger
from ..config.settings import DEFAULT_OUTPUT_DIR, DEFAULT_SIMILARITY_TOP_K

class ContractReviewWorkflow(Workflow):
    """Contract review workflow for GDPR compliance checking."""

    def __init__(
        self,
        parser: Optional[Union[LlamaParse, SimpleDirectoryReader]] = None,
        guideline_retriever: Optional[BaseRetriever] = None,
        llm: Optional[LLM] = None,
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        **kwargs,
    ) -> None:
        """Initialize the workflow.
        
        Args:
            parser: Document parser (LlamaParse or SimpleDirectoryReader)
            guideline_retriever: Retriever for GDPR guidelines
            llm: Language model instance (defaults to OpenAI GPT-4)
            similarity_top_k: Number of similar guidelines to retrieve
            output_dir: Directory for workflow outputs
            **kwargs: Additional workflow parameters
        """
        super().__init__(**kwargs)

        self.parser = parser
        if guideline_retriever is None:
            raise ValueError("guideline_retriever must be provided")
        self.guideline_retriever = guideline_retriever
        self.llm = llm or OpenAI(model="gpt-4")
        self.similarity_top_k = similarity_top_k
        self.vendor_name = None  # Will be set during contract parsing

        # Create output directory if it doesn't exist
        out_path = Path(output_dir) / "workflow_output"
        out_path.mkdir(parents=True, exist_ok=True)
        os.chmod(str(out_path), 0o0777)
        self.output_dir = out_path

    @step
    async def parse_contract(
        self, ctx: Context, ev: StartEvent
    ) -> ContractExtractionEvent:
        """Parse and extract information from the contract."""
        contract_extraction_path = Path(f"{self.output_dir}/contract_extraction.json")
        
        if contract_extraction_path.exists():
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Loading contract from cache"))
            contract_extraction_dict = json.load(open(contract_extraction_path))
            contract_extraction = ContractExtraction.model_validate(contract_extraction_dict)
        else:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Reading contract"))

            # Create reader with the contract directory
            reader = SimpleDirectoryReader(input_dir=str(Path(ev.contract_path).parent))
            docs = reader.load_data()
            
            doc_contents = "\n".join([
                d.get_content(metadata_mode=MetadataMode.ALL) 
                for d in docs
            ])
            
            prompt = ChatPromptTemplate.from_messages([
                ("user", CONTRACT_EXTRACT_PROMPT)
            ])
            contract_extraction = await self.llm.astructured_predict(
                ContractExtraction,
                prompt,
                contract_data=doc_contents
            )
            
            if not isinstance(contract_extraction, ContractExtraction):
                raise ValueError(f"Invalid extraction from contract: {contract_extraction}")
                
            with open(contract_extraction_path, "w") as fp:
                fp.write(contract_extraction.model_dump_json())
                
        if self._verbose:
            ctx.write_event_to_stream(
                LogEvent(msg=f">> Contract data: {contract_extraction.model_dump()}")
            )

        # Set vendor name from contract extraction
        self.vendor_name = contract_extraction.vendor_name

        return ContractExtractionEvent(contract_extraction=contract_extraction)

    @step
    async def match_guidelines(
        self, ctx: Context, ev: ContractExtractionEvent
    ) -> GenerateReportEvent:
        """Match contract clauses against GDPR guidelines."""
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Matching clauses against guidelines"))

        match_results = []
        for clause in ev.contract_extraction.clauses:
            try:
                # Get relevant guidelines for this clause
                relevant_docs = await self.guideline_retriever.aretrieve(
                    clause.clause_text
                )
                
                # Get the most relevant guideline
                if relevant_docs:
                    matched_guideline = relevant_docs[0]
                    
                    # Evaluate compliance with retry logic
                    max_retries = 3
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            prompt = ChatPromptTemplate.from_messages([
                                ("user", CONTRACT_MATCH_PROMPT)
                            ])
                            
                            result = await self.llm.astructured_predict(
                                ClauseComplianceCheck,
                                prompt,
                                clause_text=clause.clause_text,
                                guideline_text=matched_guideline.text
                            )
                            
                            if not isinstance(result, ClauseComplianceCheck):
                                raise ValueError(f"Invalid compliance check result: {result}")
                                
                            match_results.append(result)
                            
                            if self._verbose:
                                ctx.write_event_to_stream(
                                    LogEvent(msg=f">> Clause matched: {result.model_dump()}")
                                )
                            break  # Success, exit retry loop
                            
                        except Exception as e:
                            retry_count += 1
                            if retry_count == max_retries:
                                raise  # Re-raise the last exception if all retries failed
                            if self._verbose:
                                ctx.write_event_to_stream(
                                    LogEvent(msg=f">> Retry {retry_count}/{max_retries} for clause: {str(e)}")
                                )
                            await asyncio.sleep(1)  # Wait before retrying
                            
            except Exception as e:
                if self._verbose:
                    ctx.write_event_to_stream(
                        LogEvent(msg=f">> Error processing clause: {str(e)}")
                    )
                # Create a non-compliant result for failed clauses
                match_results.append(ClauseComplianceCheck(
                    clause_text=clause.clause_text,
                    matched_guideline=None,
                    compliant=False,
                    notes=f"Error processing clause: {str(e)}"
                ))

        return GenerateReportEvent(match_results=match_results)

    @step
    async def generate_report(
        self, ctx: Context, ev: GenerateReportEvent
    ) -> StopEvent:
        """Generate the final compliance report."""
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Generating final report"))

        prompt = ChatPromptTemplate.from_messages([
            ("system", COMPLIANCE_REPORT_SYSTEM_PROMPT),
            ("user", COMPLIANCE_REPORT_USER_PROMPT)
        ])

        report = await self.llm.astructured_predict(
            ComplianceReport,
            prompt,
            vendor_name=self.vendor_name,
            compliance_results=ev.match_results
        )

        if self._verbose:
            ctx.write_event_to_stream(
                LogEvent(msg=f">> Report generated: {report.model_dump()}")
            )

        # Create and return the StopEvent
        stop_event = StopEvent(
            report=report,
            non_compliant_results=ev.match_results
        )
        
        if self._verbose:
            ctx.write_event_to_stream(
                LogEvent(msg=f">> Returning StopEvent with report: {report.model_dump()}")
            )
            
        return stop_event  # Explicitly return the StopEvent 