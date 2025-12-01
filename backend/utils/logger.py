"""
Centralized logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str | None = None, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.

    Args:
        name: Logger name
        log_file: Optional path to log file (ignored in serverless environments)
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (always available)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (only in writable environments)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            # Serverless environments are read-only, skip file logging
            logger.info(f"File logging disabled for {name} (read-only filesystem)")

    return logger


# Application-wide loggers (console-only in serverless environments)
try:
    app_logger = setup_logger("entrepedia_app", "logs/app.log")
    scraper_logger = setup_logger("scraper", "logs/scraper.log")
    processor_logger = setup_logger("processor", "logs/processor.log")
    agent_logger = setup_logger("agent", "logs/agent.log")
except Exception:
    # Fallback to console-only loggers
    app_logger = setup_logger("entrepedia_app")
    scraper_logger = setup_logger("scraper")
    processor_logger = setup_logger("processor")
    agent_logger = setup_logger("agent")