# app/export_swagger.py
"""
OpenAPI schema export script.
Generates an ``openapi.yaml`` file from the application's OpenAPI schema
and writes it to the project root.

Usage
-----
Run from the project root after all routes and schemas are defined:

    python -m app.export_swagger
"""
import yaml
from . import create_app


def export_swagger() -> None:
    """
    Serialize the application's OpenAPI schema to ``openapi.yaml``.

    Instantiates the FastAPI application, extracts its generated OpenAPI
    schema, and writes it as a YAML file to the current working directory.
    Unicode characters are preserved as-is and block style is used for
    human-readable output.
    """
    
    with open("openapi.yaml", "w", encoding="utf-8") as f:
        yaml.dump(create_app().openapi(), f, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    export_swagger()