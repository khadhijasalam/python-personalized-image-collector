import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests, os, time, threading, re, hashlib, webbrowser
from urllib.parse import quote
from bs4 import BeautifulSoup

# ---------- helpers --------------------------------------------------------- #
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
}
SKIP_TERMS = {'logo', 'icon', 'banner', 'button', 'ad', 'gstatic', 'google'}
IMG_EXT_RE = re.compile(r'\.(jpe?g|png|gif|webp)(\?|$)', re.I)
URL_RE = re.compile(r'https://[^"\'>\s]+\.(?:jpg|jpeg|png|gif|webp)', re.I)

def valid_img(url: str) -> bool:
    return (url.startswith('http')
            and IMG_EXT_RE.search(url)
            and not any(t in url.lower() for t in SKIP_TERMS))

def fetch(url, session, **kw):
    try:
        return session.get(url, timeout=10, **kw)
    except Exception:
        return None

def extract_imgs(text: str) -> list[str]:
    return [u for u in URL_RE.findall(text) if valid_img(u)]

# ---------- GUI class ------------------------------------------------------- #
class ScraperGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Profile Image Scraper")
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        self.running = tk.BooleanVar(value=False)
        self.folder = tk.StringVar(value=os.path.join(os.getcwd(), "profile_images"))
        self.max_imgs = tk.IntVar(value=5)

        self.build_ui()

    # ----------------------------- UI -------------------------------------- #
    def build_ui(self):
        f = ttk.Frame(self.root, padding=12); f.pack(fill=tk.BOTH, expand=True)

        # person details
        det = ttk.LabelFrame(f, text="Person"); det.pack(fill=tk.X, pady=8)
        self.name   = self._entry_row(det, "Full Name:", 0)
        self.lnkurl = self._entry_row(det, "LinkedIn URL:", 1)
        self.compan = self._entry_row(det, "Company/Title:", 2)

        # settings
        setf = ttk.LabelFrame(f, text="Settings"); setf.pack(fill=tk.X, pady=8)
        self._entry_row(setf, "Folder:", 0, var=self.folder, browse=True)
        self._entry_row(setf, "Max Images:", 1, var=self.max_imgs, width=6)

        # buttons
        btn = ttk.Frame(f); btn.pack(pady=6, fill=tk.X)
        self.start_b = ttk.Button(btn, text="Start", command=self.start)
        self.stop_b  = ttk.Button(btn, text="Stop", command=self.stop, state=tk.DISABLED)
        ttk.Button(btn, text="Clear Log", command=lambda: self.logbox.delete(1.0, tk.END)).pack(side=tk.RIGHT)
        ttk.Button(btn, text="Open Folder", command=self.open_folder).pack(side=tk.RIGHT, padx=8)
        self.start_b.pack(side=tk.LEFT); self.stop_b.pack(side=tk.LEFT, padx=8)

        # progress + log
        self.prog = ttk.Progressbar(f, mode="indeterminate"); self.prog.pack(fill=tk.X, pady=4)
        self.logbox = scrolledtext.ScrolledText(f, height=12, font=("Consolas", 9))
        self.logbox.pack(fill=tk.BOTH, expand=True)

    def _entry_row(self, parent, label, row, var=None, width=40, browse=False):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
        var = var or tk.StringVar()
        ent = ttk.Entry(parent, textvariable=var, width=width)
        ent.grid(row=row, column=1, sticky=tk.EW, padx=6)
        if browse:
            ttk.Button(parent, text="…", command=lambda: self._browse(var)).grid(row=row, column=2)
        parent.columnconfigure(1, weight=1)
        return var

    # -------------------------- actions ------------------------------------ #
    def start(self):
        if not self.name.get().strip():
            messagebox.showerror("Need name", "Please enter the person's full name")
            return
        self.running.set(True)
        self.prog.start(); self.start_b["state"]="disabled"; self.stop_b["state"]="normal"
        threading.Thread(target=self.worker, daemon=True).start()

    def stop(self):
        self.running.set(False)

    def open_folder(self):
        path = self.folder.get()
        os.makedirs(path, exist_ok=True)
        webbrowser.open(path)

    def _browse(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    # --------------------------- worker ------------------------------------ #
    def worker(self):
        self.log("Scraping started")
        dest_dir = os.path.join(self.folder.get(), self.name.get().strip().replace(' ', '_'))
        os.makedirs(dest_dir, exist_ok=True)

        searches = [
            self.linkedin_image,
            lambda: self.search_google(f'"{self.name.get()}" profile picture {self.compan.get()}'),
            lambda: self.search_duckduckgo(f'"{self.name.get()}" headshot {self.compan.get()}'),
            lambda: self.search_site('medium.com', "Medium"),
            lambda: self.search_site('substack.com', "Substack")
        ]

        found = []
        for fn in searches:
            if not self.running.get() or len(found) >= self.max_imgs.get(): break
            imgs = fn() or []
            found.extend(imgs[: self.max_imgs.get() - len(found)])

        downloaded = sum(self.download(i, dest_dir) for i in found)
        self.log(f"Finished – downloaded {downloaded}/{self.max_imgs.get()} images")
        self.done()

    # ------------------------- search funcs -------------------------------- #
    def linkedin_image(self):
        url = self.lnkurl.get().strip()
        if not url: return []
        r = fetch(url, self.session)
        if not r or r.status_code != 200: return []
        soup = BeautifulSoup(r.text, 'html.parser')
        for sel in ('meta[property="og:image"]', 'img[src*="profile"]'):
            tag = soup.select_one(sel)
            src = tag.get("content") if tag and tag.name == "meta" else tag.get("src") if tag else ""
            if valid_img(src):
                self.log("LinkedIn image found")
                return [("LinkedIn", src)]
        return []

    def search_google(self, q):
        self.log("Google…")
        r = fetch(f"https://www.google.com/search?q={quote(q)}&tbm=isch&safe=off", self.session)
        return [("Google", u) for u in extract_imgs(r.text)] if r else []

    def search_duckduckgo(self, q):
        self.log("DuckDuckGo…")
        r = fetch("https://duckduckgo.com/html/", self.session, params={"q": q, "iax": "images", "ia": "images"})
        return [("DuckDuckGo", u) for u in extract_imgs(r.text)] if r else []

    def search_site(self, domain, label):
        self.log(f"{label}…")
        r = fetch(f"https://www.google.com/search?q=site:{domain}+{quote(self.name.get())}", self.session)
        if not r: return []
        soup = BeautifulSoup(r.text, 'html.parser')
        links = [a["href"] for a in soup.select("a[href]") if domain in a["href"]]
        for link in links[:3]:          # keep it quick
            rr = fetch(link, self.session)
            if rr and rr.status_code == 200:
                imgs = extract_imgs(rr.text)
                if imgs:
                    return [(label, imgs[0])]
        return []

    # --------------------------- download ---------------------------------- #
    def download(self, src_tuple, dest_dir):
        label, url = src_tuple
        if not self.running.get(): return 0
        r = fetch(url, self.session, stream=True)
        if not r or 'image' not in r.headers.get("content-type", ""): return 0

        ext = '.png' if 'png' in r.headers['content-type'] else '.gif' if 'gif' in r.headers['content-type'] else '.jpg'
        fname = f"{label}_{hashlib.md5(url.encode()).hexdigest()[:8]}{ext}"
        path = os.path.join(dest_dir, fname)

        with open(path, 'wb') as f:
            for chunk in r.iter_content(8192):
                if not self.running.get(): return 0
                f.write(chunk)

        if os.path.getsize(path) < 1024:  # toss tiny junk
            os.remove(path); return 0
        self.log(f"✓ {label}")
        return 1

    # --------------------------- utils ------------------------------------ #
    def log(self, msg):                             # timestamped log
        self.logbox.insert(tk.END, f"{time.strftime('%H:%M:%S')}  {msg}\n")
        self.logbox.see(tk.END)

    def done(self):
        self.running.set(False)
        self.prog.stop(); self.start_b["state"]="normal"; self.stop_b["state"]="disabled"

# ------------------------------ main --------------------------------------- #
if __name__ == "__main__":
    tk.Tk().withdraw()   # prevent initial flash on macOS
    root = tk.Tk()
    ScraperGUI(root)
    root.mainloop()

