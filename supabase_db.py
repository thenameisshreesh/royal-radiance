import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY, HEADERS, SUPABASE_STORAGE_URL, SUPABASE_BUCKET

# ---------- PRODUCTS ----------
def get_all_products():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/products?select=*", headers=HEADERS, timeout=10)
        return r.json() if r.status_code in (200, 206) else []
    except Exception as e:
        print("❌ Error fetching products:", e)
        return []

def add_product(name, short_desc, price, image):
    """
    image is expected to be a full URL (public URL) or filename (legacy).
    """
    data = {"name": name, "short_desc": short_desc, "price": price, "image": image}
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, data=json.dumps(data), timeout=10)
        print("🔹 add_product ->", r.status_code, r.text)
        return r.status_code in (201, 200)
    except Exception as e:
        print("❌ Error in add_product:", e)
        return False

def delete_product(pid):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}", headers=HEADERS, timeout=10)
        print("🔹 delete_product ->", r.status_code, r.text)
        return r.status_code in (200, 204)
    except Exception as e:
        print("❌ Error in delete_product:", e)
        return False

# ---------- BLOGS ----------
def get_all_blogs():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/blog_posts?select=*", headers=HEADERS, timeout=10)
        return r.json() if r.status_code in (200, 206) else []
    except Exception as e:
        print("❌ Error fetching blogs:", e)
        return []

def add_blog(title, excerpt, content, image):
    data = {"title": title, "excerpt": excerpt, "content": content, "image": image}
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/blog_posts", headers=HEADERS, data=json.dumps(data), timeout=10)
        print("🔹 add_blog ->", r.status_code, r.text)
        return r.status_code in (201, 200)
    except Exception as e:
        print("❌ Error in add_blog:", e)
        return False

def delete_blog(bid):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/blog_posts?id=eq.{bid}", headers=HEADERS, timeout=10)
        print("🔹 delete_blog ->", r.status_code, r.text)
        return r.status_code in (200, 204)
    except Exception as e:
        print("❌ Error in delete_blog:", e)
        return False

# ---------- SITE CONTENT ----------
def get_site_content(key):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/site_content?key=eq.{key}&select=value", headers=HEADERS, timeout=10)
        data = r.json()
        return data[0]['value'] if data else None
    except Exception as e:
        print("❌ Error in get_site_content:", e)
        return None

def add_site_content(key, value):
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
        return r.status_code in (204, 200)
    except Exception as e:
        print("❌ Error in update_site_content:", e)
        return False

# ---------- SUPABASE STORAGE HELPERS ----------
def upload_to_supabase_storage(file_obj, filename):
    """Upload file to Supabase Storage bucket and return public URL."""
    try:
        url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
        }
        files = {"file": (filename, file_obj.stream, file_obj.mimetype)}
        res = requests.post(url, headers=headers, files=files)
        if res.status_code in (200, 201):
            return f"{SUPABASE_STORAGE_URL}/{filename}"
        else:
            print("⚠️ upload_to_supabase_storage failed:", res.status_code, res.text)
            return None
    except Exception as e:
        print("❌ Error uploading to Supabase Storage:", e)
        return None

def public_url_for(path_in_bucket: str) -> str:
    """Return public URL for object in bucket."""
    return f"{SUPABASE_STORAGE_URL}/{path_in_bucket}"
