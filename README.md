# Contract Review Assistant

A tool for reviewing contracts against GDPR compliance guidelines using AI.

## Features

- Contract analysis using AI
- GDPR compliance checking
- Local and cloud-based implementations
- Detailed compliance reports
- Clause-by-clause analysis

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (for GPT-4)
- LlamaCloud API key (optional, for cloud implementation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ContractReviewAssistant.git
cd ContractReviewAssistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# Option 1: Using pip
pip install -r requirements.txt

# Option 2: Using setuptools
pip install -e .
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key_here
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here  # Optional
```

## Configuration

The project supports two LLM providers:

### OpenAI Configuration
1. Set `LLM_PROVIDER=openai` in your `.env` file
2. Configure your OpenAI API key: `OPENAI_API_KEY=your-api-key`
3. Optionally specify the model: `OPENAI_MODEL=gpt-4`

### Ollama Configuration
1. Install Ollama following instructions at https://ollama.ai
2. Start the Ollama server locally
3. Set `LLM_PROVIDER=ollama` in your `.env` file
4. Configure the model: `OLLAMA_MODEL=llama2` (or any other model you've pulled)
5. Optionally specify a different base URL: `OLLAMA_BASE_URL=http://localhost:11434`

## Usage

### Local Implementation

1. Add your GDPR guidelines to `data/guidelines/` directory
2. Run the local version:
```bash
contract-review-local
```

### Cloud Implementation

1. Set up your LlamaCloud credentials
2. Run the cloud version:
```bash
contract-review
```

### Command Line Options

- `--contract-path`: Path to the contract file (default: data/vendor_agreement.md)
- `--verbose`: Enable verbose output (default: True)

## Project Structure

```
contract_review/
├── config/           # Configuration files
├── models/          # Data models
├── prompts/         # AI prompts
├── utils/           # Utility functions
├── workflows/       # Workflow definitions
├── cli.py           # Command-line interface
├── main.py          # Cloud implementation
└── main_local.py    # Local implementation
```

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details 