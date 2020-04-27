from collections import abc
import datetime as dtm
import json
import os
import pprint
import re
import subprocess
import sys
import time
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union
import urllib.request
import logging

from bs4 import BeautifulSoup
import requests
# import tldextract


def pure(func):
    """
    Decorator to annotate a function as "pure" in the functional programming sense. DOES NOTHING.

    TL;DR: You can annotate a function as pure if it doesn't modify (a) its
    arguments, (b) global variables or (c) external data stores (databases,
    POST-ing to APIs etc.).

    *Actually* we relax this to match Python style, so a "pure" function means:
    - it always return same result for same arguments
    - does not have side effect (like changing data in a db etc.)
    - BUT it CAN occasionally LOG or PRINT degbugging or profiling data
    - AND it CAN THROW EXCEPTIONS (because they are too pervasive in Python and
      disallowing them would be too impractical and unidiomatic)
    """
    func._IS_PURE_ = True
    return func


pp = pprint.PrettyPrinter(indent=4).pprint


@pure
def if_none(a: Any, b: Any) -> Any:
    return b if a is None else a


@pure
def get_in_obj(obj: Any, path: Union[str, List[str]], *args) -> Any:
    """
    Get path in object(s) (using getattr), with optional default.

    Example
    -------
    >>> get_in_obj(address, 'street.number')

    ...does: `getattr(getattr(address, 'street'), 'number')`

    >>> get_in_obj(employee, ['detachment', 'department', 'name'], 'UNKNOWN')

    ...behaves similarly, but wraps `getattr` calls in `try ... catch`, and
    returns 'UNKNOWN' if AttributeError is thrown.
    """
    assert len(args) <= 1
    has_default = bool(len(args))
    if has_default:
        default = args[0]

    path = list(reversed(path.split(".") if type(path) is str else path))

    r = obj
    travelled_path = []
    while len(path):
        fld = path.pop()
        travelled_path.append(fld)
        try:
            r = getattr(r, fld)
        except AttributeError:
            if has_default:
                return default
            else:
                raise AttributeError(f"no attribute '{'.'.join(travelled_path)}'")

    return r


@pure
def get_in_dict(obj: Any, path: Union[str, List[Any]], *args) -> Any:
    """
    Get path in object(s) (using getattr), with optional default.

    Example
    -------
    >>> get_in_obj(address, 'street.number')

    ...does: address['street']['number']

    >>> get_in_obj(employee, ['departents', 0, 'name'], 'UNKNOWN')

    ...behaves similarly, but wraps attribute accesses in `try ... catch`, and
    return 'UNKNOWN' if IndexError, TypeError or KeyError is thrown.

    Notes
    -----
    *IMPORTANT:* Note that if you want to use an integer index (into a list, tuple etc.),
    you must pass the path as a list. A path like `departments.0.name` will index as
    `employee['departments']['0']['name']` - we try not to *guess* the intention of the
    user, maybe a string attribute like "0" was actually intended...
    """
    assert len(args) <= 1
    has_default = bool(len(args))
    if has_default:
        default = args[0]

    path = list(reversed(path.split(".") if type(path) is str else path))

    r = obj
    travelled_path = []
    while len(path):
        fld = path.pop()
        travelled_path.append(fld)
        try:
            r = r[fld]
        except (IndexError, TypeError, KeyError):
            if has_default:
                return default
            else:
                raise AttributeError(f"no value at path '{'.'.join(travelled_path)}'")

    return r


@pure
def getter_obj(path: Union[str, List[str]], *args) -> Any:
    return lambda obj: get_in_obj(obj, path, *args)


@pure
def getter_dict(path: Union[str, List[Any]], *args) -> Any:
    return lambda obj: get_in_obj(obj, path, *args)


def _json_converter(o):
    if isinstance(o, dtm.datetime):
        return o.isoformat()
    if hasattr(o, "_json"):
        return o._json
    return str(o)


@pure
def json_dumps(data: Any, indent: int = 2, **kwargs) -> str:
    """JSON serializer that doesn't choke on datetimes.
    """
    return json.dumps(data, default=_json_converter, indent=indent, **kwargs)


IMAGE_FILE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "jpe",
    "jif",
    "jfi",
    "jfif",
    "jp2",
    "jpx",
    "j2k",
    "j2c",
    "jpf",
    "jpm",
    "mj2",
    "jxr",
    "png",
    "webp",
    "tiff",
    "tif",
    "raw",
    "bmp",
    "dib",
    "xbm",
    "apng",
    "gif",
    "heif",
    "heic",
    "svg",
    "svgz",
    "eps",
}

VIDEO_FILE_EXTENSIONS = {
    "webm",
    "avi",
    "mkv",
    "wmv",
    "mpg",
    "mp2",
    "mpeg",
    "mpe",
    "mpv",
    "mpeg4",
    "mp4",
    "m4v",
    "m4p",
    "mov",
    "qt",
    "3gp",
    "3gp2",
    "3g2",
    "ogv",
    "ogx",
    "flv",
    "swf",
    "m2t",
    "m2ts",
    "mxf",
    "gxf",
}

