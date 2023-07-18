import gradio as gr
import random
import time
import requests

# Carica il file su ChatPDF
def get_source_id(file_path):
    files = [
    ('file', ('file', open(file_path, 'rb'), 'application/octet-stream'))
    ]
    headers = {
        'x-api-key': 'sec_YCpbMyUaZuURNGVpWJKJtKC7R1B8nymD'
    }

    response = requests.post(
        'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

    if response.status_code == 200:
        return response.json()['sourceId']
    else:
        return 'Status:'+ str(response.status_code) + 'Error:' + response.text

# Riassumi

def summarize(file_path, input_answer):

    headers = {
        'x-api-key': 'sec_YCpbMyUaZuURNGVpWJKJtKC7R1B8nymD',
        "Content-Type": "application/json",
    }

    data = {
        'sourceId': get_source_id(file_path),
        'messages': [
        {
            'role': "user",
            # Il content è il text message dell'utente
            'content': input_answer,
        }
        ]
    }

    response = requests.post(
        'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['content']
    else:
        return 'Status:' + str(response.status_code) + 'Error:' + str(response.text)
    
# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

def add_text(history, text=""):
    global input_answer
    input_answer = text
    if not text.strip():  # Verifica se l'input dell'utente è vuoto
        return history, gr.update(value="", interactive=False)
    history = history + [(text, None)]
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    global file_path
    file_path = file.name
    history = history + [((file_path,), None)]
    return history


def bot(history):
    if len(history) == 1:
        response = "Grazie per aver caricato il file. Cosa vorresti conoscere riguardo il suo contenuto?"
    else:
        response = summarize(file_path, input_answer)   
    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.05)
        yield history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)

    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Seleziona un file pdf da una cartella e inizia a porgli qualche domanda",
            ).style(container=False)
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.UploadButton("📁", file_types=["pdf"])
        with gr.Column(scale=0.15, min_width=0):
            clear = gr.Button("Clear")
    

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)
    if clear.click:
        history = []
        input_answer = ""

demo.queue()
if __name__ == "__main__":
    demo.launch()
