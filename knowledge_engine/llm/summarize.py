from knowledge_engine.models.service import Service

def summarize(service: Service) -> str:
    """
    Stub renderer that deterministically formats the Service IR model into a Markdown body.
    """
    lines = []
    lines.append(f"# {service.name}")
    lines.append("")
    lines.append("## Overview")
    lines.append(service.description or "No description provided.")
    lines.append("")
    
    lines.append("## Dependencies")
    if service.depends_on:
        for dep in service.depends_on:
            lines.append(f"- {dep}")
    else:
        lines.append("None")
    lines.append("")

    lines.append("## APIs")
    if service.apis:
        lines.append("| Name | Method | Path | Description |")
        lines.append("| --- | --- | --- | --- |")
        for api in service.apis:
            lines.append(f"| {api.name} | {api.method} | {api.path} | {api.description} |")
    else:
        lines.append("No APIs defined.")
    lines.append("")

    lines.append("## Events")
    lines.append("### Emitted Events")
    if service.emits_events:
        for event in service.emits_events:
            lines.append(f"- **{event.name}**: {event.description}")
    else:
        lines.append("None")
    lines.append("")

    lines.append("### Consumed Events")
    if service.consumes_events:
        for event in service.consumes_events:
            lines.append(f"- **{event.name}**: {event.description}")
    else:
        lines.append("None")
    lines.append("")

    return "\n".join(lines)
