import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class GroqService:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not set")

        self.client = Groq(api_key=api_key)

        self.model = "openai/gpt-oss-20b"

    def ask(self, question):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
        )

        return response.choices[0].message.content


if __name__ == "__main__":

    service = GroqService()

    answer = service.ask(
        "Explain what a customer support ticket is in one sentence."
    )

    print("Groq response:")
    print(answer)