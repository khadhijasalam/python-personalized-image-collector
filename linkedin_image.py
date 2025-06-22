import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import os
import time
import threading
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
import hashlib
import re
import json
from typing import List, Dict, Optional

class ModernProfileScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Modern Profile Image Scraper")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a0a')
        
        # Modern color scheme
        self.colors = {
            'bg': '#0a0a0a',
            'card': '#1a1a1a',
            'accent': '#00d4ff',
            'secondary': '#ff6b6b',
            'success': '#51cf66',
            'warning': '#ffd43b',
            'text': '#ffffff',
            'text_dim': '#a0a0a0',
            'button_hover': '#00b8e6'
        }
        
        self.setup_styles()
        self.setup_session()
        
        self.download_folder = "profile_images"
        self.is_scraping = False
        self.scraped_urls = set()
        
        self.create_widgets()
    
    def setup_styles(self):
        """Setup modern dark theme"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern styles
        self.style.configure('Modern.TLabelframe', 
                           background=self.colors['card'], 
                           foreground=self.colors['text'],
                           relief='flat', borderwidth=1)
        self.style.configure('Modern.TLabelframe.Label', 
                           background=self.colors['card'], 
                           foreground=self.colors['accent'], 
                           font=('SF Pro Display', 12, 'bold'))
        
        self.style.configure('Modern.TEntry', 
                           fieldbackground='#2a2a2a', 
                           foreground=self.colors['text'], 
                           borderwidth=0, relief='flat')
        
        self.style.configure('Accent.TButton', 
                           background=self.colors['accent'], 
                           foreground='#000000', 
                           font=('SF Pro Display', 10, 'bold'),
                           relief='flat', borderwidth=0)
        
        self.style.configure('Secondary.TButton', 
                           background=self.colors['secondary'], 
                           foreground='#ffffff', 
                           font=('SF Pro Display', 10, 'bold'),
                           relief='flat', borderwidth=0)
    
    def setup_session(self):
        """Initialize session with rotating user agents"""
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        self.session.headers.update({
            'User-Agent': self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'DNT': '1'
        })
    
    def create_widgets(self):
        """Create modern GUI"""
        # Main container with gradient effect
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header
        self.create_header(main_frame)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Advanced search section
        self.create_advanced_section(main_frame)
        
        # Controls
        self.create_controls(main_frame)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', 
                                      style='Modern.Horizontal.TProgressbar')
        self.progress.pack(pady=15, fill=tk.X)
        
        # Log
        self.create_log_section(main_frame)
        
        # Status
        self.create_status_bar()
    
    def create_header(self, parent):
        """Create modern header"""
        header = tk.Frame(parent, bg=self.colors['bg'])
        header.pack(fill=tk.X, pady=(0, 30))
        
        title = tk.Label(header, text="🔍 Profile Hunter", 
                        font=('SF Pro Display', 28, 'bold'),
                        bg=self.colors['bg'], fg=self.colors['accent'])
        title.pack(side=tk.LEFT)
        
        subtitle = tk.Label(header, text="AI-Powered Profile Image Discovery", 
                           font=('SF Pro Display', 12),
                           bg=self.colors['bg'], fg=self.colors['text_dim'])
        subtitle.pack(side=tk.LEFT, padx=(15, 0))
    
    def create_input_section(self, parent):
        """Create input section"""
        input_card = ttk.LabelFrame(parent, text="🎯 Target Information", 
                                   style='Modern.TLabelframe', padding="20")
        input_card.pack(fill=tk.X, pady=(0, 20))
        
        # Name input with modern styling
        name_frame = tk.Frame(input_card, bg=self.colors['card'])
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(name_frame, text="Full Name", 
                font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['accent']).pack(anchor=tk.W)
        
        self.name_entry = tk.Entry(name_frame, font=('SF Pro Display', 14),
                                  bg='#2a2a2a', fg=self.colors['text'],
                                  relief='flat', bd=10)
        self.name_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # Platform grid
        platform_frame = tk.Frame(input_card, bg=self.colors['card'])
        platform_frame.pack(fill=tk.X)
        
        platforms = [
            ("LinkedIn URL", "linkedin_entry"),
            ("Twitter/X Handle", "twitter_entry"),
            ("GitHub Username", "github_entry"),
            ("Personal Website", "website_entry")
        ]
        
        for i, (label, attr) in enumerate(platforms):
            row, col = i // 2, i % 2
            
            frame = tk.Frame(platform_frame, bg=self.colors['card'])
            frame.grid(row=row, column=col, sticky="ew", padx=(0, 10 if col == 0 else 0), pady=8)
            platform_frame.grid_columnconfigure(col, weight=1)
            
            tk.Label(frame, text=label, font=('SF Pro Display', 10, 'bold'),
                    bg=self.colors['card'], fg=self.colors['text_dim']).pack(anchor=tk.W)
            
            entry = tk.Entry(frame, font=('SF Pro Display', 11),
                           bg='#2a2a2a', fg=self.colors['text'], relief='flat', bd=5)
            entry.pack(fill=tk.X, pady=(3, 0), ipady=5)
            setattr(self, attr, entry)
    
    def create_advanced_section(self, parent):
        """Create advanced search section"""
        advanced_card = ttk.LabelFrame(parent, text="🚀 Advanced Search", 
                                     style='Modern.TLabelframe', padding="20")
        advanced_card.pack(fill=tk.X, pady=(0, 20))
        
        # Search URL input
        url_frame = tk.Frame(advanced_card, bg=self.colors['card'])
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(url_frame, text="Custom Search URL (LinkedIn/Medium/Substack search results)", 
                font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['accent']).pack(anchor=tk.W)
        
        self.search_url_entry = tk.Entry(url_frame, font=('SF Pro Display', 11),
                                        bg='#2a2a2a', fg=self.colors['text'], relief='flat', bd=5)
        self.search_url_entry.pack(fill=tk.X, pady=(5, 0), ipady=5)
        
        # Settings row
        settings_frame = tk.Frame(advanced_card, bg=self.colors['card'])
        settings_frame.pack(fill=tk.X)
        
        # Max images
        tk.Label(settings_frame, text="Max Images:", font=('SF Pro Display', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['text_dim']).pack(side=tk.LEFT)
        
        self.max_images_var = tk.StringVar(value="15")
        max_entry = tk.Entry(settings_frame, textvariable=self.max_images_var,
                           font=('SF Pro Display', 11), width=5,
                           bg='#2a2a2a', fg=self.colors['text'], relief='flat', bd=5)
        max_entry.pack(side=tk.LEFT, padx=(10, 30))
        
        # Folder selection
        tk.Label(settings_frame, text="📁", font=('SF Pro Display', 16),
                bg=self.colors['card'], fg=self.colors['accent']).pack(side=tk.LEFT)
        
        self.folder_var = tk.StringVar(value=self.download_folder)
        folder_entry = tk.Entry(settings_frame, textvariable=self.folder_var,
                               font=('SF Pro Display', 10), width=25,
                               bg='#2a2a2a', fg=self.colors['text'], relief='flat', bd=5)
        folder_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        browse_btn = tk.Button(settings_frame, text="Browse", 
                              command=self.browse_folder,
                              font=('SF Pro Display', 10, 'bold'),
                              bg=self.colors['accent'], fg='#000000',
                              relief='flat', bd=0, padx=15, pady=5)
        browse_btn.pack(side=tk.LEFT)
    
    def create_controls(self, parent):
        """Create control buttons"""
        controls_frame = tk.Frame(parent, bg=self.colors['bg'])
        controls_frame.pack(pady=20)
        
        # Start button
        self.start_btn = tk.Button(controls_frame, text="🚀 Start Hunt",
                                  command=self.start_scraping,
                                  font=('SF Pro Display', 14, 'bold'),
                                  bg=self.colors['accent'], fg='#000000',
                                  relief='flat', bd=0, padx=30, pady=12)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Stop button
        self.stop_btn = tk.Button(controls_frame, text="⏹️ Stop",
                                 command=self.stop_scraping,
                                 font=('SF Pro Display', 14, 'bold'),
                                 bg=self.colors['secondary'], fg='#ffffff',
                                 relief='flat', bd=0, padx=30, pady=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Open folder button
        open_btn = tk.Button(controls_frame, text="📂 Open Folder",
                            command=self.open_folder,
                            font=('SF Pro Display', 14, 'bold'),
                            bg=self.colors['success'], fg='#000000',
                            relief='flat', bd=0, padx=30, pady=12)
        open_btn.pack(side=tk.LEFT)
    
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = tk.Frame(parent, bg=self.colors['bg'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame, text="📋 Activity Log", 
                font=('SF Pro Display', 14, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, 
                                                 font=('SF Mono', 10),
                                                 bg='#1a1a1a', fg=self.colors['text'],
                                                 insertbackground=self.colors['accent'],
                                                 relief='flat', bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.log_text.tag_configure("success", foreground=self.colors['success'])
        self.log_text.tag_configure("error", foreground=self.colors['secondary'])
        self.log_text.tag_configure("warning", foreground=self.colors['warning'])
        self.log_text.tag_configure("info", foreground=self.colors['accent'])
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready to hunt 🎯")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg=self.colors['card'], fg=self.colors['text'],
                               font=('SF Pro Display', 10))
        status_label.pack(side=tk.LEFT, padx=15, pady=5)
    
    def log_message(self, message, level="info"):
        """Add message to log"""
        timestamp = time.strftime('%H:%M:%S')
        icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        
        if any(word in message.lower() for word in ['success', 'downloaded', 'found']):
            level = "success"
        elif any(word in message.lower() for word in ['error', 'failed']):
            level = "error"
        elif any(word in message.lower() for word in ['warning', 'skip']):
            level = "warning"
        
        formatted_message = f"{timestamp} {icons[level]} {message}\n"
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
            self.download_folder = folder
    
    def open_folder(self):
        """Open download folder"""
        if os.path.exists(self.download_folder):
            if os.name == 'nt':
                os.startfile(self.download_folder)
            else:
                os.system(f'open "{self.download_folder}"' if os.name == 'posix' else f'xdg-open "{self.download_folder}"')
    
    def start_scraping(self):
        """Start scraping process"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a person name.")
            return
        
        self.is_scraping = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set("🔍 Hunting in progress...")
        
        self.scraping_thread = threading.Thread(target=self.scrape_images, args=(name,))
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def stop_scraping(self):
        """Stop scraping"""
        self.is_scraping = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("⏹️ Hunt stopped")
        self.log_message("Hunt stopped by user", "warning")
    
    def scrape_images(self, person_name):
        """Main scraping logic"""
        try:
            self.download_folder = self.folder_var.get()
            os.makedirs(self.download_folder, exist_ok=True)
            
            max_images = int(self.max_images_var.get() or 15)
            self.scraped_urls.clear()
            
            self.log_message(f"Starting hunt for: {person_name}")
            self.log_message(f"Target: {max_images} images")
            
            all_images = []
            
            # 1. Scrape direct social media profiles
            platforms = self.get_platform_info()
            for platform, identifier in platforms.items():
                if not self.is_scraping or len(all_images) >= max_images:
                    break
                
                self.log_message(f"Scanning {platform}: {identifier}")
                
                try:
                    images = getattr(self, f'scrape_{platform}')(identifier)
                    if images:
                        all_images.extend(images)
                        self.log_message(f"Found {len(images)} from {platform}")
                except Exception as e:
                    self.log_message(f"{platform} error: {str(e)}", "error")
                
                time.sleep(0.5)
            
            # 2. Search custom URL if provided
            search_url = self.search_url_entry.get().strip()
            if self.is_scraping and search_url and len(all_images) < max_images:
                self.log_message("Scanning custom search URL...")
                try:
                    custom_images = self.scrape_search_results(search_url)
                    all_images.extend(custom_images)
                    if custom_images:
                        self.log_message(f"Found {len(custom_images)} from custom search")
                except Exception as e:
                    self.log_message(f"Custom URL error: {str(e)}", "error")
            
            # 3. Google Images search
            if self.is_scraping and len(all_images) < max_images:
                self.log_message("Searching Google Images...")
                try:
                    google_images = self.search_google_images(person_name, max_images - len(all_images))
                    all_images.extend(google_images)
                    if google_images:
                        self.log_message(f"Found {len(google_images)} from Google Images")
                except Exception as e:
                    self.log_message(f"Google search error: {str(e)}", "error")
            
            # 4. DuckDuckGo Images search
            if self.is_scraping and len(all_images) < max_images:
                self.log_message("Searching DuckDuckGo Images...")
                try:
                    ddg_images = self.search_duckduckgo_images(person_name, max_images - len(all_images))
                    all_images.extend(ddg_images)
                    if ddg_images:
                        self.log_message(f"Found {len(ddg_images)} from DuckDuckGo")
                except Exception as e:
                    self.log_message(f"DuckDuckGo error: {str(e)}", "error")
            
            # Download images
            downloaded = 0
            for i, img_info in enumerate(all_images[:max_images]):
                if not self.is_scraping:
                    break
                
                self.log_message(f"Downloading {i+1}/{len(all_images[:max_images])}: {img_info['source']}")
                if self.download_image(img_info, person_name):
                    downloaded += 1
            
            if self.is_scraping:
                self.log_message(f"Hunt completed! Downloaded {downloaded} images.")
                self.status_var.set(f"✅ Hunt complete - {downloaded} images")
                
        except Exception as e:
            self.log_message(f"Hunt error: {str(e)}", "error")
        
        finally:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress.stop()
            if self.is_scraping:
                self.status_var.set("Ready to hunt 🎯")
    
    def get_platform_info(self):
        """Get platform information from entries"""
        platforms = {}
        entries = {
            'linkedin': self.linkedin_entry,
            'twitter': self.twitter_entry,
            'github': self.github_entry,
            'website': self.website_entry
        }
        
        for platform, entry in entries.items():
            value = entry.get().strip()
            if value:
                platforms[platform] = value
        
        return platforms
    
    def scrape_linkedin(self, profile_url):
        """Enhanced LinkedIn scraping"""
        images = []
        try:
            if not profile_url.startswith('http'):
                profile_url = f"https://linkedin.com/in/{profile_url}"
            
            response = self.session.get(profile_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Multiple selectors for LinkedIn images
                selectors = [
                    'meta[property="og:image"]',
                    'img[data-delayed-url*="profile-displayphoto"]',
                    '.profile-photo img',
                    '.pv-top-card__photo img'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    for el in elements:
                        img_url = el.get('content') or el.get('src') or el.get('data-delayed-url')
                        if img_url and 'media.licdn.com' in img_url and img_url not in self.scraped_urls:
                            self.scraped_urls.add(img_url)
                            images.append({
                                'url': img_url,
                                'source': 'LinkedIn',
                                'platform': 'linkedin'
                            })
        except Exception as e:
            self.log_message(f"LinkedIn error: {str(e)}", "error")
        
        return images
    
    def scrape_twitter(self, identifier):
        """Enhanced Twitter scraping"""
        images = []
        username = identifier.replace('@', '').split('/')[-1]
        
        try:
            for domain in ['x.com', 'twitter.com']:
                url = f"https://{domain}/{username}"
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Multiple selectors for Twitter images
                    selectors = [
                        'meta[property="og:image"]',
                        'img[src*="pbs.twimg.com/profile_images"]',
                        'img[src*="profile_images"]'
                    ]
                    
                    for selector in selectors:
                        elements = soup.select(selector)
                        for el in elements:
                            img_url = el.get('content') or el.get('src')
                            if img_url and 'pbs.twimg.com' in img_url and img_url not in self.scraped_urls:
                                # Get higher quality version
                                img_url = img_url.replace('_normal', '_400x400').replace('_bigger', '_400x400')
                                self.scraped_urls.add(img_url)
                                images.append({
                                    'url': img_url,
                                    'source': f'Twitter-{username}',
                                    'platform': 'twitter'
                                })
                    break
        except Exception as e:
            self.log_message(f"Twitter error: {str(e)}", "error")
        
        return images
    
    def scrape_github(self, identifier):
        """Enhanced GitHub scraping"""
        images = []
        username = identifier.split('/')[-1]
        
        try:
            # Try API first
            api_url = f"https://api.github.com/users/{username}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                avatar_url = data.get('avatar_url')
                if avatar_url and avatar_url not in self.scraped_urls:
                    self.scraped_urls.add(avatar_url)
                    images.append({
                        'url': avatar_url + '?s=400',
                        'source': f'GitHub-{username}',
                        'platform': 'github'
                    })
        except Exception as e:
            self.log_message(f"GitHub error: {str(e)}", "error")
        
        return images
    
    def scrape_website(self, url):
        """Enhanced website scraping"""
        images = []
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                selectors = [
                    'meta[property="og:image"]',
                    'img[alt*="profile" i]',
                    'img[class*="avatar" i]',
                    'img[class*="profile" i]',
                    '.profile img',
                    '.avatar img'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    for el in elements:
                        img_url = el.get('content') or el.get('src')
                        if img_url:
                            if not img_url.startswith('http'):
                                img_url = urljoin(url, img_url)
                            
                            if img_url not in self.scraped_urls:
                                self.scraped_urls.add(img_url)
                                images.append({
                                    'url': img_url,
                                    'source': f'Website-{urlparse(url).netloc}',
                                    'platform': 'website'
                                })
        except Exception as e:
            self.log_message(f"Website error: {str(e)}", "error")
        
        return images
    
    def scrape_search_results(self, search_url):
        """Scrape images from search results page"""
        images = []
        try:
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic selectors for profile images in search results
                selectors = [
                    'img[src*="profile"]',
                    'img[src*="avatar"]',
                    'img[alt*="profile" i]',
                    'img[class*="profile" i]',
                    'img[class*="avatar" i]'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    for el in elements[:5]:  # Limit to avoid too many images
                        img_url = el.get('src')
                        if img_url and img_url not in self.scraped_urls:
                            if not img_url.startswith('http'):
                                img_url = urljoin(search_url, img_url)
                            
                            self.scraped_urls.add(img_url)
                            images.append({
                                'url': img_url,
                                'source': 'Search Results',
                                'platform': 'search'
                            })
        except Exception as e:
            self.log_message(f"Search results error: {str(e)}", "error")
        
        return images
    
    def search_google_images(self, person_name, max_results):
        """Search Google Images"""
        images = []
        try:
            query = f"{person_name} profile picture"
            search_url = f"https://www.google.com/search?q={quote(query)}&tbm=isch"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extract image URLs from Google Images
                img_urls = re.findall(r'"ou":"([^"]+)"', response.text)
                
                for img_url in img_urls[:max_results]:
                    if img_url not in self.scraped_urls:
                        self.scraped_urls.add(img_url)
                        images.append({
                            'url': img_url,
                            'source': 'Google Images',
                            'platform': 'google'
                        })
        except Exception as e:
            self.log_message(f"Google Images error: {str(e)}", "error")
        
        return images
    
    def search_duckduckgo_images(self, person_name, max_results):
        """Search DuckDuckGo Images"""
        images = []
        try:
            query = f"{person_name} profile picture"
            search_url = f"https://duckduckgo.com/?q={quote(query)}&t=h_&iax=images&ia=images"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extract image URLs from DuckDuckGo
                soup = BeautifulSoup(response.content, 'html.parser')
                img_elements = soup.select('img[src]')
                
                for img in img_elements[:max_results]:
                    img_url = img.get('src')
                    if img_url and img_url.startswith('http') and img_url not in self.scraped_urls:
                        self.scraped_urls.add(img_url)
                        images.append({
                            'url': img_url,
                            'source': 'DuckDuckGo Images',
                            'platform': 'duckduckgo'
                        })
        except Exception as e:
            self.log_message(f"DuckDuckGo Images error: {str(e)}", "error")
        
        return images
    
    def download_image(self, img_info, person_name):
        """Download individual image with enhanced error handling"""
        try:
            img_url = img_info['url']
            source = img_info['source']
            platform = img_info.get('platform', 'unknown')
            
            # Create safe filename
            safe_name = re.sub(r'[^\w\s-]', '', person_name)
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            
            # Generate unique filename
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            
            # Determine file extension
            response = self.session.head(img_url, timeout=10)
            content_type = response.headers.get('content-type', '')
            
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                # Try to guess from URL
                if '.jpg' in img_url.lower() or '.jpeg' in img_url.lower():
                    ext = '.jpg'
                elif '.png' in img_url.lower():
                    ext = '.png'
                elif '.gif' in img_url.lower():
                    ext = '.gif'
                elif '.webp' in img_url.lower():
                    ext = '.webp'
                else:
                    ext = '.jpg'  # Default
            
            filename = f"{safe_name}_{platform}_{url_hash}_{timestamp}{ext}"
            filepath = os.path.join(self.download_folder, filename)
            
            # Download image
            response = self.session.get(img_url, timeout=20, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            if not response.headers.get('content-type', '').startswith('image/'):
                self.log_message(f"Skipped non-image: {source}", "warning")
                return False
            
            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file size
            if os.path.getsize(filepath) < 1024:  # Less than 1KB
                os.remove(filepath)
                self.log_message(f"Removed tiny file from {source}", "warning")
                return False
            
            self.log_message(f"✅ Downloaded: {filename} from {source}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_message(f"Download failed from {img_info['source']}: {str(e)}", "error")
            return False
        except Exception as e:
            self.log_message(f"Unexpected error downloading from {img_info['source']}: {str(e)}", "error")
            return False
    
    def validate_inputs(self):
        """Validate user inputs"""
        name = self.name_entry.get().strip()
        if not name:
            return False, "Please enter a person name."
        
        try:
            max_images = int(self.max_images_var.get())
            if max_images <= 0 or max_images > 100:
                return False, "Max images must be between 1 and 100."
        except ValueError:
            return False, "Max images must be a valid number."
        
        return True, ""
    
    def export_results(self):
        """Export results to JSON"""
        try:
            results = {
                'person_name': self.name_entry.get().strip(),
                'download_folder': self.download_folder,
                'total_images': len([f for f in os.listdir(self.download_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]),
                'scraped_urls': list(self.scraped_urls),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            json_path = os.path.join(self.download_folder, 'scraping_results.json')
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.log_message(f"Results exported to: {json_path}")
            
        except Exception as e:
            self.log_message(f"Export error: {str(e)}", "error")
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def save_log(self):
        """Save log to file"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            log_filename = f"scraping_log_{timestamp}.txt"
            log_path = os.path.join(self.download_folder, log_filename)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            self.log_message(f"Log saved: {log_filename}")
            
        except Exception as e:
            self.log_message(f"Save log error: {str(e)}", "error")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_scraping:
            if messagebox.askokcancel("Quit", "Scraping is in progress. Do you want to quit?"):
                self.is_scraping = False
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        # You can add an icon file here if you have one
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    # Create the application
    app = ModernProfileScraper(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()