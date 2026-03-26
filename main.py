import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions, call_function
from constants import MAX_ITERATIONS, MODEL
from prompts import system_prompt

# attempt to load env vars from /.env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key is None:
    raise RuntimeError(
        "API key not found, make sure your .env file "
        "contains a variable in the following format:\n"
        "GEMINI_API_KEY='your_api_key_here'"
    )

# init gemini client
client = genai.Client(api_key=api_key)


def generate_response(client, messages, args):
    # generate LLM response
    response = client.models.generate_content(
        model=MODEL,
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt, temperature=0, tools=[available_functions]
        ),
    )

    # validate response
    if response.usage_metadata is None:
        raise RuntimeError(
            "Error: usage metadata not found, it's likely that "
            "the API request failed, try again later."
        )

    # record the response's 'candidates' to the message context ,
    # (raise an error if they're not present)
    if not response.candidates:
        raise RuntimeError("Error: malformed response: no candidates")
    for candidate in response.candidates:
        messages.append(candidate.content)

    # print meatadata (optional with verbosity)
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    # if the model doesn't want to make any function calls, then we're
    # done here - return the text response
    if not response.function_calls:
        print(f"Final Response:\n{response.text}")
        return True

    # call any desired functions, validate response, add to list
    function_results = []
    for func in response.function_calls:
        function_result = call_function(func, args.verbose)
        if not function_result.parts:
            raise Exception("Error: malformed function call")
        if not function_result.parts[0].function_response:
            raise Exception("Error: missing function response object")
        if not function_result.parts[0].function_response.response:
            raise Exception("Error: missing function response string")
        function_results.append(function_result.parts[0])
        if not args.verbose:
            continue
        print(f"-> {function_result.parts[0].function_response.response}")

    # Add the details of the function calls to the model's context
    messages.append(types.Content(role="user", parts=function_results))

    return False


def main():

    # init arg parser and parse cmd line args
    parser = argparse.ArgumentParser(description="ai-agent")
    parser.add_argument("user_prompt", type=str, help="Your LLM prompt")
    parser.add_argument(
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()

    # create list of messages back <-> forth between user/model
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    # call model to generate response, allow limited iterations. Once the model
    # decides it's finished making function calls - generate_response will
    # print the final resonse then return True. In this case we exit the program
    # in a success state
    for _ in range(MAX_ITERATIONS):
        done = generate_response(client, messages, args)
        if done:
            sys.exit()

    # we'll only make it here if the model failed to generate a final response
    # within the maximum allowed iterations. This is a failure state.
    sys.exit("Program terminated: too many iterations")

if __name__ == "__main__":
    main()
