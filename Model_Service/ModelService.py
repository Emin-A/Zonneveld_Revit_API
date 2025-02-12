import sys
import json

if __name__ == "__main__":
    # Read the input from stdin
    input_data = sys.stdin.read()
    try:
        data = json.loads(input_data)
        question = data.get("question", "")
        model_data = data.get("model_data", [])
        # For demonstration, simply report back the question and number of model elements.
        response = "Received question: {0}. Number of model elements: {1}.".format(
            question, len(model_data)
        )
        print(response)
    except Exception as e:
        print("Error: " + str(e))
