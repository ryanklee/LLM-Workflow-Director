import click
from workflow_director import WorkflowDirector


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


if __name__ == '__main__':
    cli()
