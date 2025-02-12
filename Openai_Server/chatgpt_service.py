import openai
import sys

# Set your OpenAI API key
openai.api_key = "your-api-key"


def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[{"role": "user", "content": question}],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Error: " + str(e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No question provided.")
        sys.exit(1)
    question = sys.argv[1]
    print(ask_openai(question))
