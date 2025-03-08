# Changelog

All notable changes to the Contract Review Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of contract review workflow
- Support for both OpenAI and Ollama LLM providers
- FAISS vector store integration for efficient guideline retrieval
- Asynchronous workflow execution with proper event handling
- Caching mechanism for contract extraction results
- Comprehensive logging system

### Fixed
- Resolved workflow completion issue where final events weren't being properly captured
- Improved event streaming and handling in main workflow execution
- Added robust error handling for workflow completion events

### Technical Details
- Using dimension 384 for Ollama embeddings and 1536 for OpenAI embeddings
- Implemented retry logic for clause compliance checks (max 3 retries)
- Added proper timeout settings for LLM calls (300 seconds)
- Structured workflow output directory management

## Current Status
- Application is functioning locally with proper event handling
- Supports both local (Ollama) and cloud (OpenAI) LLM providers
- Successfully processes contract documents and generates compliance reports
- Implements semantic search for guideline matching
- Provides detailed logging and progress updates during execution

## Next Steps
- Add unit tests for core functionality
- Implement CI/CD pipeline
- Add support for batch processing of multiple contracts
- Enhance error reporting and recovery mechanisms
- Consider adding a web interface for easier interaction 