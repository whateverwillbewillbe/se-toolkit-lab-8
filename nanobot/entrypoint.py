"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then launches nanobot gateway.
"""

import json
import os
import sys
from pathlib import Path


def resolve_config() -> str:
    """Load config.json, inject env vars, write resolved config."""
    config_path = Path(__file__).parent / "config.json"
    config = json.loads(config_path.read_text())

    # Resolve LLM provider config from env vars
    if "LLM_API_KEY" in os.environ:
        config["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    if "LLM_API_BASE_URL" in os.environ:
        config["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]

    # Resolve gateway config
    if "NANOBOT_GATEWAY_CONTAINER_ADDRESS" in os.environ:
        config["gateway"]["host"] = os.environ["NANOBOT_GATEWAY_CONTAINER_ADDRESS"]
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config["gateway"]["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])

    # Resolve webchat channel config
    if "NANOBOT_WEBCHAT_CONTAINER_PORT" in os.environ:
        # The webchat channel listens on this port
        pass  # Channel port is configured in channels.webchat if needed

    # Resolve MCP server env vars
    if "tools" in config and "mcpServers" in config["tools"]:
        for server_name, server_config in config["tools"]["mcpServers"].items():
            if "env" in server_config:
                if "NANOBOT_LMS_BACKEND_URL" in os.environ:
                    server_config["env"]["NANOBOT_LMS_BACKEND_URL"] = os.environ[
                        "NANOBOT_LMS_BACKEND_URL"
                    ]
                if "NANOBOT_LMS_API_KEY" in os.environ:
                    server_config["env"]["NANOBOT_LMS_API_KEY"] = os.environ[
                        "NANOBOT_LMS_API_KEY"
                    ]

    # Write resolved config to a temp file
    resolved_path = Path(__file__).parent / "config.resolved.json"
    resolved_path.write_text(json.dumps(config, indent=2))
    return str(resolved_path)


def main() -> None:
    """Resolve config and launch nanobot gateway."""
    resolved_config = resolve_config()
    workspace = str(Path(__file__).parent / "workspace")

    # Launch nanobot gateway
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            resolved_config,
            "--workspace",
            workspace,
        ],
    )


if __name__ == "__main__":
    main()
