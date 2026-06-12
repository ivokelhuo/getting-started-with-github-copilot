"""Simple console app that prints Hello World."""

import logging


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Hello World")


if __name__ == "__main__":
    main()
