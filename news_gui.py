# news_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from news_backend import NewsBackend, country_dict, language_dict

# Prepare sorted lists for dropdowns
COUNTRY_LIST = [""] + sorted(country_dict.keys())
LANGUAGE_LIST = [""] + sorted(language_dict.keys())

class SimpleNewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("News Search App")
        self.root.geometry("900x600")

        # Backend instance
        self.backend = NewsBackend()

        # --- Input Section ---
        input_frame = tk.Frame(root, pady=8)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Search Query:").grid(row=0, column=0, sticky="w", padx=5)
        self.query_entry = tk.Entry(input_frame, width=50)
        self.query_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Language:").grid(row=1, column=0, sticky="w", padx=5, pady=(6,0))
        self.lang_var = tk.StringVar()
        self.lang_cb = ttk.Combobox(input_frame, textvariable=self.lang_var, values=LANGUAGE_LIST, width=20)
        self.lang_cb.grid(row=1, column=1, sticky="w", pady=(6,0))

        tk.Label(input_frame, text="Country:").grid(row=1, column=2, sticky="w", padx=(10,0), pady=(6,0))
        self.country_var = tk.StringVar()
        self.country_cb = ttk.Combobox(input_frame, textvariable=self.country_var, values=COUNTRY_LIST, width=20)
        self.country_cb.grid(row=1, column=3, sticky="w", pady=(6,0))

        # --- Buttons ---
        button_frame = tk.Frame(root, pady=8)
        button_frame.pack(fill="x")
        self.search_btn = tk.Button(button_frame, text="Search", command=self.search)
        self.search_btn.pack(side="left", padx=5)

        # --- Summary / Page Label ---
        self.summary_label = tk.Label(root, text="Articles found: 0 | Page 0/0")
        self.summary_label.pack(anchor="w", padx=5)

        # --- Article Display ---
        self.results_frame = tk.Frame(root)
        self.results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.article_labels = []
        for _ in range(self.backend.PAGE_SIZE):
            lbl = tk.Label(self.results_frame, text="", justify="left", anchor="w", wraplength=850)
            lbl.pack(anchor="w", pady=5)
            self.article_labels.append(lbl)

        # --- Pagination Buttons ---
        pag_frame = tk.Frame(root)
        pag_frame.pack(pady=5)
        self.first_btn = tk.Button(pag_frame, text="<< First", command=self.first_page, state="disabled")
        self.first_btn.pack(side="left", padx=2)
        self.prev_btn = tk.Button(pag_frame, text="< Prev", command=self.prev_page, state="disabled")
        self.prev_btn.pack(side="left", padx=2)
        self.next_btn = tk.Button(pag_frame, text="Next >", command=self.next_page, state="disabled")
        self.next_btn.pack(side="left", padx=2)
        self.last_btn = tk.Button(pag_frame, text="Last >>", command=self.last_page, state="disabled")
        self.last_btn.pack(side="left", padx=2)

    # -------------------------
    # Search & Display Methods
    # -------------------------
    def search(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showinfo("Input needed", "Please enter a search query.")
            return
        lang = self.lang_var.get()
        country = self.country_var.get()
        lang_code = language_dict.get(lang) if lang else None
        country_code = country_dict.get(country) if country else None

        results = self.backend.search(query, lang_code, country_code)
        self.show_articles(results)
        self.update_summary()

    def show_articles(self, articles):
        for i, lbl in enumerate(self.article_labels):
            if i < len(articles):
                a = articles[i]
                text = f"Title: {a.get('title','No title')}\n"
                text += f"Author: {a.get('author','Unknown')} | Published: {a.get('publish_date','Unknown')}\n"
                snippet = (a.get('text','')[:300] + "...") if a.get('text') else ""
                text += f"{snippet}\nURL: {a.get('url','')}"
                lbl.config(text=text)
                lbl.bind("<Button-1>", lambda e, url=a.get('url'): webbrowser.open_new(url) if url else None)
            else:
                lbl.config(text="")

    def update_summary(self):
        total = self.backend.total_articles
        page = (self.backend.offset // self.backend.PAGE_SIZE) + 1 if total>0 else 0
        max_page = self.backend.total_pages
        self.summary_label.config(text=f"Articles found: {total} | Page {page}/{max_page}")
        # enable/disable buttons
        self.first_btn.config(state="normal" if self.backend.offset > 0 else "disabled")
        self.prev_btn.config(state="normal" if self.backend.offset > 0 else "disabled")
        self.next_btn.config(state="normal" if self.backend.offset + self.backend.PAGE_SIZE < total else "disabled")
        self.last_btn.config(state="normal" if self.backend.offset + self.backend.PAGE_SIZE < total else "disabled")

    # -------------------------
    # Pagination Methods
    # -------------------------
    def next_page(self):
        articles = self.backend.next_page()
        self.show_articles(articles)
        self.update_summary()

    def prev_page(self):
        articles = self.backend.prev_page()
        self.show_articles(articles)
        self.update_summary()

    def first_page(self):
        articles = self.backend.first_page()
        self.show_articles(articles)
        self.update_summary()

    def last_page(self):
        articles = self.backend.last_page()
        self.show_articles(articles)
        self.update_summary()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleNewsGUI(root)
    root.mainloop()
