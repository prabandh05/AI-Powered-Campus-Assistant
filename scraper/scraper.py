import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
import time
import os

class CampusScraper:
    def __init__(self, base_url, max_pages=50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited = set()
        self.base_domain = urlparse(base_url).netloc
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain and \
               not parsed.path.endswith(('.pdf', '.jpg', '.png', '.jpeg', '.gif'))

    def clean_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def crawl(self):
        queue = deque([self.base_url])
        all_text = []
        
        print(f"Starting crawl of {self.base_url}...")
        
        while queue and len(self.visited) < self.max_pages:
            url, _ = urldefrag(queue.popleft())
            if url in self.visited:
                continue
            
            self.visited.add(url)
            print(f"Scraping [{len(self.visited)}/{self.max_pages}]: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    continue
                
                text = self.clean_text(response.text)
                all_text.append(f"Source: {url}\n{text}")
                
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    full_url = urljoin(url, link['href'])
                    full_url, _ = urldefrag(full_url)
                    if self.is_valid_url(full_url) and full_url not in self.visited:
                        queue.append(full_url)
                
                time.sleep(0.5) # Be polite
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        output_path = os.path.join(self.data_dir, "campus_knowledge.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n" + "="*50 + "\n\n".join(all_text))
        
        print(f"Crawl complete. Saved to {output_path}")
        return output_path

if __name__ == "__main__":
    scraper = CampusScraper("https://www.dsce.edu.in", max_pages=10) # 10 pages for testing
    scraper.crawl()
