import sys
from pathlib import Path
from loguru import logger

log_dir = Path("logs")

if not log_dir.exists():
    log_dir.mkdir(parents=True)


# logger.add(
#     log_dir / "info.log",
#     format="{time:YYYY.MM.DD HH.mm.ss} | {level} | {file}:{function}:{line} | {message}",
#     level="INFO",
#     rotation="1 day",
#     serialize=False
# )

logger.add(
    log_dir / "error.log",
    format="{time:YYYY.MM.DD HH.mm.ss} | {level} | {file}:{function}:{line} | {message}",
    level="ERROR",
    rotation="1 day",
    backtrace=True,
    diagnose=True,
    serialize=False
)

logger.add(
    sys.stdout,
    format="{time:YYYY.MM.DD HH.mm.ss} | {level} | {file}:{function}:{line} | {message}",
    level="INFO",
    serialize=False
)

logger.add(
    sys.stdout,
    format="{time:YYYY.MM.DD HH.mm.ss} | {level} | {file}:{function}:{line} | {message}",
    level="ERROR",
    serialize=False
)

