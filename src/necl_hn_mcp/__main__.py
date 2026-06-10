"""Entry point — runs the MCP server over stdio."""

from .server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
