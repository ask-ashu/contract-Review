import click
import asyncio
from pathlib import Path
from contract_review.main import main
from contract_review.utils.logger import setup_logger

logger = setup_logger(__name__)

@click.command()
@click.option(
    '--contract-path',
    type=click.Path(exists=True),
    default="data/vendor_agreement.md",
    help='Path to the contract file to analyze'
)
@click.option(
    '--verbose',
    is_flag=True,
    default=True,
    help='Enable verbose output'
)
def run_review(contract_path: str, verbose: bool):
    """Run the contract review workflow."""
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    run_review() 