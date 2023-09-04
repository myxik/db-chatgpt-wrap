import sys
import openai
import pandas as pd
import gradio as gr

from pathlib import Path
from const import *


def get_meta(db):
    s = f"""[META]
    DB type: pandas.dataframe
    Tables: train
    Columns: {','.join(db.columns.to_list())}
    """
    return s


def get_user_input():
    s = input(">>>")
    return s


openai.api_key = sys.argv[1]
db = pd.read_csv("./train.csv.zip")

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": prompt_ex1},
    {"role": "assistant", "content": prompt_answ1},
    {"role": "user", "content": get_meta(db)},
    {"role": "assistant", "content": "[IGNORED]"},
]

executor = [
    {"role": "system", "content": system_executor},
]


class CapturingOutput:
    def __init__(self):
        self._original_stdout = sys.stdout
        self._captured_output = []

    def write(self, text):
        self._captured_output.append(text)

    def get_output(self):
        return ''.join(self._captured_output)

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self._original_stdout

def execute_and_capture(code):
    with CapturingOutput() as output_capturer:
        exec(code)
    return output_capturer.get_output()


def interface(message, chat_history):
    messages.append({"role": "user", "content": message})
    main_instruction = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    print(main_instruction.choices[0].message.content)
    messages.append({"role": "assistant", "content": main_instruction.choices[0].message.content})
    executor.append({"role": "user", "content": main_instruction.choices[0].message.content})

    supp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=executor
    )
    print(supp.choices[0].message.content)
    try:
        out = execute_and_capture(supp.choices[0].message.content.replace("```python", "").replace("```", "").replace("statsmodels.tsa.arima_model.ARIMA", "statsmodels.tsa.arima.model.ARIMA"))
    except Exception as e:
        print(e)
        out = "Sorry there was a mistake in executing the code, You can try again. We are still working on covering all cases"
    splitted_out = out.split()
    for o in splitted_out:
        if Path(f"./{o}").exists():
            out = (o, "")
            break

    chat_history.append((message, out))
    return "", chat_history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(avatar_images=(None, ("./0.png")))
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(interface, [msg, chatbot], [msg, chatbot])

demo.launch()