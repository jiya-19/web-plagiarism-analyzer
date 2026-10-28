import re
import base64
import requests

from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

MAX_SENTENCES = 12
MAX_RESULTS_PER_QUERY = 6
MAX_PAGE_CHARS = 70000


def extract_text(path):
    ext = path.rsplit(".", 1)[-1].lower()

    if ext == "txt":
        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:
            return f.read()

    if ext == "pdf":
        import PyPDF2

        reader = PyPDF2.PdfReader(path)

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if ext == "docx":
        from docx import Document

        doc = Document(path)

        return "\n".join(
            p.text
            for p in doc.paragraphs
        )

    raise ValueError(
        "Unsupported file type."
    )


def clean_text(text):
    text = text.replace(
        "\x00",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_sentences(text):
    text = clean_text(text)

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    result = []

    for part in parts:

        part = part.strip()

        words = len(
            part.split()
        )

        if 7 <= words <= 80:
            result.append(part)

    return result


def make_query(sentence):

    stop_words = {
        "this", "that", "with", "from",
        "they", "their", "there", "which",
        "these", "those", "have", "been",
        "were", "will", "into", "about",
        "using", "used", "also", "than",
        "such", "more", "some", "many",
        "when", "where", "what", "over"
    }

    words = re.findall(
        r"[A-Za-z0-9][A-Za-z0-9'-]+",
        sentence
    )

    words = [
        word
        for word in words
        if (
            len(word) > 3
            and word.lower() not in stop_words
        )
    ]

    return " ".join(
        words[:16]
    )


def normalize_bing_url(url):

    try:

        parsed = urlparse(url)

        params = parse_qs(
            parsed.query
        )

        if "u" in params:

            encoded = params["u"][0]

            if encoded.startswith("a1"):
                encoded = encoded[2:]

            padding = "=" * (
                (-len(encoded)) % 4
            )

            decoded = base64.urlsafe_b64decode(
                encoded + padding
            ).decode(
                "utf-8",
                errors="ignore"
            )

            if decoded.startswith("http"):
                return decoded

    except Exception:
        pass

    return url


def search_web(query):

    search_url = (
        "https://www.bing.com/search?q="
        + quote(
            '"' + query + '"'
        )
    )

    response = requests.get(
        search_url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    results = []

    for link in soup.select(
        "li.b_algo h2 a"
    ):

        title = link.get_text(
            " ",
            strip=True
        )

        url = normalize_bing_url(
            link.get(
                "href",
                ""
            )
        )

        if not url.startswith("http"):
            continue

        domain = urlparse(
            url
        ).netloc.lower()

        if not domain:
            continue

        results.append({
            "title": title or domain,
            "url": url
        })

        if len(results) >= MAX_RESULTS_PER_QUERY:
            break

    unique = []
    seen = set()

    for item in results:

        domain = urlparse(
            item["url"]
        ).netloc.lower()

        if domain not in seen:

            seen.add(domain)

            unique.append(
                item
            )

    return unique


def fetch_page(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10,
            allow_redirects=True
        )

        content_type = response.headers.get(
            "content-type",
            ""
        ).lower()

        if "text/html" not in content_type:
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
            "noscript"
        ]):

            tag.decompose()

        text = soup.get_text(
            " ",
            strip=True
        )

        return clean_text(
            text
        )[:MAX_PAGE_CHARS]

    except Exception:
        return ""


def lexical_similarity(
    text_a,
    text_b
):

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        matrix = vectorizer.fit_transform([
            text_a,
            text_b
        ])

        score = cosine_similarity(
            matrix[0:1],
            matrix[1:2]
        )[0][0]

        return float(
            score * 100
        )

    except Exception:

        return 0.0


def token_overlap(
    text_a,
    text_b
):

    words_a = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text_a.lower()
        )
    )

    words_b = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text_b.lower()
        )
    )

    if not words_a:
        return 0.0

    return (
        len(words_a & words_b)
        / len(words_a)
        * 100
    )


