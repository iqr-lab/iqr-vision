from pathlib import Path
from string import Template
from dotenv import load_dotenv
import os

load_dotenv()

try:
    hosts = os.getenv("HOSTS").split(",")
    delimited_hosts = ",".join(hosts)
    parallel_template = Template(
        Template(
            """parallel -N0 --sshlogin $delimited_hosts "$command" ::: seq $num_hosts"""
        ).safe_substitute(delimited_hosts=delimited_hosts, num_hosts=len(hosts))
    )
    module_directory = Path("~") / "opt" / "iqr-vision-utils"
except:
    print("No HOSTS in .env file")
    exit(1)
