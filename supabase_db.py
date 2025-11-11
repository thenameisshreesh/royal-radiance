# supabase_db.py
import requests, json
from config import SUPABASE_URL, HEADERS

# ------------------ PRODUCTS ------------------
def get_all_products():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/products?select=*", headers=HEADERS)
    return r.json()

def add_product(name, short_desc, price, image):
    data = {"name": name, "short_desc": short_desc, "price": price, "image": image}
    r = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, data=json.dumps(data))
    return r.status_code == 201

def delete_product(pid):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/products?id=eq.{pid}", headers=HEADERS)
    return r.status_code == 204


# ------------------ BLOGS ------------------
def get_all_blogs():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/blog_posts?select=*", headers=HEADERS)
    return r.json()

def add_blog(title, excerpt, content, image):
    data = {"title": title, "excerpt": excerpt, "content": content, "image": image}
    r = requests.post(f"{SUPABASE_URL}/rest/v1/blog_posts", headers=HEADERS, data=json.dumps(data))
    return r.status_code == 201

def delete_blog(bid):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/blog_posts?id=eq.{bid}", headers=HEADERS)
    return r.status_code == 204


# ------------------ SITE CONTENT ------------------
def get_site_content(key):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/site_content?key=eq.{key}&select=value", headers=HEADERS)
    data = r.json()
    return data[0]['value'] if data else None

def update_site_content(key, value):
    data = {"value": value}
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/site_content?key=eq.{key}", headers=HEADERS, data=json.dumps(data))
    return r.status_code == 204
