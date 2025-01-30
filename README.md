# IQR Vision Utilities

This is a collection of Python utility packages for use with the IQR Vision system. Although much of the code is specific to IQR Lab's setup, the code is generally useful for similar Realsense camera + edge node systems (see more details [here](https://iqr.cs.yale.edu/docs/#edge-camera-systems)).

## Installation
1. Install GNU Parallel `gnu-parallel` on your computer and all the edge nodes:
    ```bash
    sudo apt-get install parallel
    ```
1. Create a `.env` in your root directory following `.env.example`.
1. Ensure that you can `ssh` into each specificied host in the `HOSTS` variable with the following command format:
    ```bash
    ssh [hostname]
    ```
    <details>
    <summary>SSH Config Details</summary>

    ```bash
    Host iqr-vision-1
        HostName iqr-vision-1.local
        User lab
        IdentityFile ~/.ssh/iqr-vision-1
    ```

    </details>
1. Each host should have `librealsense2` properly installed and have a camera connected. You can test this with the following command:
    ```bash
    iqr-vision test
    ```
    or if you prefer to use `runpy`
    ```bash
    python -m iqr_vision_utils.cli test
    ```
    Expected output for each host:
    
    ```bash
    Connected devices:
    1) [USB] Intel RealSense D455 s/n [...], update serial number: [...], firmware version: [...]
    ```

## Usage

### `multivideo`

This module is specifically used for rgb color related functions. See the relevant function documentation for more details.

You must first install the `iqr-multivideo` executable to the edge nodes. Please do this through the cli: 

```bash
iqr-vision install multivideo
```

Note: **Ensure that you call `multivideo.close()` after `multivideo.start()`**. The start function is running an executable under the hood, which will terminate eventually on its own after the required duration, but subsequent runs will fail as the camera stream is already occupied. This is avoided by the `pre_stop: bool = True` parameter on the `multivideo.start()`

Example usage:
```python
from pathlib import Path

from iqr_vision_utils import multivideo


def record_timestamps():
    import time

    timestamps: list[str] = []
    before_loop = time.time()
    while time.time() - before_loop < 10: # Record for 10 seconds
        nano = time.time_ns()
        timestamps.append(
            f"{nano // 1_000_000_000}.{str(nano % 1_000_000_000).zfill(9)}"
        )
        time.sleep(0.05)  # Record timestamps for every 50ms

    return timestamps


pids = multivideo.start(duration=60, bag_path="~/test_dir/test.bag")

timestamps = record_timestamps()

multivideo.stop(pids)

multivideo.transfer(local_bag_dir="bags/", remote_bag_path="~/test_dir/test.bag")

multivideo.docker_filter_rosbag(
    local_bag_dir="bags/",
)

for bag_path in Path("bags/filtered_bags").glob("*.bag"):
    multivideo.save_rosbag_images(
        local_bag_path=bag_path,
        destination_dir=f"images/{bag_path.stem}/",
        timestamps=timestamps,
    )

```

## Contributing

This is a relative straightforward Python package, proceed with standard practices. Document functions with [Google format Python docstrings](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings) and format code with `black`.