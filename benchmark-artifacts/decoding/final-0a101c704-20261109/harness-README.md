# Quiet-host benchmark batches

Temporarily suspend the local `fff-mcp` indexers before running performance
benchmarks. This is opt-in and specific to this machine; it is not part of SWC's
production runtime or required upstream test tooling.

Start a guarded batch using a fresh state filename:

```sh
python3 quiet_host.py --suspend-fff-mcp --hold --timeout 1800 \
  --state /tmp/swc-quiet-host-batch.json
```

Run benchmarks from another terminal, serializing heavy work through the existing
benchmark lock. Record power, instantaneous CPU activity, memory pressure, and
swap activity before and during measurements. A high historical load average can
persist after indexing stops; inspect current activity too. Suspension does not
free the indexers' memory, clear filesystem caches, or guarantee an idle disk.

Finish the batch by touching the resume path printed by the helper:

```sh
touch /tmp/swc-quiet-host-batch.resume
```

The helper records PID, start time, and executable path, then uses `SIGSTOP` only
on processes named exactly `fff-mcp` that were not already stopped. It restores
those same process identities using `SIGCONT`. Exited processes are skipped.
A separate watchdog restores them on timeout or parent termination, including
unexpected parent exit. Normal interruption also requests restoration. Only one
guarded batch may run at a time. Never extend a benchmark beyond the guard's
deadline without ending that batch and deliberately starting another.

The initial live validation suspended and automatically restored all 19 selected
indexers after a three-second timeout. Keep measurements from contended runs
separate; do not pool them with a quiet-host confirmation.
