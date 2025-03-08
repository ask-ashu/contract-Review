import asyncio
from pathlib import Path
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_parse import LlamaParse
from llama_index.llms.openai import OpenAI

from contract_review.workflows.contract_review import ContractReviewWorkflow
from contract_review.models.events import LogEvent
from contract_review.config.settings import (
    LLAMA_CLOUD_CONFIG,
    ResultType,
    DEFAULT_SIMILARITY_TOP_K
)
from contract_review.utils.logger import setup_logger

logger = setup_logger(__name__)

async def main():
    """Run the contract review workflow."""
    try:
        # Initialize LlamaCloud Index and retriever
        index = LlamaCloudIndex(
            name=LLAMA_CLOUD_CONFIG["name"],
            project_name=LLAMA_CLOUD_CONFIG["project_name"],
            organization_id=LLAMA_CLOUD_CONFIG["organization_id"],
        )
        retriever = index.as_retriever(similarity_top_k=DEFAULT_SIMILARITY_TOP_K)

        # Initialize document parser
        parser = LlamaParse(result_type=ResultType.MARKDOWN.value)

        # Initialize language model
        llm = OpenAI(model="gpt-4")

        # Initialize workflow
        workflow = ContractReviewWorkflow(
            parser=parser,
            guideline_retriever=retriever,
            llm=llm,
            verbose=True,
            timeout=None,  # don't worry about timeout to make sure it completes
        )

        # Get the contract path
        contract_path = Path("data/vendor_agreement.md")
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract file not found at {contract_path}")

        # Run the workflow
        handler = workflow.run(contract_path=str(contract_path))
        
        # Stream events
        async for event in handler.stream_events():
            if isinstance(event, LogEvent):
                if event.delta:
                    print(event.msg, end="")
                else:
                    print(event.msg)

        # Get final results
        response_dict = await handler
        print("\nCompliance Report:")
        print("=" * 50)
        print(str(response_dict["report"]))

        # Print non-compliant results if any
        if response_dict["non_compliant_results"]:
            print("\nNon-Compliant Clauses:")
            print("=" * 50)
            for result in response_dict["non_compliant_results"]:
                print(f"\nClause: {result.clause_text}")
                print(f"Guideline: {result.matched_guideline.guideline_text}")
                print(f"Notes: {result.notes}")

    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main()) 