import click
from src.workflow_director import WorkflowDirector


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
