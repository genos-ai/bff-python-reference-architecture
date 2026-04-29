#!/usr/bin/env python3
"""
BFF Web Skeleton Service Manager

Manage all development services from one script.

Usage:
    python services.py start                  # Start everything
    python services.py start --backend-only   # Backend only
    python services.py start --no-migrate     # Skip migrations
    python services.py stop                   # Stop backend + frontend
    python services.py stop --backend-only    # Stop backend only
    python services.py restart                # Stop then start
    python services.py status                 # Show what's running
    python services.py check                  # Preflight checks only
"""

import argparse
import asyncio
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

BACKEND_PORT = 8000
FRONTEND_PORT = 5173


# ---------------------------------------------------------------------------
# Port utilities
# ---------------------------------------------------------------------------


def get_pids_on_port(port: int) -> list[int]:
    """Return PIDs listening on a port."""
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-t"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(p) for p in result.stdout.strip().split("\n") if p.isdigit()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def kill_pids(pids: list[int], label: str) -> int:
    """Terminate a list of PIDs gracefully, force-kill after timeout."""
    if not pids:
        return 0

    killed = 0
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            killed += 1
        except ProcessLookupError:
            pass
        except PermissionError:
            print(f"  Permission denied killing PID {pid}")

    if killed:
        print(
            f"  {label}: sent SIGTERM to {killed} process(es)"
            f" (PID {', '.join(str(p) for p in pids)})"
        )

        deadline = time.time() + 5
        alive = list(pids)
        while time.time() < deadline:
            alive = []
            for pid in pids:
                try:
                    os.kill(pid, 0)
                    alive.append(pid)
                except ProcessLookupError:
                    pass
            if not alive:
                break
            time.sleep(0.5)
        else:
            for pid in alive:
                try:
                    os.kill(pid, signal.SIGKILL)
                    print(f"  Force-killed PID {pid}")
                except (ProcessLookupError, PermissionError):
                    pass

    return killed


def stop_port(port: int, label: str) -> int:
    """Kill all processes on a port, retrying to catch respawned children."""
    total = 0
    for _ in range(3):
        pids = get_pids_on_port(port)
        if not pids:
            break
        total += kill_pids(pids, label)
        time.sleep(1)
    return total


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_redis() -> bool:
    """Check Redis connectivity."""
    try:
        from redis import Redis

        r = Redis(host="localhost", port=6379, socket_connect_timeout=2)
        r.ping()
        r.close()
        print("  Redis ............. OK")
        return True
    except Exception as e:
        print(f"  Redis ............. FAIL ({e})")
        print("    Start Redis: brew services start redis" "  OR  redis-server --daemonize yes")
        return False


def check_postgres() -> bool:
    """Check PostgreSQL connectivity using config from database.yaml."""
    try:
        from modules.backend.core.config import get_app_config, get_settings

        db_cfg = get_app_config().database
        db_password = get_settings().db_password

        async def _check():
            import asyncpg

            conn = await asyncpg.connect(
                host=db_cfg.host,
                port=db_cfg.port,
                user=db_cfg.user,
                password=db_password,
                database=db_cfg.name,
                timeout=3,
            )
            await conn.close()

        asyncio.run(_check())
        print(f"  PostgreSQL ........ OK" f" ({db_cfg.host}:{db_cfg.port}/{db_cfg.name})")
        return True
    except Exception as e:
        print(f"  PostgreSQL ........ FAIL ({e})")
        return False


def check_port_free(port: int) -> bool:
    """Check if a port is free."""
    pids = get_pids_on_port(port)
    if pids:
        print(f"  Port {port} ........... IN USE" f" (PID {', '.join(str(p) for p in pids)})")
        return False
    print(f"  Port {port} ........... free")
    return True


