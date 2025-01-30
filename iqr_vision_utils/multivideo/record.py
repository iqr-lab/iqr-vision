import os
from pathlib import Path
from iqr_vision_utils import parallel_template, module_directory, hosts


def start(duration: int, bag_path: str, pre_stop: bool = True) -> list[int]:
    """
    Start the rosbag recording process. Any necessary directories will be created if they do not exist. Any existing files will be overwritten.

    Args:
        duration (int): The maximum duration of the rosbag recording in seconds. This can be cut short by calling stop().
        bag_path (str): The path to save the rosbag file. Relative to the home directory of the user unless otherwise specified by an absolute path. Must have the .bag extension.
        pre_stop (bool): Whether to stop any existing iqr-multivideo recording processes before starting a new one. Defaults to True.
    Returns:
        pids: A list of process IDs for the rosbag recording process.
    """
    if bag_path.startswith("/"):
        bag_path = Path(f"{bag_path}")
    elif bag_path.startswith("~"):
        bag_path = Path(bag_path)
    else:
        bag_path = Path("~") / bag_path

    if bag_path.suffix != ".bag":
        raise ValueError("The rosbag file must have the .bag extension.")

    if pre_stop:
        force_stop_command = parallel_template.safe_substitute(
            command=f"pkill --signal 2 iqr-multivideo"
        )
        os.system(force_stop_command)

    parent_dir = bag_path.parent
    ensure_dir_command = parallel_template.safe_substitute(
        command=f"mkdir -p {parent_dir}"
    )
    os.system(ensure_dir_command)

    record_command = (
        parallel_template.safe_substitute(
            command=f"{module_directory}/multivideo/run.sh {bag_path} {duration}"
        )
        + " > /tmp/out"
    )
    os.system(record_command)
    with open("/tmp/out", "r") as file:
        output = file.read().strip()
        pids = output.split("\n")
    return pids


def stop(
    pids: list,
):
    """
    Stop the rosbag recording process with the given process IDs.

    Args:
        pids (list): A list of process IDs for the rosbag recording process.
    """
    if len(pids) != len(hosts):
        raise ValueError("The number of process IDs must match the number of hosts.")

    for pid, host in zip(pids, hosts):
        os.system(f"ssh {host} kill -2 {pid}")
