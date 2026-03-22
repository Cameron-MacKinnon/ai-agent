import os


def write_file(working_directory, file_path, content):
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
                f'Error: Cannot read "{file_path}" as it is outside the '
                "permitted working directory"
            )

        # check that the path doesn't resolve to a directory
        if os.path.isdir(target_path):
            return f'Error: cannot write to "{file_path}" as it is a directory'

        # make sure all the necessary parent dirs exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # open the file in write mode and overwrite it with the
        # value of 'content'
        with open(target_path, "w") as f:
            f.write(content)

        # return success message
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except Exception as e:
        return f"Error: {e}"
