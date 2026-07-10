SUMMARIZE_PROMPT_TEMPLATE = """
You are Akashic, an expert developer assistant.
Generate a structured, clean technical markdown documentation for the following service information.
Focus on dependencies, APIs, events, and a general description.

Service Name: {name}
Description: {description}
Dependencies: {depends_on}
APIs: {apis}
Events Emitted: {emits_events}
Events Consumed: {consumes_events}
"""
