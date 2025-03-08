from setuptools import setup, find_packages

setup(
    name="contract_review",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llama-index>=0.12.0",
        "llama-parse>=0.6.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "faiss-cpu>=1.7.0",  # For local vector store
        "python-dotenv>=1.0.0",  # For environment variables
        "numpy>=1.24.0",  # Required by faiss
        "tiktoken>=0.5.0",  # For token counting
        "typing-extensions>=4.5.0",  # For type hints
        "aiohttp>=3.8.0",  # For async HTTP requests
        "tenacity>=8.0.0",  # For retries
        "python-multipart>=0.0.6",  # For file uploads
        "beautifulsoup4>=4.12.0",  # For HTML parsing
        "markdown>=3.4.0",  # For markdown processing
        "llama-index-vector-stores-faiss>=0.1.0",  # For FAISS vector store
    ],
    entry_points={
        'console_scripts': [
            'contract-review=contract_review.cli:run_review',
            'contract-review-local=contract_review.main_local:main',
        ],
    },
    python_requires=">=3.9",
) 