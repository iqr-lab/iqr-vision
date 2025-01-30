import typer

from .test import test, echo
from .install import install_app


app = typer.Typer()

# Basic Command Modules
app.command()(test)
app.command("echo")(echo)

# Subcommand Modules
app.add_typer(install_app, name="install")


if __name__ == "__main__":
    app()
