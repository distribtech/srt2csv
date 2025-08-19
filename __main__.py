import argparse
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description="Process some integers.")

    parser.add_argument('--subtitle', '-s', type=Path, help="Path to the subtitle file to be processed")
    parser.add_argument('--vocabular','-v', type=Path, help="To change words in srt")
    # Parse the arguments
    args = parser.parse_args()
    subtitle = args.subtitle
                        
    print(f"Argumets of module {args}")


if __name__ == "__main__":
    main()