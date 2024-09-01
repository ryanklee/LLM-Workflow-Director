import click
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from src.workflow_director import WorkflowDirector
except ModuleNotFoundError as e:
    if "pkg.workflow.constraint.engine" in str(e):
        print("Error: The pkg.workflow.constraint.engine module is missing.")
        print("This module should be implemented in Go and compiled as a shared library.")
        print("Please make sure the Go module is compiled and the shared library is in the correct location.")
        print("Refer to the project documentation for instructions on compiling the Go module.")
    else:
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

@cli.command()
@click.option('--preview', is_flag=True, help='Preview the conventions without saving')
def conventions(preview):
    """Generate or preview coding conventions"""
    convention_manager = ConventionManager()
    if preview:
        click.echo(yaml.dump(convention_manager.conventions, default_flow_style=False))
    else:
        convention_manager.save_conventions('coding_conventions.yaml')
        click.echo("Coding conventions saved to coding_conventions.yaml")

@cli.command()
def aider_conventions():
    """Generate Aider-compatible coding conventions"""
    convention_manager = ConventionManager()
    click.echo(convention_manager.generate_aider_conventions())

if __name__ == '__main__':
    cli()
