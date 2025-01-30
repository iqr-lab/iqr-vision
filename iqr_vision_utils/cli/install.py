import os
from os.path import dirname, abspath
import subprocess
from pathlib import Path
from iqr_vision_utils import hosts, parallel_template, module_directory

import typer

install_app = typer.Typer()


@install_app.command("multivideo")
def install_multivideo():
    """
    Install the multivideo command to ~/opt/iqr-vision-utils/
    """
    file_parent_dir = dirname(abspath(__file__))
    multivideo_path = Path(file_parent_dir) / ".." / "multivideo" / "module"

    ensure_dir_command = parallel_template.safe_substitute(
        command=f"mkdir -p ~/opt/iqr-vision-utils/"
    )
    os.system(ensure_dir_command)

    for host in hosts:
        subprocess.run(
            f"scp -r {multivideo_path}/* {host}:{module_directory}/multivideo/",
            shell=True,
            check=True,
        )

    install_module_command = parallel_template.safe_substitute(
        command=f"{module_directory}/multivideo/install.sh"
    )
    os.system(install_module_command)
