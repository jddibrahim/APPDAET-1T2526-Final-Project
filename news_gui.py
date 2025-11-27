# news_gui.py
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import matplotlib.pyplot as plt
from collections import Counter

# Import your backend (news_backend.py)
from news_backend import NewsBackend, country_dict, language_dict

# Build sorted lists for dropdowns
COUNTRY_LIST = [""] + sorted(country_dict.keys())
LANGUAGE_LIST = [""] + sorted(language_dict.keys())

class NewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("News Search — GUI")
        self.root.geometry("950x700")

        self.backend = NewsBackend()

        # Top frame - inputs
        top = tk.Frame(root, pady=8)
        top.pack(fill="x")

        tk.Label(top, text="Search Query:").grid(row=0, column=0, sticky="w", padx=6)
        self.query_entry = tk.Entry(top, width=45)
        self.query_entry.grid(row=0, column=1, columnspan=2, sticky="w")

        tk.Label(top, text="Language:").grid(row=1, column=0, sticky="w", padx=6, pady=(6,0))
        self.lang_var = tk.StringVar()
        self.lang_cb = ttk.Combobox(top, textvariable=self.lang_var, values=LANGUAGE_LIST, width=30)
        self.lang_cb.grid(row=1, column=1, sticky="w", pady=(6,0))

        tk.Label(top, text="Country:").grid(row=1, column=2, sticky="w", padx=(10,0), pady=(6,0))
        self.country_var = tk.StringVar()
        self.country_cb = ttk.Combobox(top, textvariable=self.country_var, values=COUNTRY_LIST, width=30)
        self.country_cb.grid(row=1, column=3, sticky="w", pady=(6,0))

        # Buttons
        btn_frame = tk.Frame(root, pady=8)
        btn_frame.pack(fill="x")
        self.search_btn = tk.Button(btn_frame, text="🔎 Search", command=self.run_search)
        self.search_btn.pack(side="left", padx=6)

        self.trend_btn = tk.Button(btn_frame, text="📈 Generate Trend", command=self.run_generate_trend)
        self.trend_btn.pack(side="left", padx=6)

        # Results summary
        self.summary_label = tk.Label(root, text="Articles found: 0 | Page 0/0")
        self.summary_label.pack(anchor="w", padx=8, pady=(4,0))

        # Results area (scrollable)
        results_container = tk.Frame(root)
        results_container.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(results_container)
        self.scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Pre-create five article frames
        self.article_frames = []
        for i in range(self.backend.PAGE_SIZE):
            fr = ttk.Frame(self.scrollable_frame, padding=8, style="Card.TFrame")
            fr.pack(fill="x", pady=6)
            title = tk.Label(fr, text="", font=("TkDefaultFont", 12, "bold"), wraplength=820, justify="left", anchor="w")
            title.pack(anchor="w")
            meta = tk.Label(fr, text="", font=("TkDefaultFont", 9), fg="#555555", wraplength=820, justify="left", anchor="w")
            meta.pack(anchor="w", pady=(4,0))
            snippet = tk.Label(fr, text="", wraplength=820, justify="left", anchor="w")
            snippet.pack(anchor="w", pady=(6,0))
            url = tk.Label(fr, text="", fg="blue", cursor="hand2", wraplength=820, justify="left", anchor="w")
            url.pack(anchor="w", pady=(6,0))

            # bind URL click to open in browser
            def make_open(link):
                import webbrowser
                return lambda e: webbrowser.open_new(link) if link else None

            # We'll set url text and binding later
            self.article_frames.append({
                "frame": fr, "title": title, "meta": meta, "snippet": snippet, "url": url
            })

        # Pagination controls
        pag = tk.Frame(root, pady=6)
        pag.pack(fill="x")

        self.first_btn = tk.Button(pag, text="<< First", command=self.run_first, state="disabled")
        self.first_btn.pack(side="left", padx=4)
        self.prev_btn = tk.Button(pag, text="< Prev", command=self.run_prev, state="disabled")
        self.prev_btn.pack(side="left", padx=4)
        self.next_btn = tk.Button(pag, text="Next >", command=self.run_next, state="disabled")
        self.next_btn.pack(side="left", padx=4)
        self.last_btn = tk.Button(pag, text="Last >>", command=self.run_last, state="disabled")
        self.last_btn.pack(side="left", padx=4)

        # status bar
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(root, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", padx=4, pady=(6,4))

    # -------------------------
    # UI state helpers
    # -------------------------
    def set_loading(self, is_loading: bool, text="Loading..."):
        state = "disabled" if is_loading else "normal"
        for w in [self.search_btn, self.trend_btn, self.first_btn, self.prev_btn, self.next_btn, self.last_btn]:
            try:
                w.config(state=state)
            except:
                pass
        self.status_var.set(text if is_loading else "Ready")

    def update_summary(self):
        total = self.backend.total_articles
        page = (self.backend.offset // self.backend.PAGE_SIZE) + 1 if total>0 else 0
        max_page = self.backend.total_pages
        self.summary_label.config(text=f"Articles found: {total} | Page {page}/{max_page}")

        # enable/disable pagination buttons
        if total == 0:
            for b in [self.first_btn, self.prev_btn, self.next_btn, self.last_btn]:
                b.config(state="disabled")
        else:
            self.first_btn.config(state="normal" if self.backend.offset > 0 else "disabled")
            self.prev_btn.config(state="normal" if self.backend.offset > 0 else "disabled")
            self.next_btn.config(state="normal" if (self.backend.offset + self.backend.PAGE_SIZE) < total else "disabled")
            self.last_btn.config(state="normal" if (self.backend.offset + self.backend.PAGE_SIZE) < total else "disabled")

    def clear_article_frames(self):
        for slot in self.article_frames:
            slot["title"].config(text="")
            slot["meta"].config(text="")
            slot["snippet"].config(text="")
            slot["url"].config(text="", fg="blue")
            # unbind any previous click events by replacing with dummy
            slot["url"].bind("<Button-1>", lambda e: None)

    def populate_articles(self, articles):
        self.clear_article_frames()
        for i, entry in enumerate(articles):
            slot = self.article_frames[i]
            title = entry.get("title") or "(No title)"
            author = entry.get("author") or "Unknown"
            published = entry.get("publish_date") or "Unknown date"
            lang_code = entry.get("language") or ""
            source_country = entry.get("source_country") or ""
            # find names
            lang_name = next((n for n, c in language_dict.items() if c and c.lower() == lang_code.lower()), lang_code)
            country_name = next((n for n, c in country_dict.items() if c and c.lower() == source_country.lower()), source_country)

            snippet = (entry.get("text") or "")[:400].replace("\n", " ") + "..."
            url_text = entry.get("url") or ""

            slot["title"].config(text=title)
            slot["meta"].config(text=f"Author: {author} | Published: {published} | Lang: {lang_name} | Country: {country_name}")
            slot["snippet"].config(text=snippet)
            slot["url"].config(text=url_text)
            if url_text:
                import webbrowser
                slot["url"].bind("<Button-1>", lambda e, link=url_text: webbrowser.open_new(link))

    # -------------------------
    # Threaded operations
    # -------------------------
    def run_search(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showinfo("Input needed", "Please enter a search query.")
            return

        # resolve selected language and country to codes
        lang_name = self.lang_var.get()
        country_name = self.country_var.get()
        lang_code = language_dict.get(lang_name) if lang_name else None
        country_code = country_dict.get(country_name) if country_name else None

        self.set_loading(True, "Searching...")
        threading.Thread(target=self._search_thread, args=(query, lang_code, country_code), daemon=True).start()

    def _search_thread(self, query, lang_code, country_code):
        try:
            results = self.backend.search(query, lang_code=lang_code, country_code=country_code)
            # backend.search returns first page results (5 items) or []
            self.root.after(0, lambda: self.populate_articles(results))
            self.root.after(0, self.update_summary)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {e}"))
        finally:
            self.root.after(0, lambda: self.set_loading(False))

    def run_next(self):
        self.set_loading(True, "Loading next page...")
        threading.Thread(target=self._next_thread, daemon=True).start()

    def _next_thread(self):
        try:
            articles = self.backend.next_page()
            self.root.after(0, lambda: self.populate_articles(articles))
            self.root.after(0, self.update_summary)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Next page failed: {e}"))
        finally:
            self.root.after(0, lambda: self.set_loading(False))

    def run_prev(self):
        self.set_loading(True, "Loading previous page...")
        threading.Thread(target=self._prev_thread, daemon=True).start()

    def _prev_thread(self):
        try:
            articles = self.backend.prev_page()
            self.root.after(0, lambda: self.populate_articles(articles))
            self.root.after(0, self.update_summary)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Prev page failed: {e}"))
        finally:
            self.root.after(0, lambda: self.set_loading(False))

    def run_first(self):
        self.set_loading(True, "Loading first page...")
        threading.Thread(target=self._first_thread, daemon=True).start()

    def _first_thread(self):
        try:
            articles = self.backend.first_page()
            self.root.after(0, lambda: self.populate_articles(articles))
            self.root.after(0, self.update_summary)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"First page failed: {e}"))
        finally:
            self.root.after(0, lambda: self.set_loading(False))

    def run_last(self):
        self.set_loading(True, "Loading last page...")
        threading.Thread(target=self._last_thread, daemon=True).start()

    def _last_thread(self):
        try:
            articles = self.backend.last_page()
            self.root.after(0, lambda: self.populate_articles(articles))
            self.root.after(0, self.update_summary)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Last page failed: {e}"))
        finally:
            self.root.after(0, lambda: self.set_loading(False))

    def run_generate_trend(self):
        if not self.backend.query:
            messagebox.showinfo("No query", "Search first before generating trend.")
            return
        self.set_loading(True, "Generating trend...")
        threading.Thread(target=self._trend_thread, daemon=True).start()

    def _trend_thread(self):
        try:
            dates = self.backend.get_trend_data()
            if not dates:
                self.root.after(0, lambda: messagebox.showinfo("No data", "No publish date data found to generate a trend."))
                return

            counts = Counter(dates)
            # sort by date
            sorted_dates = sorted(counts.keys())
            y = [counts[d] for d in sorted_dates]
            x = [d for d in sorted_dates]

            # Plot
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_title(f"Search Trend for '{self.backend.query}'")
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Articles")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Trend generation failed: {e}"))
        finally:
            self.root.after(0, lambda: self.set_loading(False))

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsGUI(root)
    root.mainloop()