AUDIO_FILE_EXTENSIONS = {
    "m4a",
    "f4a",
    "m4b",
    "m4r",
    "f4b",
    "ogg",
    "oga",
    "mp3",
    "wav",
    "wma",
    "weba",
    "flac",
    "aac",
    "aa",
    "aax",
    "aiff",
    "alac",
}

COMMON_DOC_EXTENSIONS = {
    "pdf",
    "dot",
    "dotm",
    "doc",
    "docm",
    "docx",
    "csv",
    "xls",
    "xlt",
    "xlm",
    "xlsx",
    "xlsb",
    "xlsm",
    "xltx",
    "xltm",
    "ppt",
    "pps",
    "pptx",
    "ppsx",
    "pptm",
    "rtf",
    "wps",
    "xps",
    "eps",
    "dbf",
    "odt",
    "ods",
}

FILE_EXTENSIONS = (
    IMAGE_FILE_EXTENSIONS.union(IMAGE_FILE_EXTENSIONS)
    .union(VIDEO_FILE_EXTENSIONS)
    .union(AUDIO_FILE_EXTENSIONS)
    .union(COMMON_DOC_EXTENSIONS)
)


@pure
def extension_from_url(url: str) -> Optional[str]:
    # ignore after first "#" from left
    if (i_pound := url.find("#")) != -1:
        url = url[:i_pound]
    # ignore after first "?" from left
    if (i_qm := url.find("?")) != -1:
        url = url[:i_qm]
    # get extension if any
    if m := re.search(r"\.([^.]+)$", url):
        return m.groups(0)[0]
    else:
        return None


@pure
def is_url_to_file(url: str) -> bool:
    if not url:
        return False
    return extension_from_url(url) in FILE_EXTENSIONS


@pure
def medium_type_from_url_extension(url: str) -> Optional[str]:
    ext = extension_from_url(url)
    # type from extension
    if not ext:
        return None
    if ext in IMAGE_FILE_EXTENSIONS:
        return "image"
    if ext in VIDEO_FILE_EXTENSIONS:
        return "video"
    if ext in AUDIO_FILE_EXTENSIONS:
        return "audio"
    return None


@pure
def struct_time_to_datetime(struct_time: Optional[time.struct_time],) -> Optional[dtm.datetime]:
    if struct_time is None:
        return None
    YmdHMS = tuple(struct_time)[:6]
    tz = dtm.timezone(dtm.timedelta(seconds=struct_time.tm_gmtoff or 0))
    tzdt = dtm.datetime(*YmdHMS, tzinfo=tz)
    return tzdt


@pure
def struct_time_to_naive_datetime(
    struct_time: Optional[time.struct_time],
) -> Optional[dtm.datetime]:
    if struct_time is None:
        return None
    return dtm.datetime.fromtimestamp(time.mktime(struct_time))


@pure
def struct_time_to_iso_str(struct_time: time.struct_time) -> str:
    return struct_time_to_datetime(struct_time).isoformat()


@pure
def timestamp_to_iso_str(ts: Optional[int]) -> Optional[str]:
    if ts is None:
        return None
    return dtm.datetime.fromtimestamp(ts, dtm.timezone.utc).isoformat()


# @pure
# def strip_html_tags(s: Optional[str]) -> Optional[str]:
#     if s is None:
#         return None
#     return BeautifulSoup(s, "html.parser").text.strip()


def get_now_utc_iso_str():
    return dtm.datetime.utcnow().replace(tzinfo=dtm.timezone.utc).isoformat()


# @pure
# def get_tld(url: Optional[str]) -> Optional[str]:
#     if not url:
#         return None
#     tldr = tldextract.extract(url)
#     return "%s.%s" % (tldr.domain, tldr.suffix)


def trace_proc(label: str = ""):
    """Debug helper for code using multiprocessing.
    """
    print(f"~~~> Process {os.getpid()}, child of {os.getppid()} [{label}]")


class DataObject:
    def __repr__(self):
        return str({k: v for k, v in vars(self).items()})


def data_to_object(data: Union[Mapping[str, Any], Iterable]) -> object:
    """
    Example
    -------
    >>> data = {
    ...     "name": "Bob Howard",
    ...     "positions": [{"department": "ER", "manager_id": 13}],
    ... }
    ... data_to_object(data).positions[0].manager_id
    13
    """
    if isinstance(data, abc.Mapping):
        r = DataObject()
        for k, v in data.items():
            if type(v) is dict or type(v) is list:
                setattr(r, k, data_to_object(v))
            else:
                setattr(r, k, v)
        return r
    elif isinstance(data, abc.Iterable):
        return [data_to_object(e) for e in data]
    else:
        return data


