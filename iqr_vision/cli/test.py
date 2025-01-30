import subprocess
import typer
from typing_extensions import Annotated
from iqr_vision import hosts


def test():
    for host in hosts:
        subprocess.run(
            f"echo 'rs-fw-update -l' | ssh -q {host} /usr/bin/bash",
            shell=True,
            check=True,
        )


def echo(
    value: Annotated[str, typer.Argument(help="The value to echo")] = "Hello World!",
):
    print(f"{value}")
