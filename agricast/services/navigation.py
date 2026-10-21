"""Navigation label normalization shared by UI and regression tests."""
PAGE_OPTIONS = ["Home", "Farm data", "Farm overview", "Yield forecasting", "Climate analysis",
                "Agronomy guidance", "Knowledge assistant", "Model quality", "Integrations"]
PAGE_MAP = {
    "Home": "Command overview", "Farm data": "Data configuration", "Farm overview": "Farm overview",
    "Yield forecasting": "Yield forecast", "Climate analysis": "Climate signals",
    "Agronomy guidance": "Evidence search", "Knowledge assistant": "Knowledge assistant",
    "Model quality": "Model diagnostics", "Integrations": "Tool integrations",
}
ALIASES = {
    "Climate & weather": "Climate analysis", "Climate and weather": "Climate analysis",
    "Yield forecast": "Yield forecasting", "Agronomy library": "Agronomy guidance",
    "Find guidance": "Agronomy guidance", "Data configuration": "Farm data",
    "Command overview": "Home", "Climate signals": "Climate analysis",
    "Evidence search": "Agronomy guidance", "Model diagnostics": "Model quality",
    "Tool integrations": "Integrations",
}

def resolve_navigation_target(target):
    """Return a valid radio option for current and legacy labels, or None."""
    if target in PAGE_OPTIONS:
        return target
    return ALIASES.get(target)
