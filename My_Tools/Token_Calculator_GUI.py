import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import font
from tkinter import ttk

import My_Tools.Token_Calculator as tokenC










def calculate_tokens(text):
    con = [{"role": "user", "content": text}]
    tokens = tokenC.num_tokens_from_conversation(con, "gpt-3.5-turbo")
    return tokens-9


class TokenCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Token 計算器')
        self.configure(bg='black')

        self.text_font = tk.StringVar(value="Arial")
        self.text_size = tk.IntVar(value=14)  # 文字大小的變量

        self.init_ui()

    def init_ui(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 創建字體選擇下拉菜單
        font_selector = ttk.Combobox(control_frame, textvariable=self.text_font, values=font.families(), width=20)
        font_selector.grid(row=0, column=0, padx=5, pady=5)
        font_selector.bind('<<ComboboxSelected>>', self.update_text_font)

        # 創建調整文字大小的 Spinbox
        size_spinbox = ttk.Spinbox(control_frame, from_=2, to=128, increment=2, textvariable=self.text_size, command=self.update_text_size, width=7)
        size_spinbox.grid(row=0, column=1, padx=5, pady=5)

        # 創建計算tokens的按鈕
        calculate_button = tk.Button(control_frame, text="Count it!", command=self.calculate_and_display_tokens, bg="grey", fg="white")
        calculate_button.grid(row=0, column=2, padx=5, pady=5)

        # 創建顯示tokens的標籤
        self.tokens_label = tk.Label(self, text="Tokens: 0", bg="black", fg="white", font=("Arial", 20))
        self.tokens_label.pack(padx=10, pady=5)

        # 文字輸入框外層的滾動條
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_scroll = tk.Scrollbar(text_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 創建文本輸入框，並與滾動條連接
        self.text_input = tk.Text(text_frame, bg="grey", fg="white", 
                                  font=(self.text_font.get(), self.text_size.get()), 
                                  yscrollcommand=self.text_scroll.set)
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scroll.config(command=self.text_input.yview)

    def update_text_font(self, event=None):
        self.update_text_size()

    def update_text_size(self):
        new_font = (self.text_font.get(), self.text_size.get())
        self.text_input.configure(font=new_font)

    def calculate_and_display_tokens(self):
        # 獲取文本框內的文本
        text = self.text_input.get("1.0", tk.END)
        # 計算tokens
        tokens = calculate_tokens(text)
        # 更新標籤顯示tokens數量
        self.tokens_label.configure(text=f"Tokens: {tokens}")










if __name__ == "__main__":
    app = TokenCalculatorApp()
    app.mainloop()




