import re
import typing

StrOrRegexList = typing.Sequence[typing.Union[str, re.Pattern]]


def combine_strs_and_regex(
    str_list: typing.Union[typing.Sequence[str], None],
    regex_list: typing.Union[typing.Sequence[str], None],
) -> StrOrRegexList:
    """Combine an optional lists of strings and regex strings
    into a list of strings and compiled regex.

    Parameters
    ----------
    str_list
        Optional list of strings.
    regex_list
        Optional list of regex strings.

    If str_list and regex_list are both None, returns []
    """
    result: StrOrRegexList
    if str_list:
        result = list(str_list)
    else:
        result = []
    if regex_list:
        result += [re.compile(regex_str) for regex_str in regex_list]
    return result