def sentence_match(
    student_sentence,
    source_text
):

    candidates = split_sentences(
        source_text
    )

    if not candidates:
        return (
            0.0,
            "",
            0.0
        )

    best_score = 0.0
    best_sentence = ""
    best_overlap = 0.0

    for candidate in candidates:

        lexical = lexical_similarity(
            student_sentence,
            candidate
        )

        overlap = token_overlap(
            student_sentence,
            candidate
        )

        combined = (
            0.70 * lexical
            + 0.30 * overlap
        )

        if combined > best_score:

            best_score = combined
            best_sentence = candidate
            best_overlap = overlap

    return (
        best_score,
        best_sentence,
        best_overlap
    )


def analyze_document(path):

    text = clean_text(
        extract_text(path)
    )

    if len(text.split()) < 20:

        raise ValueError(
            "The document contains too little "
            "readable text."
        )

    all_sentences = split_sentences(
        text
    )

    if not all_sentences:

        raise ValueError(
            "No suitable sentences could "
            "be extracted."
        )

    sentences = all_sentences[
        :MAX_SENTENCES
    ]

    matches = []

    source_map = {}

    web_searches = 0
    web_results_found = 0
    pages_retrieved = 0

    for sentence in sentences:

        query = make_query(
            sentence
        )

        if len(query.split()) < 5:
            continue

        web_searches += 1

        try:

            web_results = search_web(
                query
            )

        except Exception:

            web_results = []

        web_results_found += len(
            web_results
        )

        best = None

        for source in web_results:

            page_text = fetch_page(
                source["url"]
            )

            if not page_text:
                continue

            pages_retrieved += 1

            (
                score,
                matched_text,
                overlap
            ) = sentence_match(
                sentence,
                page_text
            )

            item = {
                "sentence": sentence,
                "score": round(
                    score,
                    1
                ),
                "overlap": round(
                    overlap,
                    1
                ),
                "matched_text": matched_text,
                "title": source["title"],
                "url": source["url"]
            }

            if (
                best is None
                or item["score"] > best["score"]
            ):

                best = item

        if best:

            matches.append(best)

            domain = urlparse(
                best["url"]
            ).netloc.lower()

            if domain not in source_map:

                source_map[domain] = {
                    "title": best["title"],
                    "url": best["url"],
                    "score": best["score"],
                    "matches": 1
                }

            else:

                source_map[
                    domain
                ]["score"] = max(
                    source_map[
                        domain
                    ]["score"],
                    best["score"]
                )

                source_map[
                    domain
                ]["matches"] += 1

    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if matches:

        overall = sum(
            item["score"]
            for item in matches
        ) / len(matches)

    else:

        overall = 0.0

    flagged = [
        item
        for item in matches
        if item["score"] >= 20
    ]

    sources = sorted(
        source_map.values(),
        key=lambda x: (
            x["score"],
            x["matches"]
        ),
        reverse=True
    )[:8]

    if web_searches == 0:

        status = (
            "No suitable sentences were "
            "available for web search."
        )

    elif web_results_found == 0:

        status = (
            "The document was read successfully, "
            "but the web search returned no "
            "usable results."
        )

    elif pages_retrieved == 0:

        status = (
            "Web results were found, but their "
            "pages could not be retrieved "
            "for comparison."
        )

    else:

        status = (
            f"{web_results_found} web results found "
            f"and {pages_retrieved} source pages analyzed."
        )

    return {
        "word_count": len(
            text.split()
        ),

        "total_sentences": len(
            all_sentences
        ),

        "sentences_checked": len(
            sentences
        ),

        "searched_sentences": (
            web_searches
        ),

        "web_results_found": (
            web_results_found
        ),

        "pages_retrieved": (
            pages_retrieved
        ),

        "status": status,

        "overall": round(
            overall,
            1
        ),

        "flagged": flagged,

        "matches": matches,

        "sources": sources
    }