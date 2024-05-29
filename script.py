import gradio as gr
import modules.shared as shared
import json
from datetime import datetime
from pathlib import Path
import html
import re


myprompt=""
myreply=""
mytag=""

params = {
    "name": "SmartSave",
    "display_name": "SmartSave",
    "activate": True,
    "custom string": "n/a",
}

def manual_save_data(filename):
    global mytag

    if filename == '':
        print(f'Manual save failure. The filename is empty.')
        return

    mytime = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
    fname = f"{filename}.txt"
    
    file_path=f'extensions/{params["name"]}/output'
    
    if not Path(file_path).exists():
        Path(file_path).mkdir()
    
    model = shared.model_name
    with open(Path(f'{file_path}/{fname}'), 'a+', encoding='utf-8') as f:
        f.write(f'Save Time: {mytime}\n')
        f.write(f'Model: {model}\n')
        f.write(f'Tag: {mytag}\n')
        f.write(f'Content:\n')
        f.write(f'{html.unescape(myprompt)}{html.unescape(myreply)}\n\n')
        f.write('------------------------------------------------------------\n\n')

def auto_save_data(string):
    mydate = datetime.now().strftime('%Y%m%d')
    filename = f"{mydate}_text_log"
    
    manual_save_data(filename)

def input_modifier(string):
    """
    This function is applied to your text inputs before
    they are fed into the model.
    """ 
    global myprompt
    myprompt=string
    
    # Support commenting out some lines.
    string = re.sub(r'(?m)^\s*!@#.*\n?', '', string)
    
    # Remove trailing new lines.
    string = string.rstrip()

    return string

def output_modifier(string):
    """
    This function is applied to the model outputs.
    """
    global myreply
    
    # Remove the last </s>.
    if string[-10:] == '&lt;/s&gt;':
        string = string[:-10]
    myreply=string

    if not params['activate']:
        return string
    
    auto_save_data(string)

    return string

def bot_prefix_modifier(string):
    """
    This function is only applied in chat mode. It modifies
    the prefix text for the Bot and can be used to bias its
    behavior.
    """
    return string

def update_tag(tag):
    global mytag
    mytag = tag

def ui():
    # Gradio elements
    activate = gr.Checkbox(value=params['activate'], label='Activate AutoSave')

    # Event functions to update the parameters in the backend
    activate.change(lambda x: params.update({"activate": x}), activate, None)
    
    filename_txt = gr.Textbox(label="Filename")
    tag_txt = gr.Textbox(label="Tag")
    tag_txt.change(update_tag, inputs=[tag_txt])
    save_btn = gr.Button(value="Manual Save")
    save_btn.click(manual_save_data, inputs=[filename_txt])
