import os

from google.genai import types

from constants import MAX_CHARS

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the first 10,000 chars of a given file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to desired file, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)


def get_file_content(working_directory, file_path):
    """
    Reads and returns the content of a file, constrained to a
    permitted working directory.

    Args:
        working_directory: The root directory that access is
            restricted to.
        file_path: Path to the file to read, relative to
            working_directory.

    Returns:
        The file's content as a string, truncated to MAX_CHARS
        with a notice if the file exceeds that limit. Returns
        an error string if the path is outside the working
        directory, resolves to a directory, or cannot be read.
    """
    try:
        # get the absolute path for the working directory,
        # then join it with the user's target argument to
        # get the proposed path to the target. normpath()
        # makes sure the path is sanitised.
        working_dir_path = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_path, file_path))

        # check that the target dir's path contains the permitted
        # working dir in totality.
        if os.path.commonpath([working_dir_path, target_path]) != working_dir_path:
            return (
                f"Error: Cannot read {file_path} as it is outside the "
                "permitted working directory"
            )

        # check if the filepath does not resolve to a file
        if os.path.isdir(target_path):
            return f'Error: file not found or is not a regular file: "{file_path}"'

        # open file, and read/return first 10000 characters (indicate
        # if truncation was necessary)
        with open(target_path, "r") as f:
            contents = f.read(MAX_CHARS)
            if f.read(1):
                contents += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )
        return contents

    except Exception as e:
        return f"Error: {e}"
