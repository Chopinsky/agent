"""Centralized logging configuration for the application."""
import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for scripts and the web app.

    Call this early (before modules import) to ensure a consistent logging
    configuration across the project.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


__all__ = ["configure_logging"]
