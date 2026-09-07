"""Course-style {key?default} template resolution for ADK 2.8."""

import re

_OPTIONAL = re.compile(
    r"\{((?:app|user|temp):[a-zA-Z_][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_]*)\?"
    r"((?:[^{}]|\{(?:app|user|temp):[a-zA-Z_][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_]*\})*)\}"
)


def resolve_course_template(template: str, state: dict) -> str:
    """Resolve {key?default} and {key?text {key}} patterns from course labs."""

    def optional(match: re.Match[str]) -> str:
        key, suffix = match.group(1), match.group(2)
        placeholder = f"{{{key}}}"
        if key in state and state[key] is not None:
            value = str(state[key])
            if placeholder in suffix:
                return suffix.replace(placeholder, value)
            return value
        if placeholder in suffix:
            return ""
        return suffix

    return _OPTIONAL.sub(optional, template)