def preflight(backend_port: int, check_frontend: bool = True) -> bool:
    """Run all preflight checks. Returns True if all pass."""
    print("\nPreflight checks...")
    redis_ok = check_redis()
    pg_ok = check_postgres()
    port_ok = check_port_free(backend_port)
    if check_frontend:
        check_port_free(FRONTEND_PORT)

    if not (redis_ok and pg_ok):
        print("\nRequired services are not running." " Fix the issues above and retry.")
        return False
    if not port_ok:
        print(
            f"\nPort {backend_port} is in use."
            " Run 'python services.py stop' first or use --port <other>."
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Migrations
# ---------------------------------------------------------------------------


def run_migrations() -> bool:
    """Run alembic upgrade head."""
    print("\nRunning migrations...")
    result = subprocess.run(
        [sys.executable, "run.py", "--service", "migrate", "--migrate-action", "upgrade"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if result.returncode == 0:
        print("  Migrations ........ OK")
        return True
    else:
        stderr = result.stderr.strip() or result.stdout.strip()
        print(f"  Migrations ........ FAIL\n    {stderr[:200]}")
        return False


# ---------------------------------------------------------------------------
# Process management
# ---------------------------------------------------------------------------


class DevRunner:
    """Manages backend and frontend subprocesses."""

    def __init__(self):
        self.procs: list[subprocess.Popen] = []
        self._shutting_down = False

    def start_backend(self, host: str, port: int, reload: bool) -> subprocess.Popen:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "modules.backend.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]
        if reload:
            cmd.append("--reload")

        proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
        self.procs.append(proc)
        return proc

    def start_worker(self) -> subprocess.Popen:
        cmd = [
            sys.executable,
            "-m",
            "taskiq",
            "worker",
            "modules.backend.tasks.broker:broker",
            "modules.backend.tasks.cleanup",
            "--workers",
            "1",
        ]
        proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
        self.procs.append(proc)
        return proc

    def start_frontend(self) -> subprocess.Popen:
        frontend_dir = PROJECT_ROOT / "modules" / "frontend"
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
        )
        self.procs.append(proc)
        return proc

    def shutdown(self, signum=None, frame=None):
        if self._shutting_down:
            return
        self._shutting_down = True
        print("\n\nShutting down...")

        for proc in self.procs:
            if proc.poll() is None:
                proc.terminate()

        deadline = time.time() + 5
        for proc in self.procs:
            remaining = max(0.1, deadline - time.time())
            try:
                proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

        print("All services stopped.")

    def wait(self):
        """Block until any child exits or Ctrl-C."""
        try:
            while True:
                for proc in self.procs:
                    ret = proc.poll()
                    if ret is not None:
                        name = (
                            " ".join(proc.args[:4])
                            if isinstance(proc.args, list)
                            else str(proc.args)
                        )
                        print(f"\nProcess exited (code {ret}): {name}")
                        self.shutdown()
                        return ret
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.shutdown()
            return 0


# ===========================================================================
# Commands
# ===========================================================================


def cmd_start(args):
    """Start development services."""
    print("=" * 50)
    print("  BFF WEB SKELETON — Start")
    print("=" * 50)

    if not preflight(args.port, check_frontend=not args.backend_only):
        sys.exit(1)

    if not args.no_migrate:
        if not run_migrations():
            print("Migration failed." " Fix the issue or use --no-migrate to skip.")
            sys.exit(1)
    else:
        print("\n  Migrations ........ skipped")

    runner = DevRunner()
    signal.signal(signal.SIGINT, runner.shutdown)
    signal.signal(signal.SIGTERM, runner.shutdown)

    print(f"\nStarting backend at http://localhost:{args.port} ...")
    runner.start_backend(args.host, args.port, not args.no_reload)

    print("Starting task worker ...")
    runner.start_worker()

    if not args.backend_only:
        print(f"Starting frontend at http://localhost:{FRONTEND_PORT} ...")
        runner.start_frontend()

    print("\n" + "-" * 50)
    print(f"  Backend API:  http://localhost:{args.port}")
    print(f"  Swagger UI:   http://localhost:{args.port}/docs")
    print("  Task Worker:  1 worker")
    if not args.backend_only:
        print(f"  Frontend:     http://localhost:{FRONTEND_PORT}")
    print("-" * 50)
    print("Press Ctrl+C to stop all services\n")

    sys.exit(runner.wait())


def cmd_stop(args):
    """Stop running development services."""
    print("=" * 50)
    print("  BFF WEB SKELETON — Stop")
    print("=" * 50)

    total = 0
    total += stop_port(args.port, f"Backend (:{args.port})")

    if not args.backend_only:
        total += stop_port(FRONTEND_PORT, f"Frontend (:{FRONTEND_PORT})")

    if total == 0:
        print("\n  No services running.")
    else:
        remaining = get_pids_on_port(args.port) + (
            [] if args.backend_only else get_pids_on_port(FRONTEND_PORT)
        )
        if remaining:
            print(
                f"\n  Warning: {len(remaining)} process(es) still running."
                " Try again or kill manually."
            )
        else:
            print(f"\n  Stopped {total} process(es).")


def cmd_restart(args):
    """Stop then start services."""
    cmd_stop(args)
    time.sleep(2)
    print()
    cmd_start(args)


def _probe_redis() -> bool:
    """Quick Redis ping for status display."""
    try:
        from redis import Redis

        r = Redis(host="localhost", port=6379, socket_connect_timeout=1)
        r.ping()
        r.close()
        return True
    except (ConnectionError, OSError, ImportError):
        return False


def _probe_postgres() -> bool:
    """Quick PostgreSQL ping for status display."""
    try:
        from modules.backend.core.config import get_app_config, get_settings

        db_cfg = get_app_config().database

        async def _pg():
            import asyncpg

            conn = await asyncpg.connect(
                host=db_cfg.host,
                port=db_cfg.port,
                user=db_cfg.user,
                password=get_settings().db_password,
                database=db_cfg.name,
                timeout=2,
            )
            await conn.close()

        asyncio.run(_pg())
        return True
    except (ConnectionError, OSError, ImportError):
        return False


def cmd_status(args):
    """Show which services are running."""
    print("=" * 50)
    print("  BFF WEB SKELETON — Status")
    print("=" * 50)

    backend_pids = get_pids_on_port(args.port)
    if backend_pids:
        print(
            f"\n  Backend (:{args.port})  .... RUNNING"
            f" (PID {', '.join(str(p) for p in backend_pids)})"
        )
    else:
        print(f"\n  Backend (:{args.port})  .... stopped")

    frontend_pids = get_pids_on_port(FRONTEND_PORT)
    if frontend_pids:
        print(
            f"  Frontend (:{FRONTEND_PORT}) ... RUNNING"
            f" (PID {', '.join(str(p) for p in frontend_pids)})"
        )
    else:
        print(f"  Frontend (:{FRONTEND_PORT}) ... stopped")

    redis_ok = _probe_redis()
    print(f"  Redis ............. {'RUNNING' if redis_ok else 'stopped'}")

    pg_ok = _probe_postgres()
    print(f"  PostgreSQL ........ {'RUNNING' if pg_ok else 'stopped'}")
    print()


def cmd_check(args):
    """Run preflight checks only."""
    print("=" * 50)
    print("  BFF WEB SKELETON — Check")
    print("=" * 50)

    if preflight(args.port):
        print("\nAll checks passed.")
    else:
        sys.exit(1)


# ===========================================================================
# CLI
# ===========================================================================


def main():
    parser = argparse.ArgumentParser(
        description="BFF Web Skeleton service manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python services.py start                  Start all services
  python services.py start --backend-only   Backend only (no frontend)
  python services.py start --no-migrate     Skip DB migrations
  python services.py stop                   Stop all services
  python services.py restart                Restart everything
  python services.py status                 Show what's running
  python services.py check                  Run preflight checks
        """,
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=BACKEND_PORT,
        help=f"Backend port (default: {BACKEND_PORT})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # -- start --
    p_start = subparsers.add_parser("start", help="Start development services")
    p_start.add_argument("--host", default="0.0.0.0", help="Backend host (default: 0.0.0.0)")
    p_start.add_argument("--no-reload", action="store_true", help="Disable backend auto-reload")
    p_start.add_argument("--backend-only", action="store_true", help="Skip frontend dev server")
    p_start.add_argument("--no-migrate", action="store_true", help="Skip database migrations")

    # -- stop --
    p_stop = subparsers.add_parser("stop", help="Stop running services")
    p_stop.add_argument("--backend-only", action="store_true", help="Stop backend only")

    # -- restart --
    p_restart = subparsers.add_parser("restart", help="Restart services (stop + start)")
    p_restart.add_argument("--host", default="0.0.0.0", help="Backend host")
    p_restart.add_argument("--no-reload", action="store_true", help="Disable backend auto-reload")
    p_restart.add_argument("--backend-only", action="store_true", help="Backend only")
    p_restart.add_argument("--no-migrate", action="store_true", help="Skip migrations")

    # -- status --
    subparsers.add_parser("status", help="Show service status")

    # -- check --
    subparsers.add_parser("check", help="Run preflight checks only")

    args = parser.parse_args()

    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "restart": cmd_restart,
        "status": cmd_status,
        "check": cmd_check,
    }

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands[args.command](args)


if __name__ == "__main__":
    main()
