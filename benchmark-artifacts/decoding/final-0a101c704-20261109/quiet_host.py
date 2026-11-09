#!/usr/bin/env python3
"""Opt-in local benchmark isolation; suspend only fff-mcp, then restore it.

Use --hold for a batch spanning multiple benchmark commands. Touch the printed
resume file when finished. A separate watchdog restores processes on timeout or
parent exit, including an unexpected parent termination. Never stops unrelated
processes or resumes processes that were already stopped.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def processes():
    rows = subprocess.check_output(
        ["ps", "-axo", "pid=,stat=,lstart=,comm="], text=True
    ).splitlines()
    result = {}
    for row in rows:
        fields = row.split(None, 7)
        if len(fields) == 8:
            result[int(fields[0])] = {
                "state": fields[1], "started": " ".join(fields[2:7]),
                "command": fields[7],
            }
    return result


def restore(state_path):
    state = json.loads(state_path.read_text())
    live = processes()
    restored = []
    errors = []
    for item in state["processes"]:
        current = live.get(item["pid"])
        if current and all(current[k] == item[k] for k in ("started", "command")):
            try:
                os.kill(item["pid"], signal.SIGCONT)
                restored.append(item["pid"])
            except ProcessLookupError:
                pass
            except OSError as error:
                # One inaccessible process must not prevent restoring others.
                errors.append({"pid": item["pid"], "error": str(error)})
    state["restored_pids"] = restored
    state["restored_at"] = time.time()
    state["restore_errors"] = errors
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(f"Resumed {len(restored)} recorded indexers.", flush=True)
    if errors:
        print(f"Restoration needs attention: {errors}", file=sys.stderr, flush=True)


def watch(path):
    state = json.loads(path.read_text())
    while time.time() < state["deadline"] and not Path(state["resume_file"]).exists():
        try:
            os.kill(state["parent_pid"], 0)
        except ProcessLookupError:
            break
        time.sleep(1)
    restore(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suspend-fff-mcp", action="store_true")
    parser.add_argument("--hold", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--watch", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.watch:
        watch(args.watch)
        return
    if not args.suspend_fff_mcp or not args.hold or not args.state or args.timeout <= 0:
        parser.error("require --suspend-fff-mcp --hold --state PATH and positive timeout")
    guard_lock = open("/tmp/swc-quiet-host.lock", "a")
    try:
        fcntl.flock(guard_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        parser.error("another quiet-host batch is already active")
    state_path = args.state.resolve()
    if state_path.exists():
        parser.error("choose a fresh state file")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    resume_file = state_path.with_suffix(".resume")
    if resume_file.exists():
        parser.error("choose a fresh resume-file path")
    selected = [{"pid": pid, **data} for pid, data in processes().items()
                if Path(data["command"]).name == "fff-mcp" and "T" not in data["state"]]
    state = {"parent_pid": os.getpid(), "deadline": time.time() + args.timeout,
             "resume_file": str(resume_file), "processes": selected}
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    # Start recovery before the first stop signal, so partial setup is recoverable.
    watcher = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                "--watch", str(state_path)], start_new_session=True)
    def finish(signum=None, frame=None):
        raise SystemExit(128 + (signum or 0))
    signal.signal(signal.SIGTERM, finish)
    signal.signal(signal.SIGINT, finish)
    try:
        live = processes()
        stopped = []
        for item in selected:
            if watcher.poll() is not None or time.time() >= state["deadline"]:
                break
            current = live.get(item["pid"])
            if current and all(current[k] == item[k] for k in ("started", "command")):
                try:
                    os.kill(item["pid"], signal.SIGSTOP)
                    stopped.append(item["pid"])
                except ProcessLookupError:
                    pass
        print(f"Suspended {len(stopped)} indexers; touch {resume_file} to resume.", flush=True)
        while watcher.poll() is None:
            time.sleep(1)
    finally:
        resume_file.touch()
        try:
            watcher.wait(timeout=15)
        finally:
            # Also recover if the watchdog exited early during partial setup.
            restore(state_path)


if __name__ == "__main__":
    main()
