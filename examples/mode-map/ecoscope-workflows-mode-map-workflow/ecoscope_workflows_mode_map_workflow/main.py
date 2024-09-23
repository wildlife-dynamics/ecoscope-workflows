import click

from .dags import sequential_mock_io


@click.command()
def main():
    sequential_mock_io()


if __name__ == "__main__":
    main()
