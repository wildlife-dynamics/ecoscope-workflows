dependencies = {
    "jinja2": "*",
    "pandera": "*",
    "pydantic": "<2.9.0",
    "pydantic-settings": "*",
    "ruamel.yaml": "*",
    "ruff": "*",
    "tomli-w": "*",
}
features = [
    {
        "dependencies": {
            "ecoscope": {
                "version": "v1.8.3",
                "channel": "https://prefix.dev/ecoscope-workflows",
            }
        }
    }
]
