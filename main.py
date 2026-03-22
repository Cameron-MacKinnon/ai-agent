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
    response = client.models.generate_content(
        model=MODEL,
        contents=(
            "Why is Boot.dev such a great place to learn "
            "backend development? Use one paragraph maximum."
        ),
    )
    print(response.text)


if __name__ == "__main__":
    main()
