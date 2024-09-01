import click
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from src.workflow_director import WorkflowDirector
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    print("Make sure all required modules are installed and in the correct location.")
    sys.exit(1)


@click.group()
def cli():
    """LLM Workflow Director CLI"""
    pass


@cli.command()
@click.option('--config', default='src/workflow_config.yaml', help='Path to the workflow configuration file')
def run(config):
    """Run the LLM Workflow Director"""
    director = WorkflowDirector(config_path=config)
    director.run()

@cli.command()
@click.option('--config', default='src/workflow_config.yaml', help='Path to the workflow configuration file')
@click.option('--format', default='plain', type=click.Choice(['plain', 'markdown', 'html']), help='Output format for the report')
def report(config, format):
    """Generate a comprehensive project state report"""
    director = WorkflowDirector(config_path=config)
    report = director.generate_project_report(format)
    click.echo(report)

if __name__ == '__main__':
    cli()
