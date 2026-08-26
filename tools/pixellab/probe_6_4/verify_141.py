#!/usr/bin/env python3
"""Does run_controls.py really exit 0 on an aborted run? Checked, not reasoned about.

Filed as #141 on the strength of an observed "[exited with code 0]" beside an
`ABORT: capture failed` line. That observation came from a command that ended in `| tail -70`,
and a shell pipeline reports the exit status of its LAST command, not the first — so the 0 may
have been tail's all along.

This forces the abort path with an unusable engine binary and reads the status directly, with
no pipe anywhere near it.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

DRIVER = '''
import sys, os
sys.path.insert(0, os.path.join(%r, "tools/tier0_harness"))
import run_controls as rc
rc.GODOT = "/nonexistent/godot-that-cannot-run"      # force shoot() down its abort path
try:
    rc.main()
except SystemExit as e:
    print("SystemExit code:", e.code)
    raise
''' % REPO


def main():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(DRIVER)
        path = f.name
    try:
        # No pipe. capture_output keeps the child's streams off this process's stdout without
        # putting another process between us and its exit status.
        p = subprocess.run([sys.executable, path, "--only", "determinism"],
                           capture_output=True, text=True, cwd=REPO, timeout=900)
        tail = (p.stdout + p.stderr).strip().splitlines()
        print("--- last lines of the aborted run ---")
        for line in tail[-6:]:
            print("   " + line)
        print("\nrun_controls.py exit status on abort: %d" % p.returncode)
        print("VERDICT: %s" % (
            "#141 is REAL — an aborted run reports success."
            if p.returncode == 0 else
            "#141 IS NOT REAL — the script exits %d on abort. The 0 that was reported came "
            "from the `| tail` in the observing command, not from this script." % p.returncode))

        # And the claim that produced the false report, demonstrated on its own.
        piped = subprocess.run("exit 3 | tail -1", shell=True)
        print("\ncontrol: `exit 3 | tail -1` reports %d — a pipeline reports its LAST command."
              % piped.returncode)
        return 0
    finally:
        os.unlink(path)


if __name__ == "__main__":
    sys.exit(main())
