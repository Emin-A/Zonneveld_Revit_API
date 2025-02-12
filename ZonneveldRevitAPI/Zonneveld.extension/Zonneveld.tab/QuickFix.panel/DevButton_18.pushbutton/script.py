__title__ = "AI"
__doc__ = """Unified WPF dialog with a TabControl - one tab for generic ChatGPT queries and one for Revit model=based queries(ModelMind)."""

import os
import json
import subprocess
from pyrevit import forms
from System.Windows.Documents import Run, Paragraph
from System.Windows.Media import Brushes

# --------------------------------------------------------------------
# Update these paths with the full paths to your executables and service scripts
PYTHON_EXE_PATH = r"C:\Zonneveld\Zonneveld_Revit_API\.venv\Scripts\python.exe"  # Full path to the Python executable
CHATGPT_SERVICE_PATH = r"C:\Zonneveld\Zonneveld_Revit_API\Openai_Server\chatgpt_service.py"  # Full path to chatgpt_service.py
MODEL_SERVICE_PATH = r"C:\Zonneveld\Zonneveld_Revit_API\Model_Service\ModelService.py"  # Full path to the script handling model queries


# --------------------------------------------------------------------
# ChatGPT mode: call the chatgpt_service.py via subprocess
def ask_chatgpt(question):
    try:
        result = subprocess.check_output(
            [PYTHON_EXE_PATH, CHATGPT_SERVICE_PATH, question],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        return "Error: " + e.output.strip()


# --------------------------------------------------------------------
# ModelMind mode: extract Revit model data and send query
from Autodesk.Revit.UI import UIApplication
from Autodesk.Revit.DB import FilteredElementCollector

# Get the current Revit application and document via pyRevit's __revit__ variable
uiapp = __revit__
doc = uiapp.ActiveUIDocument.Document
DATA_PATH = os.path.join(os.path.expanduser("~"), "RevitModelData.json")


def extract_model_data():
    elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
    all_data = []
    for el in elements:
        data = {
            "Id": el.Id.IntegerValue,
            "Category": (
                unicode(el.Category.Name) if el.Category and el.Category.Name else "N/A"
            ),
            "Name": (
                unicode(el.Name)
                if hasattr(el, "Name") and el.Name
                else "Unnamed Element"
            ),
            # Add any additional parameters as needed.
        }
        all_data.append(data)
    # Write JSON with ensure_ascii=False to support Unicode characters.
    with open(DATA_PATH, "w") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    return all_data


# Load model data from file if available; otherwise, extract it.
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        model_data = json.load(f)
else:
    model_data = extract_model_data()


def query_model(question):
    # Package the question and model data into a JSON object
    input_data = json.dumps({"question": question, "model_data": model_data})
    try:
        process = subprocess.Popen(
            [PYTHON_EXE_PATH, MODEL_SERVICE_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate(input=input_data)
        if process.returncode != 0:
            return "Error: " + stderr.strip()
        return stdout.strip()
    except Exception as e:
        return "Error: " + str(e)


# --------------------------------------------------------------------
# Unified WPF Form class that loads the UnifiedForm.xaml
class UnifiedChatForm(forms.WPFWindow):
    def __init__(self):
        xaml_path = os.path.join(os.path.dirname(__file__), "UnifiedForm.xaml")
        forms.WPFWindow.__init__(self, xaml_path)

        # Attach event handlers to the Send buttons in each tab
        self.ChatGPTSendButton.Click += self.chatgpt_send
        self.ModelMindSendButton.Click += self.modelmind_send

    def chatgpt_send(self, sender, args):
        question = self.ChatGPTInput.Text.strip()
        if not question:
            return

        # Add the user's question to the ChatGPT conversation history (red text)
        para = Paragraph()
        run = Run("User: " + question + "\n")
        run.Foreground = Brushes.Red
        para.Inlines.Add(run)
        self.ChatGPTHistory.Document.Blocks.Add(para)

        # Get the AI response via chatgpt_service.py
        response = ask_chatgpt(question)

        # Add the response in green
        para2 = Paragraph()
        run2 = Run("ChatGPT: " + response + "\n\n")
        run2.Foreground = Brushes.Green
        para2.Inlines.Add(run2)
        self.ChatGPTHistory.Document.Blocks.Add(para2)

        # Clear input and scroll to end
        self.ChatGPTInput.Text = ""
        self.ChatGPTHistory.ScrollToEnd()

    def modelmind_send(self, sender, args):
        question = self.ModelMindInput.Text.strip()
        if not question:
            return

        # Add the user's question to the ModelMind conversation history (red text)
        para = Paragraph()
        run = Run("User: " + question + "\n")
        run.Foreground = Brushes.Red
        para.Inlines.Add(run)
        self.ModelMindHistory.Document.Blocks.Add(para)

        # Query the model-based service (includes model data)
        response = query_model(question)

        # Add the response in green
        para2 = Paragraph()
        run2 = Run("ModelMind: " + response + "\n\n")
        run2.Foreground = Brushes.Green
        para2.Inlines.Add(run2)
        self.ModelMindHistory.Document.Blocks.Add(para2)

        # Clear input and scroll to end
        self.ModelMindInput.Text = ""
        self.ModelMindHistory.ScrollToEnd()


# --------------------------------------------------------------------
# Launch the unified chat form
try:
    UnifiedChatForm().ShowDialog()
except Exception as e:
    print("An error occurred while displaying the unified chat form: " + str(e))
