"""File Manager Utility

Handles reading and writing text files with safe exception handling.
"""


def read_file(file_path: str) -> str:
    """Read UTF-8 text content from a file safely.

    Args:
        file_path (str): Path to the target file.

    Returns:
        str: Text content of the file.

    Raises:
        IOError: If reading fails due to missing file, permission errors, or encoding issues.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise IOError(f"Gagal membaca file '{file_path}': {e}") from e


def write_file(file_path: str, content: str) -> bool:
    """Write UTF-8 text content to a file safely.

    Args:
        file_path (str): Path to the target file.
        content (str): Text content to write.

    Returns:
        bool: True if writing succeeded.

    Raises:
        IOError: If writing fails due to permission or I/O errors.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError as e:
        raise IOError(f"Gagal menyimpan file '{file_path}': {e}") from e
