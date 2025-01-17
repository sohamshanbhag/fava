# pylint: disable=redefined-outer-name

from __future__ import annotations

import sys
from socket import socket
from subprocess import PIPE
from subprocess import Popen
from subprocess import STDOUT
from time import sleep
from time import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path
    from typing import IO


@pytest.fixture()
def open_port() -> int:
    """Get an open port."""
    sock = socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    assert isinstance(port, int)
    return port


TIMEOUT = 10


def output_contains(stdout: IO[str], output: str) -> bool:
    endtime = time() + TIMEOUT
    while time() < endtime:
        if output in stdout.readline():
            return True
        sleep(0.001)
    return False


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_cli(
    monkeypatch: pytest.MonkeyPatch,
    test_data_dir: Path,
    open_port: int,
) -> None:
    port = str(open_port)
    monkeypatch.delenv("BEANCOUNT_FILE", raising=False)
    args = ("fava", str(test_data_dir / "example.beancount"), "-p", port)
    with Popen(
        args,
        stdout=PIPE,
        stderr=STDOUT,
        universal_newlines=True,
    ) as process:
        assert process.stdout
        assert output_contains(process.stdout, "Starting Fava on")
        with Popen(
            args,
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
        ) as process2:
            process2.wait()
            process.terminate()
            assert process2.stdout
            assert "in use" in "".join(process2.stdout.readlines())
            assert process2.returncode > 0
