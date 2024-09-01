import click
from workflow_director import WorkflowDirector


@click.group()
def cli():
    """LLM Workflow Director CLI"""
    pass


@cli.command()
def run():
    """Run the LLM Workflow Director"""
    director = WorkflowDirector()
    director.run()


if __name__ == '__main__':
    cli()
