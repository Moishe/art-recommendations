import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def pick_largest_image(img_tags, base_url):
    """
    Attempt to pick the largest image based on the width and height attributes in HTML.
    (Note: many sites don't provide width/height in the HTML, so further HEAD requests might be required.)
    """
    best_img = None
    best_area = 0

    for img in img_tags:
        src = img.get("src")
        if not src:
            continue

        width = 0
        height = 0

        # Some images specify width/height as attributes
        try:
            width = int(img.get("width", 0))
            height = int(img.get("height", 0))
        except ValueError:
            # If the attribute is non-numeric, ignore
            pass

        area = width * height
        if area > best_area:
            best_area = area
            best_img = src

    if best_img:
        return urljoin(base_url, best_img)
    return None

def get_representative_image(page_url):
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Check OG, Twitter, link rel, etc. (same as before)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return urljoin(page_url, og_image["content"])

        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return urljoin(page_url, twitter_image["content"])

        link_image = soup.find("link", rel="image_src")
        if link_image and link_image.get("href"):
            return urljoin(page_url, link_image["href"])

        # Fallback scan for all <img>
        img_tags = soup.find_all("img")
        if not img_tags:
            return None

        return pick_largest_image(img_tags, page_url)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {page_url}: {e}")
        return None
