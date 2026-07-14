"""
global config
"""

import configparser
from pathlib import Path
import warnings

import logging

logger = logging.getLogger(__name__)


def _escape_split(s, delim=",", escape="\\"):
    """Split a string on a delimiter while respecting escape characters.

    A delimiter preceded by the escape character is treated as a literal
    character and does not split the string. A double escape (``\\\\``) is
    treated as a literal escape character.

    Args:
        s (str): Input string to split.
        delim (str): Delimiter character. Default is ``","``.
        escape (str): Escape character. Default is ``"\\"``.

    Returns:
        list: List of token strings.
    """
    tokens = []
    previous_escape = False
    subtoken = ""
    for k in range(len(s)):
        if s[k] == delim and (not previous_escape):
            if len(subtoken) > 0:
                tokens.append(subtoken)
            subtoken = ""  # reset subtoken
        else:
            # ESCAPE DELIM  -> DELIM
            if previous_escape and s[k] != escape and s[k] == delim:
                subtoken = subtoken[:-1] + s[k]
            else:
                # add to subtoken
                subtoken += s[k]
            # set previous_escape flag:
            # If for current char is escape (True and s[k]=='\\') and previous_escape is False -> set it to True
            # If for current char is escape (True and s[k]=='\\') and previous_escape is True -> case of '\\\\' -> escaping an escape character -> set it back to False
            # if current char is no escape character -> set it to false
            previous_escape = (not previous_escape) and (s[k] == escape)
    if len(subtoken) > 0:
        tokens.append(subtoken)
    return tokens


def _kwarg_converter(s: str):
    """Parse a comma-separated string of positional and keyword arguments.

    Used as a custom converter for :mod:`configparser` to parse config values
    of the form ``"arg1, key=value, arg2"`` into Python args and kwargs.

    Args:
        s (str): Raw config string to parse.

    Returns:
        tuple: ``(args, kwargs)`` where ``args`` is a list of positional
            argument strings and ``kwargs`` is a dict of keyword argument strings.
    """
    tokens = _escape_split(s, ",", escape="\\")
    args = []
    kwargs = {}
    for k in tokens:
        subtokens = _escape_split(k, "=", escape="\\")
        if len(subtokens) == 1:
            args.append(subtokens[0])
        else:
            kwargs[subtokens[0].strip()] = subtokens[1].strip()
    return args, kwargs


def _get_sl_config(configname="spinlab.cfg"):
    """Load the SpinLab configuration file.

    Searches three locations in order of increasing precedence:

    1. The directory containing this module (package default ``spinlab.cfg``)
    2. The user's home directory
    3. The current working directory

    A file found later in the list overrides values from earlier files, allowing
    users to customize settings without modifying the package defaults.

    Args:
        configname (str): Name of the configuration file. Default is ``"spinlab.cfg"``.

    Returns:
        configparser.ConfigParser: Populated configuration object with custom
            ``list`` and ``args_kwargs`` converters.
    """
    config = configparser.ConfigParser(
        converters={
            "list": lambda x: list(x.strip("[").strip("]").split(",")),
            "args_kwargs": _kwarg_converter,
        }
    )

    # define three possible locations:
    spinlab_current_config = Path.cwd() / configname
    spinlab_home_config = Path.home() / configname

    spinlab_cfg_folder = str(
        Path(__file__).parent
    )  # / configname #.with_name("config"))
    spinlab_global_config = Path(spinlab_cfg_folder) / configname

    config_read_list = [
        spinlab_global_config,
        spinlab_home_config,
        spinlab_current_config,
    ]

    # user defined takes precedence
    config.read(config_read_list)
    return config


SpinLAB_CONFIG = _get_sl_config()
