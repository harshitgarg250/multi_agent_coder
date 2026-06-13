# agents/tester.py
# Tester Agent: run generated code as a Python script

import subprocess
import tempfile
import textwrap
from pathlib import Path


class TesterAgent:
    def __init__(self, python_exec: str = "python3"):
        self.python_exec = python_exec

    def clean_code(self, code: str) -> str:
        code = code.strip()
        if code.startswith("```"):
            lines = code.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        return textwrap.dedent(code).strip()

    def run_code(self, code: str) -> tuple[bool, str]:
        """
        code: full Python script as string
        return: (success: bool, output: str)
        """
        code = self.clean_code(code)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "temp_script.py"
            tmp_path.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    [self.python_exec, str(tmp_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except subprocess.TimeoutExpired:
                return False, "Error: Code execution timed out."

            output = ""
            if result.stdout:
                output += "STDOUT:\n" + result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr

            success = result.returncode == 0
            return success, output.strip()