import argparse
import logging
from typing import List, Tuple
from pathlib import Path
import time
import subtitle_csv
import vocabulary
import random
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def with_lock(lock_suffix: str = ".lock", max_wait: float = 1.0):
    """
    Decorator to add lock-file logic around a function that processes a Path.
    Expects the first argument of the decorated function to be a Path (e.g., subtitle_path).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(subtitle_path: Path, *args, **kwargs):
            lock_file = subtitle_path.with_suffix(subtitle_path.suffix + lock_suffix)

            if lock_file.exists():
                logger.info(f"Lock file {lock_file} already exists")
                return None

            timeout = random.random() * max_wait
            time.sleep(timeout)

            if lock_file.exists():
                logger.info(f"Lock file {lock_file} appeared after waiting {timeout} seconds")
                return None

            try:
                lock_file.touch()
                logger.info(f"Lock file {lock_file} created")
                return func(subtitle_path, *args, **kwargs)
            finally:
                if lock_file.exists():
                    lock_file.unlink()
                    logger.info(f"Lock file {lock_file} removed")
        return wrapper
    return decorator

@with_lock()
def process_srt_file(subtitle_path: Path, vocabular_replacements: List[Tuple[str, str]], output_path: Path=None) -> None:
    if not output_path:
        output_path = subtitle_path.with_suffix('.csv')
    if output_path.exists() and output_path.is_file():
        logger.info(f"Output file {output_path} already exists")
        return output_path
    with open(subtitle_path, 'r', encoding='utf-8') as subtitle_file:
        subtitle_text = subtitle_file.read()
    if vocabular_replacements:
        subtitle_text = vocabulary.modify_subtitles_with_vocabular_text_only_optimized(subtitle_text, vocabular_replacements)
    result_text = subtitle_csv.srttext_to_csvfile(subtitle_text, output_path)
    logger.info(f"Wrote {output_path}")
    if logger.level <= logging.DEBUG:  # Only print text in DEBUG mode
        logger.debug(f"Generated CSV content for {output_path}:")
        logger.debug(result_text)
    return output_path        

def process_srt_folder(subtitle_path: Path, vocabular_replacements: List[Tuple[str, str]], output_path: Path) -> None:
    logger.info(f"Processing folder {subtitle_path}")
    for subtitle_file in subtitle_path.glob("**/*.srt"):
        logger.info(f"Processing file {subtitle_file}")
        process_srt_file(subtitle_file, vocabular_replacements, output_path)
    return output_path

def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--subtitle', '-s', type=Path, help="Path to the subtitle file(folder) to be processed")
    parser.add_argument('--vocabular','-v', type=Path, help="To change words in srt")
    parser.add_argument('--output', '-o', type=Path, help="Path to output csv")


    # Parse the arguments
    args = parser.parse_args()
    subtitle,vocabular,output = args.subtitle,args.vocabular,args.output

    if not subtitle.exists():
        raise FileNotFoundError(f"Subtitle file(s) {subtitle} does not exist")
    if vocabular:
        vocabular_replacements = vocabulary.parse_vocabular_file(vocabular)
    if subtitle.is_file():
        process_srt_file(subtitle, vocabular_replacements, output)
    elif subtitle.is_dir():
        process_srt_folder(subtitle, vocabular_replacements, output)
    else:
        raise ValueError(f"{subtitle} is neither a file nor a directory")
                        
    print(f"Argumets of module {args}")


if __name__ == "__main__":
    main()