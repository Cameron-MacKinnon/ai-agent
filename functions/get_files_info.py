import os


def get_files_info(working_directory, directory="."):
    """
    Lists files and directories within a given directory,
    constrained to a permitted working directory.

    Args:
        working_directory: The root directory that access is
            restricted to.
        directory: The target directory to list, relative to
            working_directory. Defaults to ".".

    Returns:
        A newline-separated string of entries, each showing the
        name, size in bytes, and whether it is a directory.
        Returns an error string if the path is outside the working
        directory, is not a directory, or cannot be read.
    """
    # get the absolute path for the working directory,
    # then join it with the user's target argument to
    # get the proposed path to the target. normpath()
    # makes sure the path is sanitised.
    working_dir_path = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_dir_path, directory))

    # check that the target dir's path contains the permitted
    # working dir in totality.
    if os.path.commonpath([working_dir_path, target_path]) != working_dir_path:
        return (
            f"Error: Cannot list {directory} as it is outside the "
            "permitted working directory"
        )

    # check if the target path is in fact a directory,
    # not a file
    if not os.path.isdir(target_path):
        return f"Error: {directory} is not a directory"

    # iterate over the target dir and build info about each
    # file/dir therein
    contents = []
    try:
        for path in os.listdir(path=target_path):
            name = os.path.basename(os.path.join(target_path, path))
            size = os.path.getsize(os.path.join(target_path, path))
            is_dir = os.path.isdir(os.path.join(target_path, path))
            contents.append(f"- {name}: file_size={size} bytes, is_dir={is_dir}")
    except Exception as e:
        return f"Error: failed to perform os.path action - {e}"

    # return a string representation of the collected info
    return "\n".join(contents)
