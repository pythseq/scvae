# ======================================================================== #
#
# Copyright (c) 2017 - 2019 scVAE authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ======================================================================== #

import os
import re
import sys
import shutil
import time
import urllib.request
from contextlib import contextmanager
from math import floor


def format_time(t):
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(t))


def format_duration(seconds):
    if seconds < 0.001:
        return "<1 ms"
    elif seconds < 1:
        return "{:.0f} ms".format(1000 * seconds)
    elif seconds < 60:
        return "{:.3g} s".format(seconds)
    elif seconds < 60 * 60:
        minutes = floor(seconds / 60)
        seconds = seconds % 60
        if round(seconds) == 60:
            seconds = 0
            minutes += 1
        return "{:.0f}m {:.0f}s".format(minutes, seconds)
    else:
        hours = floor(seconds / 60 / 60)
        minutes = floor((seconds / 60) % 60)
        seconds = seconds % 60
        if round(seconds) == 60:
            seconds = 0
            minutes += 1
        if minutes == 60:
            minutes = 0
            hours += 1
        return "{:.0f}h {:.0f}m {:.0f}s".format(hours, minutes, seconds)


def normalise_string(s):

    s = s.lower()

    replacements = {
        "_": [" ", "-", "/"],
        "": ["(", ")", ",", "$"]
    }

    for replacement, characters in replacements.items():
        pattern = "[" + re.escape("".join(characters)) + "]"
        s = re.sub(pattern, replacement, s)

    return s


def proper_string(original_string, translation, normalise=True):

    if normalise:
        transformed_string = normalise_string(original_string)
    else:
        transformed_string = original_string

    for proper_string, related_strings in translation.items():
        if transformed_string in related_strings:
            return proper_string

    return original_string


def capitalise_string(original_string):
    string_parts = re.split(
        pattern=r"(\s)",
        string=original_string,
        maxsplit=1
    )
    if len(string_parts) == 3:
        first_word, split_character, rest_of_original_string = string_parts
        if re.match(pattern=r"[A-Z]", string=first_word):
            capitalised_first_word = first_word
        else:
            capitalised_first_word = first_word.capitalize()
        capitalised_string = (
            capitalised_first_word + split_character + rest_of_original_string)
    else:
        if re.match(pattern=r"[A-Z]", string=original_string):
            capitalised_string = original_string
        else:
            capitalised_string = original_string.capitalize()
    return capitalised_string


def enumerate_strings(strings, conjunction="and"):
    if not isinstance(strings, list):
        raise ValueError("`strings` should be a list of strings.")
    conjunction = conjunction.strip()
    n_strings = len(strings)
    if n_strings == 1:
        enumerated_string = strings[0]
    elif n_strings == 2:
        enumerated_string = " {} ".format(conjunction).join(strings)
    elif n_strings >= 3:
        enumerated_string = "{}, {} {}".format(
            ", ".join(strings[:-1]),
            conjunction,
            strings[-1]
        )
    else:
        raise ValueError("`strings` does not contain any strings.")
    return enumerated_string


def heading(string, underline_symbol="-", plain=False):
    string = "{}\n{}\n".format(string, _underline(string, underline_symbol))
    if not plain:
        string = _bold(string)
    return string


def title(string, plain=False):
    underline_symbol = "═"
    return heading(string, underline_symbol, plain)


def subtitle(string, plain=False):
    underline_symbol = "─"
    return heading(string, underline_symbol, plain)


def subheading(string, plain=False):
    underline_symbol = "╌"
    return heading(string, underline_symbol, plain)


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def copy_file(url, path):
    shutil.copyfile(url, path)


def remove_empty_directories(source_directory):
    for directory_path, _, _ in os.walk(source_directory, topdown=False):
        if directory_path == source_directory:
            break
        try:
            os.rmdir(directory_path)
        except OSError:
            pass


def download_file(url, path):
    urllib.request.urlretrieve(url, path, _download_report_hook)


def _download_report_hook(block_num, block_size, total_size):
    bytes_read = block_num * block_size
    if total_size > 0:
        percent = bytes_read / total_size * 100
        sys.stderr.write("\r{:3.0f}%.".format(percent))
        if bytes_read >= total_size:
            sys.stderr.write("\n")
    else:
        sys.stderr.write("\r{:d} bytes.".format(bytes_read))


def _bold(string):
    """Convert to bold type."""
    bold_format = "\033[1m"
    reset_format = "\033[0m"
    return bold_format + string + reset_format


def _underline(string, character="-"):
    """Convert string to header marks"""
    return character * len(string)
