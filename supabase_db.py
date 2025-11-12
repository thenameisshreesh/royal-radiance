import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY, HEADERS

BUCKET = "uploads"

def upload_to_supabase_storage(filename, file_bytes, content_type):
    """Upload file bytes to Supabase Storage under profile_images/ and return public URL"""
    # ✅ Store in a folder inside the bucket
    path = f"profile_images/{filename}"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": content_type,
        "x-upsert": "true"  # ✅ allows overwrite if file exists
    }

    res = requests.post(url, headers=headers, data=file_bytes)

    if res.status_code == 409:
        print("⚠️ File already exists in storage, skipping upload.")

    if res.status_code in (200, 201, 409):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"
        return public_url
    else:
        print("❌ Upload failed:", res.status_code, res.text)
        return None


# ---------- PRODUCTS ----------
def get_all_products():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/products?select=*", headers=HEADERS, timeout=10)
        return r.json() if r.status_code in (200, 206) else []
    except Exception as e:
        print("❌ Error fetching products:", e)
        return []


def add_product(name, short_desc, price, image_url):
    data = {"name": name, "short_desc": short_desc, "price": price, "image": image_url}
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, data=json.dumps(data))
        return r.status_code in (200, 201)
    except Exception as e:
        print("❌ Error adding product:", e)
        return False


def delete_product(pid):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}", headers=HEADERS)
        return r.status_code in (200, 204)
    except Exception as e:
        print("❌ Error deleting product:", e)
        return False


# ---------- BLOGS ----------
def get_all_blogs():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/blog_posts?select=*", headers=HEADERS, timeout=10)
        return r.json() if r.status_code in (200, 206) else []
    except Exception as e:
        print("❌ Error fetching blogs:", e)
        return []


def add_blog(title, excerpt, content, image_url):
    data = {"title": title, "excerpt": excerpt, "content": content, "image": image_url}
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/blog_posts", headers=HEADERS, data=json.dumps(data))
        return r.status_code in (200, 201)
    except Exception as e:
        print("❌ Error adding blog:", e)
        return False


def delete_blog(bid):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/blog_posts?id=eq.{bid}", headers=HEADERS)
        return r.status_code in (200, 204)
    except Exception as e:
        print("❌ Error deleting blog:", e)
        return False
