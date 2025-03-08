import asyncio
from pathlib import Path
import faiss
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding

from contract_review.workflows.contract_review import ContractReviewWorkflow
from contract_review.models.events import LogEvent
from llama_index.core.workflow import StopEvent
from contract_review.config.settings import ResultType, DEFAULT_SIMILARITY_TOP_K
from contract_review.config.model_settings import ModelSettings, LLMProvider
from contract_review.utils.logger import setup_logger

logger = setup_logger(__name__)

async def initialize_llm():
    """Initialize the LLM based on configuration."""
    provider = ModelSettings.get_llm_provider()
    model_name = ModelSettings.get_llm_model()
    
    if provider == LLMProvider.OPENAI:
        return OpenAI(model=model_name)
    else:
        return Ollama(
            model=model_name,
            base_url=ModelSettings.get_ollama_base_url(),
            timeout=300,  # 5 minutes timeout
            streaming=True,  # Enable streaming
            max_retries=3,  # Add retry logic
            request_timeout=300  # 5 minutes timeout for HTTP requests
        )

async def initialize_embedding():
    """Initialize the embedding model based on configuration."""
    provider = ModelSettings.get_llm_provider()
    model_name = ModelSettings.get_llm_model()
    
    if provider == LLMProvider.OPENAI:
        return OpenAIEmbedding(model=ModelSettings.get_embedding_model())
    else:
        return OllamaEmbedding(
            model_name=model_name,
            base_url=ModelSettings.get_ollama_base_url(),
            timeout=300,  # 5 minutes timeout
            request_timeout=300  # 5 minutes timeout for HTTP requests
        )

async def main():
    """Run the contract review workflow with local implementations."""
    try:
        # Initialize local vector store for guidelines
        guidelines_dir = Path("data/guidelines")
        if not guidelines_dir.exists():
            raise FileNotFoundError("Guidelines directory not found. Please add your guidelines in data/guidelines/")
            
        # Load and index guidelines
        guidelines_docs = SimpleDirectoryReader(input_dir=str(guidelines_dir)).load_data()
        
        # Set up embedding model
        embed_model = await initialize_embedding()
        Settings.embed_model = embed_model
        
        # Create FAISS index with appropriate dimension
        d = 384 if ModelSettings.get_llm_provider() == LLMProvider.OLLAMA else 1536
        faiss_index = faiss.IndexFlatL2(d)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        
        # Create index and add documents
        index = VectorStoreIndex.from_documents(guidelines_docs, vector_store=vector_store)
        retriever = index.as_retriever(similarity_top_k=DEFAULT_SIMILARITY_TOP_K)

        # Initialize language model
        llm = await initialize_llm()

        # Initialize workflow with SimpleDirectoryReader
        workflow = ContractReviewWorkflow(
            guideline_retriever=retriever,
            llm=llm,
            verbose=True,
            timeout=None,
        )

        # Get the contract path
        contract_path = Path("data/vendor_agreement.md")
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract file not found at {contract_path}")

        # Run the workflow
        handler = workflow.run(contract_path=str(contract_path))
        
        # Stream events and collect the final event
        final_event = None
        async for event in handler.stream_events():
            if isinstance(event, LogEvent):
                if event.delta:
                    print(event.msg, end="")
                else:
                    print(event.msg)
            elif isinstance(event, StopEvent):
                final_event = event
                break

        # Get final results
        if final_event is None:
            # If we didn't get the final event from streaming, try to get it directly
            final_event = await handler
            if final_event is None:
                raise ValueError("Workflow completed but no final event was returned")
            
        if not isinstance(final_event, StopEvent):
            raise ValueError(f"Expected StopEvent, got {type(final_event)}")

        print("\nCompliance Report:")
        print("=" * 50)
        print(str(final_event.report))

        # Print non-compliant results if any
        if final_event.non_compliant_results:
            print("\nNon-Compliant Clauses:")
            print("=" * 50)
            for result in final_event.non_compliant_results:
                print(f"\nClause: {result.clause_text}")
                if result.matched_guideline:
                    print(f"Guideline: {result.matched_guideline.guideline_text}")
                print(f"Notes: {result.notes}")

    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main()) 