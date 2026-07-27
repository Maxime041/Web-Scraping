# benchmark_throttling.py
import time
from main import get_page, parse_articles, BASE_URL

def benchmark(nb_pages: int, delay: float) -> float:
    t0 = time.time()
    tous = []
    for page in range(1, nb_pages + 1):
        url = "https://www.blogdumoderateur.com/" if page == 1 else BASE_URL.format(n=page)
        soup = get_page(url)
        arts = parse_articles(soup)
        tous.extend(arts)
        time.sleep(delay)
    duree = time.time() - t0
    print(f"Pages: {nb_pages} | Delay: {delay}s => Duree: {duree:.1f}s ({len(tous)} articles)")
    return duree

if __name__ == "__main__":
    print("--- Benchmark du throttling ---")
    for pages in [2, 5, 10]:
        for d in [0.5, 1.0, 2.0]:
            benchmark(pages, d)
