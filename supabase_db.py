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

def get_site_content(key):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/site_content?key=eq.{key}&select=value", headers=HEADERS, timeout=10)
        data = r.json()
        return data[0]['value'] if data else None
    except Exception as e:
        print("❌ Error in get_site_content:", e)
        return None


def add_site_content(key, value):
    """Insert row if missing (used during app init)."""
    data = {"key": key, "value": value}
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/site_content", headers=HEADERS, data=json.dumps(data), timeout=10)
        print("🔹 add_site_content ->", r.status_code, r.text)
        return r.status_code in (201, 200)
    except Exception as e:
        print("❌ Error in add_site_content:", e)
        return False


def update_site_content(key, value):
    data = {"value": value}
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/site_content?key=eq.{key}", headers=HEADERS, data=json.dumps(data), timeout=10)
        print("🔹 update_site_content ->", r.status_code, r.text)
        # supabase returns 204 on success for patch
        return r.status_code in (204, 200)
    except Exception as e:
        print("❌ Error in update_site_content:", e)
        return False