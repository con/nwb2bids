#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

help_content = subprocess.run(
    ["nwb2bids", "--help"], check=True, text=True, encoding="utf-8", stdout=subprocess.PIPE
).stdout

help_content = f"```shell\n$ nwb2bids --help\n\n{help_content}\n```\n"

convert_help_content = subprocess.run(
    ["nwb2bids", "convert", "--help"],
    check=True,
    text=True,
    encoding="utf-8",
    stdout=subprocess.PIPE,
).stdout

convert_help_content = f"```shell\n$ nwb2bids convert --help\n\n{convert_help_content}\n```\n"

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
text = re.sub(
    r"(?<=<!-- BEGIN HELP -->\n).*(?=^<!-- END HELP -->)",
    help_content,
    text,
    flags=re.S | re.M,
)

text = re.sub(
    r"(?<=<!-- BEGIN CONVERT HELP -->\n).*(?=^<!-- END CONVERT HELP -->)",
    convert_help_content,
    text,
    flags=re.S | re.M,
)

readme.write_text(text, encoding="utf-8")
