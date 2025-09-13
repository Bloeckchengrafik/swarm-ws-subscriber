import tomllib
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration loader for the WebSocket subscriber application."""

    def __init__(self, config_path: str = "config.toml"):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to the TOML configuration file
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "rb") as f:
            return tomllib.load(f)

    @property
    def server_host(self) -> str:
        """Get server host."""
        return self._config["server"]["host"]

    @property
    def server_port(self) -> int:
        """Get server port."""
        return self._config["server"]["port"]

    @property
    def serial_port(self) -> str:
        """Get serial connection port."""
        return self._config["connection"]["serial"]

    @property
    def subscribers(self) -> Dict[str, str]:
        """Get all subscribers mapping."""
        return self._config["subscribers"]

    def get_subscriber(self, alias: str) -> str:
        """
        Get subscriber by alias.

        Args:
            alias: The web alias for the subscriber

        Returns:
            The subscriber identifier

        Raises:
            KeyError: If alias not found
        """
        return self._config["subscribers"][alias]

    def get_all_config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self._config

    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_config()


# Convenience function to get a configured instance
def load_config(config_path: str = "config.toml") -> Config:
    """
    Load configuration from file.

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Configured Config instance
    """
    return Config(config_path)


# Example usage
if __name__ == "__main__":
    config = load_config()

    print(f"Server: {config.server_host}:{config.server_port}")
    print(f"Serial port: {config.serial_port}")
    print(f"Subscribers: {config.subscribers}")

    # Access specific subscriber
    try:
        subscriber1 = config.get_subscriber("webalias1")
        print(f"webalias1 maps to: {subscriber1}")
    except KeyError as e:
        print(f"Subscriber not found: {e}")
