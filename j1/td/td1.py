import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)

url = "https://www.blogdumoderateur.com/"
params = {"page": 2, "cat": "ia"}

try:
    r = session.get(url, params=params, timeout=10)
    r.raise_for_status()
    print("--- REQUÊTE GET ---")
    print("URL finale  :", r.url)
    print("Code HTTP   :", r.status_code)
    print("Extrait HTML:", r.text)
except requests.exceptions.HTTPError as e:
    print("Erreur HTTP :", e)
except requests.exceptions.Timeout:
    print("Erreur : Timeout dépassé")

print("\n" + "=" * 40 + "\n")

'''url_api = "https://httpbin.org/post"
payload = {"q": "machine learning"}

try:
    r_post = session.post(url_api, json=payload, timeout=10)
    r_post.raise_for_status()
    data = r_post.json()
    print("--- REQUÊTE POST ---")
    print("Code HTTP   :", r_post.status_code)
    print("JSON reçu   :", data.get("json"))
except requests.exceptions.HTTPError as e:
    print("Erreur HTTP :", e)
except requests.exceptions.Timeout:
    print("Erreur : Timeout dépassé")
except requests.exceptions.JSONDecodeError:
    print("Erreur : Réponse non JSON")'''