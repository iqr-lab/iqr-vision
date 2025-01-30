from decimal import Decimal, getcontext
import os
from pathlib import Path
import subprocess
from os.path import dirname, abspath

from tqdm import tqdm

from iqr_vision import hosts

from rosbags.highlevel import AnyReader
import numpy as np
from PIL import Image
import bisect


def transfer(
    local_bag_dir: str,
    remote_bag_path: str,
):
    """
    Transfer a rosbag file from all remote hosts to the local host.

    Args:
        local_bag_dir (str): The directory to save the rosbag files on the local host.
        remote_bag_path (str): The path to the rosbag file on the remote host. Relative to the home directory of the user unless otherwise specified by an absolute path. Must have the .bag extension.
    """
    if remote_bag_path.startswith("/"):
        remote_bag_path = Path(f"{remote_bag_path}")
    elif remote_bag_path.startswith("~"):
        remote_bag_path = Path(remote_bag_path)
    else:
        remote_bag_path = Path("~") / remote_bag_path

    if remote_bag_path.suffix != ".bag":
        raise ValueError("The rosbag file must have the .bag extension.")

    os.system(f"mkdir -p {local_bag_dir}")

    for idx, host in enumerate(hosts):
        transfer_command = f"scp {host}:{remote_bag_path} {local_bag_dir}/{remote_bag_path.stem}_{idx}.bag"
        subprocess.run(transfer_command, shell=True, check=True)


def docker_filter_rosbag(local_bag_dir: str):
    """
    Filter the rosbag files in the given directory using a ROS Noetic docker container. Will save the filtered rosbag files in a subdirectory called filtered_bags.

    Args:
        local_bag_path (str): The directory containing the rosbag files on the local host.
    """
    local_bag_dir = local_bag_dir.rstrip("/")

    file_parent_dir = dirname(abspath(__file__))
    filter_script_path = Path(file_parent_dir) / "scripts" / "filter.sh"

    os.system(f"docker run --name ros_noetic -itd --entrypoint bash ros:noetic")
    os.system(f"docker cp {local_bag_dir}/ ros_noetic:/bags")
    os.system(f"docker cp {filter_script_path} ros_noetic:/")
    os.system(f"docker exec -it ros_noetic bash -c 'cd /bags && /filter.sh'")
    os.system(f"docker cp ros_noetic:/filtered_bags/ {local_bag_dir}/")
    os.system(f"docker stop ros_noetic")
    os.system(f"docker rm ros_noetic")


def save_rosbag_images(
    local_bag_path: str,
    destination_dir: str,
    timestamps: list[str],
):
    """
    Read rosbag file and save the images at the given timestamps.

    Args:
        local_bag_path(str): The path to the rosbag file on the local host.
        destination_dir (str): The directory to save the images.
        timestamps (list[str]): The timestamps to save the images at. Must be in the format of a list of strings in the format of "sec.nanosec".
    """
    os.makedirs(destination_dir, exist_ok=True)

    getcontext().prec = 50

    class DecimalComparesBisect(object):
        def __init__(self, value: str):
            self.value = value

        def __gt__(self, other: str):
            return Decimal(self.value).compare(Decimal(other)) > 0

    bagpath = Path(local_bag_path)
    with AnyReader([bagpath]) as reader:
        connections = [
            x
            for x in reader.connections
            if x.topic == "/device_0/sensor_1/Color_0/image/data"
        ]
        bag_timestamps = [
            str(reader.deserialize(rawdata, connection.msgtype).header.stamp.sec)
            + "."
            + str(
                reader.deserialize(rawdata, connection.msgtype).header.stamp.nanosec
            ).zfill(9)
            for connection, _, rawdata in reader.messages(connections=connections)
        ]

    final_idx = [
        bisect.bisect_left(bag_timestamps, DecimalComparesBisect(timestamp))
        for timestamp in timestamps
    ]

    with AnyReader([bagpath]) as reader:
        connections = [
            x
            for x in reader.connections
            if x.topic == "/device_0/sensor_1/Color_0/image/data"
        ]
        for idx in tqdm(final_idx, desc=f"Extracting {Path(local_bag_path).name}"):
            for sub_idx, (connection, _, rawdata) in enumerate(
                reader.messages(connections=connections)
            ):
                if sub_idx == idx:
                    break
            image = np.array(
                reader.deserialize(rawdata, connection.msgtype).data, dtype=np.uint8
            ).reshape(480, 640, 3)
            im = Image.fromarray(image)
            im.save(f"{destination_dir}/image_{idx}.jpeg")
