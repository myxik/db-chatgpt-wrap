import sys
import openai
import pandas as pd

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

while True:
    s = get_user_input()
    messages.append({"role": "user", "content": s})
    main_instruction = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    print(main_instruction.choices[0].message.content)
    messages.append({"role": "assistant", "content": main_instruction.choices[0].message.content})
    executor.append({"role": "user", "content": main_instruction.choices[0].message.content})

    supp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=executor
    )
    print(supp.choices[0].message.content)
    exec(supp.choices[0].message.content)
