"""
TKinter Designer command-line interface.
"""

import os
import json
import shutil
import logging
import argparse
from tkdesigner.constants import ASSETS_PATH
from tkdesigner.parse import FigmaParser

from tkdesigner import figma_api

from pathlib import Path


if int(os.getenv("TKDESIGNER_VERBOSE", 0)) == 1:
    log_level = logging.INFO
else:
    log_level = logging.WARN

logging.basicConfig(level=log_level)


# def create_dirs(output_path, asset_path):
#     os.mkdir(output_path)
#     os.mkdir(asset_path)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate TKinter GUI code from Figma design.")
    parser.add_argument("file_url", type=str, help="File url of the Figma design.")
    parser.add_argument("token", type=str, help="Figma token.")
    parser.add_argument("-o", "--output", type=str, default="build/", help="Folder to output code and image assets to. Defaults to build/.")
    parser.add_argument("-f", "--force", action="store_true", help="If this flag is passed in, the output directory given will be overwritten if it exists.")
    args = parser.parse_args()

    logging.basicConfig()

    logging.info(f"args: {args}")

    output_path = Path(args.output)
    assets_path = output_path / ASSETS_PATH

    output_path.mkdir(exist_ok=True)
    assets_path.mkdir(exist_ok=True)


    # Create the output and output/assets directory
    asset_path = os.path.join(args.output, ASSETS_PATH)
    try:
        create_dirs(args.output, asset_path)
    except FileExistsError as e:
        logging.info(f"{args.output} or {asset_path} already exists")
        if args.force:
            logging.info(f"Overwritting exisiting output directory")
            shutil.rmtree(args.output)
            create_dirs(args.output, asset_path)
    except PermissionError as e:
        print("An error occurred creating output directories.")
        raise e

    figma_data, figma_file_id = figma_api.get_file_and_id(args.token, args.file_url)

    with open(os.path.join(args.output, "figma_data.json"), "w") as f:
        json.dump(figma_data, f)

    parser = FigmaParser(args.token, figma_file_id, args.output)
    gui = parser.parse_gui(figma_data)
    generated_code = gui.to_code()

    with open(os.path.join(args.output, "gui.py"), "w") as f:
        f.write(generated_code)


if __name__ == "__main__":
    main()
