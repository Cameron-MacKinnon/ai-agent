import argparse
import os

from dotenv import load_dotenv
from google import genai

from constants import MODEL

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

    # init arg parser
    parser = argparse.ArgumentParser(description="ai-agent")
    parser.add_argument("prompt_str", type=str, help="Your LLM prompt")
    args = parser.parse_args()

    # generate LLM response
    response = client.models.generate_content(
        model=MODEL,
        contents=args.prompt_str,
    )

    # validate response
    if response.usage_metadata is None:
        raise RuntimeError(
            "usage metadata not found, it's likely that "
            "the API request failed, try again later."
        )

    # print interaction details
    print(f"User prompt: {args.prompt_str}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print(f"Response:\n{response.text}")


if __name__ == "__main__":
    main()
