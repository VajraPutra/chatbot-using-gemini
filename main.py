import os
import threading
from tkinter import *
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
  #Enter your instructions
    system_instruction=(
        """    """
    ),
)

BG_GRAY = "#892CDC"
BG_COLOR = "#000000"
TEXT_COLOR = "#EAECEE"
FONT = "Helvetica 12"
FONT_BOLD = "Helvetica 13 bold"

history = []

class ChatApp:
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        self.chat_session = model.start_chat(history=history)
        self.chat_log = open("chat_history.txt", "a")

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("Chatbot")
        self.window.resizable(width=True, height=True)
        self.window.configure(width=590, height=550, bg=BG_COLOR)

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)

        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.845, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)

        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        self.msg_entry = Entry(bottom_label, bg="#000000", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.07, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        send_button = Button(
            bottom_label, text="Send", fg="#FFFFFF", font=FONT_BOLD, width=20, bg="#000000",
            command=lambda: self._on_enter_pressed(None)
        )
        send_button.place(relx=0.77, rely=0.008, relheight=0.07, relwidth=0.22)

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")

        threading.Thread(target=self._process_response, args=(msg,)).start()

    def _process_response(self, msg):
        if not msg.strip():
            return

        try:
            history.append({"role": "user", "parts": [msg]})
            response = self.chat_session.send_message(msg)
            model_response = response.text
        except Exception as e:
            model_response = f"Error: {e}"

        self._display_response(model_response)

    def _insert_message(self, msg, sender):
        if not msg.strip():
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n"

        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)

        self.chat_log.write(msg1)
        self.chat_log.flush()

        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, "Chatbot is typing...\n")
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

    def _display_response(self, model_response):
        self.text_widget.configure(state=NORMAL)
        self.text_widget.delete("end-2l", "end-1l")
        self.text_widget.configure(state=DISABLED)

        msg2 = f"Chatbot: {model_response}\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg2)
        self.text_widget.configure(state=DISABLED)

        self.chat_log.write(msg2)
        self.chat_log.flush()

        self.text_widget.see(END)

        history.append({"role": "model", "parts": [model_response]})

    def __del__(self):
        self.chat_log.close()

# Run the chat application
if __name__ == "__main__":
    app = ChatApp()
    app.run()
