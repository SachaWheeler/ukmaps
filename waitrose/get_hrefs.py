from bs4 import BeautifulSoup

# --- Path to your HTML file ---
html_file = "index.html"

# --- Read the file ---
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# --- Extract all hrefs ---
hrefs = []
for a in soup.find_all("a", href=True):
    hrefs.append(a["href"])

# --- Output the links ---
for link in hrefs:
    print(link)

