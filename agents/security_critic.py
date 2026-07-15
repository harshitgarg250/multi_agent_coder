# agents/security_critic.py
# Security Critic Agent - static analysis pass that scans generated code
# for common security anti-patterns BEFORE it is shown to the user.
#
# Deliberately NOT LLM-based: this is a deterministic rule-engine (regex +
# AST checks), which makes it fast, free (no extra API call), and
# reliable/repeatable — the kind of defense-in-depth check a real
# fintech/production codebase would run in CI.

import ast
import re
from dataclasses import dataclass, field


@dataclass
class SecurityFinding:
    severity: str      # "HIGH" | "MEDIUM" | "LOW"
    rule: str           # short rule id, e.g. "hardcoded-secret"
    message: str
    line: int | None = None


@dataclass
class SecurityReport:
    findings: list[SecurityFinding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(f.severity == "HIGH" for f in self.findings)

    def summary(self) -> str:
        if not self.findings:
            return "No security issues detected."
        lines = []
        for f in self.findings:
            loc = f" (line {f.line})" if f.line else ""
            lines.append(f"[{f.severity}] {f.rule}{loc}: {f.message}")
        return "\n".join(lines)


# --- Regex-based checks (fast, catch textual patterns) ---------------------

_SECRET_PATTERNS = [
    re.compile(r"""(?i)(api[_-]?key|secret|password|token|access[_-]?key)\s*=\s*['"][A-Za-z0-9_\-/+=]{8,}['"]"""),
    re.compile(r"""(?i)gsk_[A-Za-z0-9]{20,}"""),   # Groq-style key
    re.compile(r"""(?i)sk-[A-Za-z0-9]{20,}"""),    # OpenAI-style key
    re.compile(r"""(?i)AKIA[0-9A-Z]{16}"""),       # AWS access key
]

_SHELL_TRUE = re.compile(r"subprocess\.\w+\([^)]*shell\s*=\s*True")


class SecurityCriticAgent:
    """Runs static security checks on a piece of generated code."""

    def scan(self, code: str) -> SecurityReport:
        report = SecurityReport()

        self._check_hardcoded_secrets(code, report)
        self._check_shell_true(code, report)
        self._check_ast_rules(code, report)

        return report

    # -- individual rules ---------------------------------------------------

    def _check_hardcoded_secrets(self, code: str, report: SecurityReport):
        for lineno, line in enumerate(code.splitlines(), start=1):
            for pattern in _SECRET_PATTERNS:
                if pattern.search(line):
                    report.findings.append(SecurityFinding(
                        severity="HIGH",
                        rule="hardcoded-secret",
                        message="Possible hardcoded API key/secret/password in source code.",
                        line=lineno,
                    ))
                    break  # one flag per line is enough

    def _check_shell_true(self, code: str, report: SecurityReport):
        for lineno, line in enumerate(code.splitlines(), start=1):
            if _SHELL_TRUE.search(line):
                report.findings.append(SecurityFinding(
                    severity="HIGH",
                    rule="shell-injection-risk",
                    message="subprocess call with shell=True can enable shell injection.",
                    line=lineno,
                ))

    def _check_ast_rules(self, code: str, report: SecurityReport):
        """Use the AST so we don't false-positive on eval/exec inside strings/comments."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            report.findings.append(SecurityFinding(
                severity="MEDIUM",
                rule="syntax-error",
                message="Code could not be parsed for security analysis (syntax error).",
            ))
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._call_name(node)

                if func_name in ("eval", "exec"):
                    report.findings.append(SecurityFinding(
                        severity="HIGH",
                        rule="dangerous-builtin",
                        message=f"Use of `{func_name}()` allows arbitrary code execution.",
                        line=getattr(node, "lineno", None),
                    ))

                if func_name == "pickle.loads" or func_name == "loads" and self._imported_from(tree, "pickle"):
                    report.findings.append(SecurityFinding(
                        severity="MEDIUM",
                        rule="unsafe-deserialization",
                        message="pickle.loads() on untrusted input can execute arbitrary code.",
                        line=getattr(node, "lineno", None),
                    ))

                if func_name == "os.system":
                    report.findings.append(SecurityFinding(
                        severity="MEDIUM",
                        rule="os-system-call",
                        message="os.system() is unsafe with unsanitized input; prefer subprocess with a list of args.",
                        line=getattr(node, "lineno", None),
                    ))

            # SQL string concatenation / f-strings used directly in execute()
            if isinstance(node, ast.Call):
                call_name = self._call_name(node)
                if call_name == "execute" or call_name.endswith((".execute", ".executemany")):
                    for arg in node.args:
                        if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                            report.findings.append(SecurityFinding(
                                severity="HIGH",
                                rule="sql-injection-risk",
                                message="SQL query built with string formatting/concatenation instead of parameterized query.",
                                line=getattr(node, "lineno", None),
                            ))

    @staticmethod
    def _call_name(node: ast.Call) -> str:
        f = node.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            parts = []
            cur = f
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _imported_from(tree: ast.Module, module: str) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == module for alias in node.names):
                    return True
            if isinstance(node, ast.ImportFrom) and node.module == module:
                return True
        return False
