import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import os
import time
import threading
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
import hashlib
from PIL import Image, ImageTk
import io
import re

class EnhancedProfileImageScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Profile Image Scraper")
        self.root.geometry("900x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize scraper session with better headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.download_folder = "profile_images"
        self.is_scraping = False
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Enhanced Profile Image Scraper", 
                              font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Person name input
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(name_frame, text="Person Name:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.name_entry = ttk.Entry(name_frame, font=('Arial', 11), width=50)
        self.name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Platforms frame - Enhanced
        platforms_frame = ttk.LabelFrame(main_frame, text="Platform Information (Optional)", padding="10")
        platforms_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create a scrollable frame for platforms
        canvas = tk.Canvas(platforms_frame, height=200)
        scrollbar = ttk.Scrollbar(platforms_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Twitter/X
        twitter_frame = ttk.Frame(scrollable_frame)
        twitter_frame.pack(fill=tk.X, pady=2)
        ttk.Label(twitter_frame, text="Twitter/X:", width=15).pack(side=tk.LEFT)
        self.twitter_entry = ttk.Entry(twitter_frame, width=35)
        self.twitter_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # GitHub
        github_frame = ttk.Frame(scrollable_frame)
        github_frame.pack(fill=tk.X, pady=2)
        ttk.Label(github_frame, text="GitHub:", width=15).pack(side=tk.LEFT)
        self.github_entry = ttk.Entry(github_frame, width=35)
        self.github_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # LinkedIn
        linkedin_frame = ttk.Frame(scrollable_frame)
        linkedin_frame.pack(fill=tk.X, pady=2)
        ttk.Label(linkedin_frame, text="LinkedIn URL:", width=15).pack(side=tk.LEFT)
        self.linkedin_entry = ttk.Entry(linkedin_frame, width=35)
        self.linkedin_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Substack
        substack_frame = ttk.Frame(scrollable_frame)
        substack_frame.pack(fill=tk.X, pady=2)
        ttk.Label(substack_frame, text="Substack:", width=15).pack(side=tk.LEFT)
        self.substack_entry = ttk.Entry(substack_frame, width=35)
        self.substack_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(substack_frame, text="(username or full URL)", font=('Arial', 8)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Medium
        medium_frame = ttk.Frame(scrollable_frame)
        medium_frame.pack(fill=tk.X, pady=2)
        ttk.Label(medium_frame, text="Medium:", width=15).pack(side=tk.LEFT)
        self.medium_entry = ttk.Entry(medium_frame, width=35)
        self.medium_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(medium_frame, text="(@username or full URL)", font=('Arial', 8)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Personal Website
        website_frame = ttk.Frame(scrollable_frame)
        website_frame.pack(fill=tk.X, pady=2)
        ttk.Label(website_frame, text="Website URL:", width=15).pack(side=tk.LEFT)
        self.website_entry = ttk.Entry(website_frame, width=35)
        self.website_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Folder setting
        folder_frame = ttk.Frame(settings_frame)
        folder_frame.pack(fill=tk.X, pady=2)
        ttk.Label(folder_frame, text="Download Folder:", width=15).pack(side=tk.LEFT)
        self.folder_var = tk.StringVar(value=self.download_folder)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=30)
        self.folder_entry.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Max images setting
        max_frame = ttk.Frame(settings_frame)
        max_frame.pack(fill=tk.X, pady=2)
        ttk.Label(max_frame, text="Max Images:", width=15).pack(side=tk.LEFT)
        self.max_images_var = tk.StringVar(value="15")
        ttk.Entry(max_frame, textvariable=self.max_images_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Public only checkbox
        public_frame = ttk.Frame(settings_frame)
        public_frame.pack(fill=tk.X, pady=2)
        self.public_only_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(public_frame, text="Public profiles/posts only", 
                       variable=self.public_only_var).pack(side=tk.LEFT)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_button = ttk.Button(buttons_frame, text="Start Scraping", 
                                      command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop", 
                                     command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Open Folder", command=self.open_download_folder).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Scraping Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log area"""
        self.log_text.delete(1.0, tk.END)
    
    def browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
            self.download_folder = folder
    
    def open_download_folder(self):
        """Open the download folder in file explorer"""
        if os.path.exists(self.download_folder):
            if os.name == 'nt':  # Windows
                os.startfile(self.download_folder)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{self.download_folder}"')
        else:
            messagebox.showwarning("Folder Not Found", f"Folder '{self.download_folder}' does not exist.")
    
    def start_scraping(self):
        """Start the scraping process"""
        person_name = self.name_entry.get().strip()
        if not person_name:
            messagebox.showerror("Error", "Please enter a person name.")
            return
        
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set("Scraping in progress...")
        
        # Start scraping in a separate thread
        self.scraping_thread = threading.Thread(target=self.scrape_images, args=(person_name,))
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Scraping stopped")
        self.log_message("Scraping stopped by user")
    
    def scrape_images(self, person_name):
        """Main scraping method (runs in separate thread)"""
        try:
            self.download_folder = self.folder_var.get()
            os.makedirs(self.download_folder, exist_ok=True)
            
            # Collect platform info
            platforms = {}
            if self.twitter_entry.get().strip():
                platforms['twitter'] = self.twitter_entry.get().strip()
            if self.github_entry.get().strip():
                platforms['github'] = self.github_entry.get().strip()
            if self.linkedin_entry.get().strip():
                platforms['linkedin'] = self.linkedin_entry.get().strip()
            if self.substack_entry.get().strip():
                platforms['substack'] = self.substack_entry.get().strip()
            if self.medium_entry.get().strip():
                platforms['medium'] = self.medium_entry.get().strip()
            if self.website_entry.get().strip():
                platforms['website'] = self.website_entry.get().strip()
            
            max_images = int(self.max_images_var.get() or 15)
            
            self.log_message(f"Starting enhanced scrape for: {person_name}")
            self.log_message(f"Max images: {max_images}")
            if self.public_only_var.get():
                self.log_message("Mode: Public profiles/posts only")
            
            all_images = []
            
            # Check specific platforms
            for platform, identifier in platforms.items():
                if not self.is_scraping:
                    break
                
                self.log_message(f"Checking {platform}: {identifier}")
                
                try:
                    if platform == 'twitter':
                        img = self.scrape_twitter_profile(identifier)
                    elif platform == 'github':
                        img = self.scrape_github_profile(identifier)
                    elif platform == 'linkedin':
                        img = self.scrape_linkedin_profile(identifier)
                    elif platform == 'substack':
                        img = self.scrape_substack_profile(identifier)
                    elif platform == 'medium':
                        img = self.scrape_medium_profile(identifier)
                    elif platform == 'website':
                        img = self.scrape_website_profile(identifier, person_name)
                    
                    if img:
                        all_images.append(img)
                        self.log_message(f"✓ Found image from {platform}")
                    else:
                        self.log_message(f"✗ No image found from {platform}")
                        
                except Exception as e:
                    self.log_message(f"✗ Error with {platform}: {str(e)}")
                
                time.sleep(1)  # Rate limiting
            
            # Search general sources if we need more images
            if self.is_scraping and len(all_images) < max_images:
                self.log_message("Searching general sources...")
                
                # Search Google Images
                google_images = self.search_google_images(person_name, max_images - len(all_images))
                all_images.extend(google_images)
                
                # Search alternative sources
                if len(all_images) < max_images:
                    alt_images = self.search_alternative_sources(person_name, max_images - len(all_images))
                    all_images.extend(alt_images)
            
            # Validate and filter images
            self.log_message(f"Validating {len(all_images)} found images...")
            valid_images = []
            for img in all_images:
                if not self.is_scraping:
                    break
                if self.validate_image_url(img['url']):
                    valid_images.append(img)
                    self.log_message(f"✓ Valid: {img['source']}")
                else:
                    self.log_message(f"✗ Invalid: {img['source']}")
            
            # Download images
            downloaded_count = 0
            for i, img_info in enumerate(valid_images[:max_images]):
                if not self.is_scraping:
                    break
                
                self.log_message(f"Downloading {i+1}/{len(valid_images)}: {img_info['source']}")
                filepath = self.download_image(img_info, person_name)
                if filepath:
                    downloaded_count += 1
                    self.log_message(f"✓ Saved: {os.path.basename(filepath)}")
                else:
                    self.log_message(f"✗ Failed: {img_info['source']}")
            
            if self.is_scraping:
                self.log_message(f"Scraping completed! Downloaded {downloaded_count} images.")
                self.status_var.set(f"Completed - {downloaded_count} images downloaded")
                messagebox.showinfo("Complete", f"Successfully downloaded {downloaded_count} images!")
            
        except Exception as e:
            self.log_message(f"Error during scraping: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress.stop()
            if self.is_scraping:
                self.status_var.set("Ready")
    
    def scrape_twitter_profile(self, username: str) -> Optional[Dict]:
        """Get Twitter/X profile image - public profiles only"""
        try:
            # Clean username
            if username.startswith('@'):
                username = username[1:]
            if username.startswith('http'):
                username = username.split('/')[-1]
            
            # Use Nitter or other Twitter alternatives for public data
            profile_url = f"https://twitter.com/{username}"
            
            self.log_message(f"Accessing Twitter: {profile_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = self.session.get(profile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for og:image
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img_url = og_image.get('content')
                    if 'pbs.twimg.com' in img_url:
                        return {
                            'url': img_url,
                            'source': 'Twitter (Meta)',
                            'profile_url': profile_url,
                            'method': 'og_image'
                        }
                
                # Look for profile images
                profile_selectors = [
                    'img[src*="pbs.twimg.com"]',
                    'img[alt*="profile"]',
                    '.profile-picture img'
                ]
                
                for selector in profile_selectors:
                    img_element = soup.select_one(selector)
                    if img_element and img_element.get('src'):
                        img_url = img_element.get('src')
                        if 'pbs.twimg.com' in img_url and 'profile_images' in img_url:
                            return {
                                'url': img_url,
                                'source': 'Twitter (Profile)',
                                'profile_url': profile_url,
                                'method': 'profile_img'
                            }
            
        except Exception as e:
            self.log_message(f"Error scraping Twitter: {e}")
        
        return None
    
    def scrape_github_profile(self, username: str) -> Optional[Dict]:
        """Get GitHub profile image"""
        try:
            # Clean username
            if username.startswith('http'):
                username = username.split('/')[-1]
            
            profile_url = f"https://github.com/{username}"
            
            self.log_message(f"Accessing GitHub: {profile_url}")
            
            response = self.session.get(profile_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # GitHub avatar
                avatar_selectors = [
                    'img[alt*="avatar"]',
                    '.avatar img',
                    'img[src*="githubusercontent.com"]'
                ]
                
                for selector in avatar_selectors:
                    img_element = soup.select_one(selector)
                    if img_element and img_element.get('src'):
                        img_url = img_element.get('src')
                        if 'githubusercontent.com' in img_url:
                            return {
                                'url': img_url,
                                'source': 'GitHub',
                                'profile_url': profile_url,
                                'method': 'avatar'
                            }
            
        except Exception as e:
            self.log_message(f"Error scraping GitHub: {e}")
        
        return None
    
    def scrape_linkedin_profile(self, profile_url: str) -> Optional[Dict]:
        """Enhanced LinkedIn profile scraping - public profiles only"""
        try:
            if not profile_url.startswith('http'):
                profile_url = f"https://www.linkedin.com/in/{profile_url}"
            
            # Use browser-like headers to avoid detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            response = self.session.get(profile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Method 1: og:image meta tag
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img_url = og_image.get('content')
                    if 'licdn.com' in img_url:
                        return {
                            'url': img_url,
                            'source': 'LinkedIn (Meta)',
                            'profile_url': profile_url,
                            'method': 'og_image'
                        }
                
                # Method 2: Look for profile image elements
                profile_selectors = [
                    'img[src*="licdn.com"]',
                    '.profile-photo img',
                    '.presence-entity__image img',
                    'img[alt*="profile"]',
                    'img[data-delayed-url*="licdn.com"]'
                ]
                
                for selector in profile_selectors:
                    img_element = soup.select_one(selector)
                    if img_element:
                        img_url = img_element.get('src') or img_element.get('data-delayed-url')
                        if img_url and 'licdn.com' in img_url:
                            return {
                                'url': img_url,
                                'source': 'LinkedIn (Profile)',
                                'profile_url': profile_url,
                                'method': 'profile_img'
                            }
            
        except Exception as e:
            self.log_message(f"Error scraping LinkedIn: {e}")
        
        return None
    
    def scrape_substack_profile(self, identifier: str) -> Optional[Dict]:
        """Get Substack profile image - only from public profiles"""
        try:
            # Handle both username and full URLs
            if identifier.startswith('http'):
                profile_url = identifier
            else:
                # Try common Substack URL patterns
                if '.' in identifier and 'substack.com' in identifier:
                    profile_url = f"https://{identifier}"
                else:
                    profile_url = f"https://{identifier}.substack.com"
            
            self.log_message(f"Accessing Substack: {profile_url}")
            
            # Use headers that look like a regular browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = self.session.get(profile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Method 1: Look for author image in meta tags
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img_url = og_image.get('content')
                    if 'substackcdn.com' in img_url:
                        return {
                            'url': img_url,
                            'source': 'Substack (Meta)',
                            'profile_url': profile_url,
                            'method': 'og_image'
                        }
                
                # Method 2: Look for profile images in the page
                profile_selectors = [
                    'img[src*="substackcdn.com"]',
                    '.profile-img img',
                    '.author-photo img',
                    'img[alt*="profile"]',
                    'img[alt*="author"]'
                ]
                
                for selector in profile_selectors:
                    img_element = soup.select_one(selector)
                    if img_element and img_element.get('src'):
                        img_url = img_element.get('src')
                        if 'substackcdn.com' in img_url and 'profile' in img_url.lower():
                            return {
                                'url': img_url,
                                'source': 'Substack (Profile)',
                                'profile_url': profile_url,
                                'method': 'profile_img'
                            }
                
                # Method 3: Look in JSON-LD structured data
                json_scripts = soup.find_all('script', type='application/ld+json')
                for script in json_scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and 'author' in data:
                            author = data['author']
                            if isinstance(author, dict) and 'image' in author:
                                return {
                                    'url': author['image'],
                                    'source': 'Substack (JSON-LD)',
                                    'profile_url': profile_url,
                                    'method': 'json_ld'
                                }
                    except:
                        continue
                        
            else:
                self.log_message(f"Substack access failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_message(f"Error scraping Substack: {e}")
        
        return None
    
    def scrape_medium_profile(self, identifier: str) -> Optional[Dict]:
        """Get Medium profile image - only from public profiles"""
        try:
            # Handle both @username and full URLs
            if identifier.startswith('http'):
                profile_url = identifier
            elif identifier.startswith('@'):
                profile_url = f"https://medium.com/{identifier}"
            else:
                # Add @ if not present
                username = identifier if identifier.startswith('@') else f"@{identifier}"
                profile_url = f"https://medium.com/{username}"
            
            self.log_message(f"Accessing Medium: {profile_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = self.session.get(profile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Method 1: Look for og:image
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img_url = og_image.get('content')
                    if 'miro.medium.com' in img_url:
                        return {
                            'url': img_url,
                            'source': 'Medium (Meta)',
                            'profile_url': profile_url,
                            'method': 'og_image'
                        }

                # Method 2: Look for profile images in the page
                profile_selectors = [
                    'img[src*="miro.medium.com"]',
                    '.avatar-image',
                    'img[alt*="profile"]'
                ]
                for selector in profile_selectors:
                    img_element = soup.select_one(selector)
                    if img_element and img_element.get('src'):
                        img_url = img_element.get('src')
                        if 'miro.medium.com' in img_url:
                            return {
                                'url': img_url,
                                'source': 'Medium (Profile)',
                                'profile_url': profile_url,
                                'method': 'profile_img'
                            }
        except Exception as e:
            self.log_message(f"Error scraping Medium: {e}")