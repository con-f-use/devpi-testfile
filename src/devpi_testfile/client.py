from pluggy import HookimplMarker
import appdirs
import json
import os
import collections
from pathlib import Path as P
import py

from devpi.test import DevIndex, post_tox_json_report
from devpi_common.url import URL


import tempfile

example_file, example_json = tempfile.mkstemp(suffix=".json", text=True)
example_file = f = os.fdopen(example_file, "w")
# Example from tox documentation
example_file.write(
    r"""
    {
    "testenvs": {
        "py27": {
        "python": {
            "executable": "/home/hpk/p/tox/.tox/py27/bin/python",
            "version": "2.7.3 (default, Aug  1 2012, 05:14:39) \n[GCC 4.6.3]",
            "version_info": [ 2, 7, 3, "final", 0 ]
        },
        "test": [
            {
            "output": "...",
            "command": [
                "/home/hpk/p/tox/.tox/py27/bin/pytest",
                "--instafail",
                "--junitxml=/home/hpk/p/tox/.tox/py27/log/junit-py27.xml",
                "tests/test_config.py"
            ],
            "retcode": "0"
            }
        ],
        "setup": []
        }
    },
    "platform": "linux2",
    "installpkg": {
        "basename": "tox-1.6.0.dev1.zip",
        "sha256": "b6982dde5789a167c4c35af0d34ef72176d0575955f5331ad04aee9f23af4326"
    },
    "toxversion": "1.6.0.dev1",
    "reportversion": "1"
    }"""
)
example_file.close()


client_hookimpl = HookimplMarker("devpiclient")
devpi_testfile_data_dir = appdirs.user_data_dir("devpi-testfile", "devpi")
PkgTestInfo = collections.namedtuple("PkgTestInfo", ["pkg", "hash", "path", "data"])


def testfile_arguments(parser):
    """Upload test result from tox result files."""

    parser.add_argument(
        "--index",
        default=None,
        help="index to upload results to, defaults to current index. "
        "Either just the NAME, using the current user, USER/NAME using "
        "the current server or a full URL for another server.",
    )

    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="Just list the release files the tests pertain to.",
    )

    parser.add_argument(
        "resultfile",
        metavar="resultfile",
        type=str,
        default=None,
        action="store",
        nargs="+",
        help="Test result file from run with 'tox --result-json' ...",
    )


def load_result(path):
    path = P(path)
    data = json.load(path.open("r"))
    pkg = data["installpkg"]
    return PkgTestInfo(pkg=pkg["basename"], hash=pkg["sha256"], path=path, data=data)


assert load_result(example_json)[:2] == (
    "tox-1.6.0.dev1.zip",
    "b6982dde5789a167c4c35af0d34ef72176d0575955f5331ad04aee9f23af4326",
)


def normalize_index(index):
    return index  # ToDo: implement this


def upload_result(hub, result, index):
    #
    # url = URL(link.href)
    # post_tox_json_report(hub, url, result.data)
    pass  # ToDo: implement this


def handle_testfile(hub, args):
    results = map(load_result, args.resultfile)

    if args.list is True:
        for result in results:
            print(result.pkg, result.hash)
        return True

    current = hub.current
    index = args.index
    if index:
        if index.startswith(("http:", "https:")):
            current = hub.current.switch_to_temporary(hub, index)
            index = None
        elif index.count("/") > 1:
            hub.fatal("index %r not of form URL, USER/NAME or NAME" % index)
    tmpdir = py.path.local.make_numbered_dir("devpi-test", keep=3)
    devindex = DevIndex(hub, tmpdir, current)
    hub.debug(f"devindex: {devindex.current}")
    for result in results:
        upload_result(result, devindex)


class Object(object):
    pass


example_object = Object()
example_object.resultfile = [example_json, example_json]
example_object.list = True

assert handle_testfile(None, example_object) is True


@client_hookimpl
def devpiclient_subcommands():
    return [(testfile_arguments, "testfile", "devpi_testfile.client:handle_testfile")]


def main(hub, args):
    for pkgspec in args.pkgspec:
        versioninfo = devindex.get_matching_versioninfo(pkgspec, index)
        if not versioninfo:
            hub.fatal("could not find/receive links for", pkgspec)
        links = versioninfo.get_links("releasefile")
        if not links:
            hub.fatal("could not find/receive links for", pkgspec)

        universal_only = args.select is None
        sdist_links, wheel_links = find_sdist_and_wheels(
            hub, links, universal_only=universal_only
        )
        toxrunargs = prepare_toxrun_args(
            devindex, versioninfo, sdist_links, wheel_links, select=args.select
        )
        all_ret = 0
        if args.list:
            hub.info("would test:")
        for toxargs in toxrunargs:
            if args.list:
                hub.info("  ", toxargs[0].href)
                continue
            ret = devindex.runtox(*toxargs, upload_tox_results=args.upload_tox_results)
            if ret != 0:
                all_ret = 1
    return all_ret