URL_SHOTENER_DOMAINS = {
    "bit.do",
    "t.co",
    "lnkd.in",
    "db.tt",
    "qr.ae",
    "adf.ly",
    "goo.gl",
    "bit.ly",
    "ift.tt",
    "cur.lv",
    "tinyurl.com",
    "ow.ly",
    "bit.ly",
    "ity.im",
    "q.gs",
    "is.gd",
    "po.st",
    "bc.vc",
    "u.to",
    "j.mp",
    "buzurl.com",
    "cutt.us",
    "u.bb",
    "yourls.org",
    "x.co",
    "scrnch.me",
    "filoops.info",
    "vzturl.com",
    "qr.net",
    "1url.com",
    "tweez.me",
    "v.gd",
    "tr.im",
    "virg.in",
    "lc.chat",
    "tiny.cc",
    "soo.gd",
    "rb.gy",
    "cnn.it",
    "go.aws",
}


def is_shorturl_domain(domain: Optional[str]) -> bool:
    if not domain:
        return False
    if len(domain) == 4:
        return True
    return domain in URL_SHOTENER_DOMAINS


def is_shortened_url(url):
    return get_tld(url) in URL_SHOTENER_DOMAINS


def ts_print(*args):
    print("[%s]" % dtm.datetime.now(), *args)


def ts_pp(label, x):
    print("[%s] %s: " % (dtm.datetime.now(), label), end="")
    pprint.pprint(x)


def err_print(*args, **kwargs):
    print("[%s]" % dtm.datetime.now(), *args, file=sys.stderr, **kwargs)


def run(
    cmd: List[str],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.PIPE,
    cinput=None,
    shell=False,
    can_fail=False,
    echo=True,
) -> Tuple[int, bytes, bytes]:
    """Way to run commands that behaves identically across Python versions.
    """
    if echo:
        ts_print("+", " ".join(cmd))
    try:
        p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, stdin=stdin, shell=shell,)
        out, err = p.communicate(cinput)
        r = p.returncode
    except Exception as exc:
        if echo:
            err_print("ERROR (exception):", exc)
        if not can_fail:
            raise exc
        r = -1000
        out = b""
        err = str(exc).encode("utf-8", errors="ignore")
        return r, out, err
    if r != 0:
        if echo:
            err_print("ERROR (code %d):" % r, err)
        if not can_fail:
            raise Exception("Error executing command", " ".join(cmd), r, err)
    return r, out, err


def is_running(script_name: str) -> bool:
    return_code, out, _err = run(["pgrep", "-f", script_name], can_fail=True, echo=False)
    if return_code != 0:  # pgrep found nothing (error), so not running
        return False
    this_pid = os.getpid()
    parent_pid = os.getppid()
    for pid in map(int, out.strip(b"\n").split(b"\n")):
        if pid != this_pid and pid != parent_pid:
            return True
    return False


def unshorten_url(
    url: str,
    *,
    depth: Optional[int] = None,
    max_depth: int = 10,
    timeout_s: float = 3.0,
    user_agent: Optional[str] = None,
) -> Tuple[Optional[str], Any]:
    headers = None
    if user_agent is not None:
        headers = {"User-Agent": user_agent}

    curr_url = url
    curr_depth = 0
    seen_urls = {}

    while True:
        try:
            if depth is not None and curr_depth >= depth:
                return curr_url, None

            if curr_depth >= max_depth:
                raise IOError(
                    f"Exceeded max depth while trying to unshorten URL: {url}, {curr_depth + 1}"
                )

            if curr_url in seen_urls:
                raise IOError(
                    f"Loop detected while trying to unshorten URL: {url}, {list(seen_urls.keys()) + [curr_url]}"
                )

            r = requests.get(curr_url, allow_redirects=False, headers=headers, timeout=timeout_s)

            seen_urls[curr_url] = True

            if r.status_code // 100 == 2:
                return r.url, None
            elif r.status_code // 100 == 3:
                curr_url = r.headers["Location"]
            else:
                return (
                    r.url,
                    IOError(
                        f"Bad HTTP status while trying to unshorten URL: {url}, {r.status_code} for {curr_url}"
                    ),
                )
        except Exception as exc:
            return None, exc
        curr_depth += 1


PAGE_MIME_TYPES = {
    'application/xhtml+xml',
    'text/html',
    'text/plain',
}


FAIL_ENCODING = 'ISO-8859-1'


def get_html_from_response(response: requests.Response) -> str:
    """Copied from newspaper.network."""
    if response.encoding != FAIL_ENCODING:
        # return response as a unicode string
        html = response.text
    else:
        html = response.content
        if 'charset' not in response.headers.get('content-type'):
            encodings = requests.utils.get_encodings_from_content(response.text)
            if len(encodings) > 0:
                response.encoding = encodings[0]
                html = response.text

    return html or ''
