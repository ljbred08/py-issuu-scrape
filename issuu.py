from bs4 import BeautifulSoup
import wget
import os
import urllib.request
import glob
from PIL import Image  # pip install pillow

# --- INPUT ---
url = input("Enter the url: ")
howmanypages = int(input("How many pages? "))

# --- FETCH PAGE ONCE ---
webpage = urllib.request.urlopen(url)
soup = BeautifulSoup(webpage, 'html.parser')

# Get title & image link pattern
pagetitle = soup.find('meta', attrs={'property': 'og:title'})['content']
print(f"Document Title: {pagetitle}")

imglink3 = soup.find('meta', attrs={'property': 'og:image'})['content']
imglink2 = imglink3.replace('1_social_preview.jpg', '')

# Make folder for pages
os.makedirs("pages", exist_ok=True)

# --- DOWNLOAD ALL PAGES ---
for page in range(1, howmanypages + 1):
    imglink = f"{imglink2}{page}_social_preview.jpg"
    filename = f"pages/page_{page}.jpg"
    wget.download(imglink, filename)
    print(f"\nPage {page} downloaded from {imglink}")

    with open('urls.txt', 'a') as f:
        f.write(imglink + '\n')

# --- MERGE INTO PDF ---
image_files = sorted(glob.glob("pages/page_*.jpg"))
images = [Image.open(img).convert("RGB") for img in image_files]

if images:
    pdf_path = f"{pagetitle}.pdf"
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"\nPDF saved as: {pdf_path}")

# --- METADATA ---
def safe_meta(property_name):
    tag = soup.find('meta', attrs={'property': property_name})
    return tag['content'] if tag and 'content' in tag.attrs else "N/A"

def safe_div(itemprop_name, attr):
    tag = soup.find('div', attrs={'itemprop': itemprop_name})
    return tag[attr] if tag and attr in tag.attrs else "N/A"

def safe_uploader_link():
    div_tag = soup.find('div', attrs={'class': 'PublisherInfo__name--3j27Y'})
    return "https://issuu.com" + div_tag.a['href'] if div_tag and div_tag.a else "N/A"

def safe_uploader():
    tag = soup.find('a', attrs={'itemprop': 'author'})
    return tag.contents[0] if tag and tag.contents else "N/A"

metadata = {
    'URL': url,
    'description': safe_meta('og:description'),
    'uploaded': safe_div('datePublished', 'datetime'),
    'uploader_link': safe_uploader_link(),
    'uploader': safe_uploader()
}


metadata_out = '\n'.join(f"{k}: {v}" for k, v in metadata.items())
print("\nMetadata:\n", metadata_out)

with open('info.txt', 'w') as f:
    f.write(metadata_out)

# --- CLEANUP ---
for f in image_files:
    os.remove(f)
print("\nAll temporary images deleted.")
