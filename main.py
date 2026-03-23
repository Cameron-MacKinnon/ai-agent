import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions
from constants import MODEL
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

    # call model to generate response
    generate_response(client, messages, args)


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
            "usage metadata not found, it's likely that "
            "the API request failed, try again later."
        )

    # print interaction details (optional verbosity)
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    if response.function_calls:
        for call in response.function_calls:
            print(f"Calling function: {call.name}({call.args})")
    print(f"Response:\n{response.text}")


if __name__ == "__main__":
    main()
