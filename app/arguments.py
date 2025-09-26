import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Обработка конфигурации приложения.")
    parser.add_argument(
        "--config", "-c", type=str, help="файл конфигурации", default="config.toml"
    )
    return parser.parse_args()
