import tkinter as tk

from bot import run_search

root = tk.Tk()

root.title("Amazon商品検索ツール")
root.geometry("400x200")

label = tk.Label(root, text="検索キーワード")
label.pack(pady=10)

entry = tk.Entry(root, width=30)
entry.pack()

button = tk.Button(
    root,
    text="検索開始",
    command=lambda: run_search(entry.get())
)
button.pack(pady=20)

root.mainloop()
