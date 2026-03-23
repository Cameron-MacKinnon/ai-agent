import os
import subprocess

from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes and captures the subsequent output of a '.py' file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to desired file, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="An array of cmd line arguments that will be passed to the invoked function",
                items=types.Schema(
                    type=types.Type.STRING, description="A single command line argument"
                ),
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(working_directory, file_path, args=None):
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
                f'Error: Cannot execute "{file_path}" as it is outside the '
                "permitted working directory"
            )

        # check the target path's validity
        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if os.path.splitext(target_path)[1] != ".py":
            return f'Error: "{file_path}" is not a Python file'

        # build the basic command
        command = ["python", target_path]
        if args:
            command.extend(args)

        # call subprocess, interrogate response, gen return string
        result = subprocess.run(
            args=command, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return f"Process exited with code {result.returncode}"
        if not result.stdout and not result.stderr:
            return "No output produced"
        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
