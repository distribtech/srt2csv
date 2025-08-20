import re
from pathlib import Path
from typing import List, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)

def check_vocabular(voice_dir):
    """Ensure a vocabulary file exists in ``voice_dir``.

    If the ``vocabular.txt`` file is missing, an empty file will be created so
    the pipeline can continue without manual intervention.  The path to the
    vocabulary file is always returned.
    """

    vocabular_pth = Path(voice_dir) / "vocabular.txt"
    if not vocabular_pth.is_file():
        print(f"Vocabulary file not found at {vocabular_pth}, creating default.")
        vocabular_pth.parent.mkdir(parents=True, exist_ok=True)
        vocabular_pth.write_text("", encoding="utf-8")
    else:
        print(f"Vocabulary file is {vocabular_pth}.")
    return vocabular_pth

def two_cases(title):
    if not title:
       return '',''
    return title[0].upper() + title[1:], title[0].lower() + title[1:]

def parse_vocabular_text(vocabular_text: str):
    """
    Parses vocabular text with lines like:
        Kiyv<=>Kiev
        Ekaterina II<=>Ekaterina druga

    Returns a list of tuples:
        [("Kiyv","Kiev"), ("Kiyv","kiev"), ("Ekaterina II","Ekaterina druga"), ("Ekaterina II","ekaterina druga")]
    """
    replacements = []
    for line in vocabular_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Expect a separator <=>
        if "<=>" in line:
            old, new = line.split("<=>", 1)
            new_upper, new_lower = two_cases(new.strip())
            old_strip = old.strip()
            replacements.append((old_strip, new_upper))
            replacements.append((old_strip, new_lower))

    # Sort by length of the old string, descending (longest first)
    replacements.sort(key=lambda x: len(x[0]), reverse=True)
    return replacements

def parse_vocabular_file(vocabular_path):
    """
    Parses a vocabular file with lines like:
        Kiyv<=>Kiev
        Ekaterina II<=>Ekaterina druga
    Returns a list of tuples [("Kiyv","Kiev"), ("Ekaterina II","Ekaterina druga")].
    """
    replacements = []
    with open(vocabular_path, 'r', encoding='utf-8') as file:
        replacements = parse_vocabular_text(file.read())
    return replacements


def apply_replacements(line, replacements, whole_words=True):
    """
    Applies replacements sequentially in the order given (longest first),
    with optional word boundary matching.
    """
    for old, new in replacements:
        if whole_words:
            pattern = fr'\b{re.escape(old)}\b'
            line = re.sub(pattern, new, line)
        else:
            line = line.replace(old, new)
    return line

def modify_subtitles_with_vocabular_text_only_optimized(subtitles: str, replacements: List[Tuple[str, str]]) -> str:
    """
    Optimized version that pre-compiles regex patterns and processes replacements more efficiently.
    """
    if not replacements:
        return subtitles

    # Pre-compile all regex patterns
    compiled_replacements = []
    for old, new in replacements:
        # Match word boundaries or punctuation after the word
        pattern = re.compile(rf'(?<![\w-])({re.escape(old)})(?![\w-])')
        compiled_replacements.append((pattern, new))
    
    result_lines = []
    lines = subtitles.splitlines()
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines, numeric lines, or timecodes
        if not line_stripped or line_stripped.isdigit() or "-->" in line_stripped:
            result_lines.append(line)
            continue

        # Apply all replacements to the line
        original_line = line
        new_line = line
        
        # Apply all patterns and collect changes
        changes = []
        for pattern, replacement in compiled_replacements:
            new_text = pattern.sub(replacement, new_line)
            if new_text != new_line:  # If this pattern made a change
                changes.append((pattern.pattern, replacement))
                new_line = new_text
        
        # Log if any changes were made
        if changes:
            logger.info(f"Original: {original_line.strip()}")
            logger.info(f"Modified: {new_line.strip()}")
            for pattern, repl in changes:
                logger.debug(f"Applied: {pattern} -> {repl}")
        
        result_lines.append(new_line)

    return '\n'.join(result_lines)


# def modify_subtitles_with_vocabular_text_only_to_file(subtitles:str, replacements:List[Tuple[str, str]], output_path:Path)->None:
#     text = modify_subtitles_with_vocabular_text_only(subtitles, replacements)
#     with open(output_path, 'w', encoding='utf-8') as outfile:
#         logger.info(f"Writing modified subtitles to {output_path}")
#         outfile.write(text)

# def modify_subtitles_with_vocabular_text_only(subtitles:str, replacements:List[Tuple[str, str]])->str:
#     """
#     Reads subtitles from `subtitle_path` and applies replacements
#     from `vocabular_path`. Returns the modified subtitle text as a string.
#     """
#     result_lines = []
#     lines = [line.strip() for line in subtitles.splitlines()]
#     for line in lines:
#             # Skip numeric lines or timecodes
#             if line.isdigit() or "-->" in line:
#                 result_lines.append(line)
#                 continue

#             # Apply replacements only to text lines
#             new_line = apply_replacements(line, replacements) if line != "" else "\n"
#             result_lines.append(new_line)
#             logger.debug(f"new_line: {new_line}")

#     return "".join(result_lines)