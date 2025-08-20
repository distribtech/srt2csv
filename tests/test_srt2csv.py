import os
import csv
from pathlib import Path
import pytest
from srt2csv import subtitle_csv, vocabulary

# Test data paths
TEST_DIR = Path(__file__).parent / "test_data"

# Fixture for test files
@pytest.fixture(params=[
    "test_0.srt",
    "test_1.srt",
    "test_2_multi.srt"
])
def test_srt_file(request):
    return TEST_DIR / request.param

# Test SRT to CSV conversion
def test_srt_to_csv_conversion(test_srt_file, tmp_path):
    # Get expected CSV path
    expected_csv = test_srt_file.with_suffix('.csv')
    
    # Convert SRT to CSV
    with open(test_srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # Test conversion
    csv_content = subtitle_csv.srttext_to_csv(srt_content)
    
    # Write to temp file
    output_file = tmp_path / "output.csv"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    # Read both CSVs and compare
    with open(expected_csv, 'r', encoding='utf-8') as f1, open(output_file, 'r', encoding='utf-8') as f2:
        reader1 = csv.reader(f1)
        reader2 = csv.reader(f2)
        
        # Compare each row
        for row1, row2 in zip(reader1, reader2):
            assert row1 == row2, f"Mismatch in {test_srt_file.name}"

# Test vocabulary replacement
def test_vocabulary_replacement():
    test_text = "Kyiv is the capital of Ukraine. Bendery is a city."
    replacements = [
        ("Kyiv", "Kiev"),
        ("Bendery", "Bendeerryy")
    ]
    expected = "Kiev is the capital of Ukraine. Bendeerryy is a city."
    
    # Test with direct replacement
    result = vocabulary.apply_replacements(test_text, replacements)
    assert result == expected
    
    # Test with regex replacement
    result = vocabulary.modify_subtitles_with_vocabular_text_only_optimized(test_text, replacements)
    assert result == expected

# Test main functionality
def test_main_script(test_srt_file, tmp_path, monkeypatch):
    from srt2csv.__main__ import main
    import sys
    
    # Prepare test arguments
    output_file = tmp_path / "output.csv"
    vocab_file = TEST_DIR / "vocabular.txt"
    
    # Mock command line arguments
    test_args = [
        "srt2csv",
        "-s", str(test_srt_file),
        "-v", str(vocab_file),
        "-o", str(output_file)
    ]
    
    with monkeypatch.context() as m:
        m.setattr(sys, 'argv', test_args)
        main()
    
    # Check if output file was created
    assert output_file.exists(), "Output file was not created"
    assert os.path.getsize(output_file) > 0, "Output file is empty"
