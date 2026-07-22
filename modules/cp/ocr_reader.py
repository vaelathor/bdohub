"""
OCR Reader for BDO Life Skills Screenshots - OCR.space Edition
Uses OCR.space cloud API for far superior accuracy on colored game UI text.
"""

import re
import base64
import os
from io import BytesIO

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False

OCR_SPACE_API_URL = "https://api.ocr.space/parse/image"

OCR_SPACE_API_KEY = None

# Try python-dotenv first, fall back to manual .env parsing
if HAS_DOTENV:
    # Search for .env in common locations
    env_candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".env"),
        os.path.join(os.path.expanduser("~"), "projects", "bdohub", ".env"),
        ".env",
    ]
    for env_path in env_candidates:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break
    OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY") or os.getenv("OCRSPACE_API_KEY")

# Fallback: manual parsing if dotenv didn't find the key
if not OCR_SPACE_API_KEY:
    env_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".env"),
        os.path.join(os.path.expanduser("~"), "projects", "bdohub", ".env"),
        ".env",
    ]
    for env_path in env_paths:
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OCR_SPACE_API_KEY="):
                        OCR_SPACE_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
                    if line.startswith("OCRSPACE_API_KEY="):
                        OCR_SPACE_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            if OCR_SPACE_API_KEY:
                break
        except (IOError, OSError):
            continue


KNOWN_PROFESSIONS = ["Alquimia", "Caça", "Coleta", "Culinária", "Cultivo", "Pesca"]

RANKS = ["Iniciante", "Aprendiz", "Profissional", "Artesao", "Artifice", "Mestre", "Guru"]

RANK_VARIANTS = {
    "Inicante": "Iniciante", "Iniciant": "Iniciante",
    "Aprendz": "Aprendiz", "Aprend": "Aprendiz",
    "Profssional": "Profissional", "Profisonal": "Profissional",
    "Profision": "Profissional",
    "Artesao": "Artesao", "Artesan": "Artesao",
    "Artifce": "Artifice", "Artifice": "Artifice",
    "Mest": "Mestre",
    "Guri": "Guru", "Giru": "Guru",
}

PROFESSION_VARIANTS = {
    "Alquimia":  ["Alquimia", "Alquim", "Alguimia", "Alqm", "Alquima"],
    "Caça":      ["Caça", "Caca", "Caga"],
    "Coleta":    ["Coleta", "Colea", "Colet"],
    "Culinária": ["Culinária", "Culinaria", "Culinria", "Culindria", "Culina"],
    "Cultivo":   ["Cultivo", "Cultvo", "Cultiv"],
    "Pesca":     ["Pesca", "Psca", "Peca"],
}


def preprocess_image(image_bytes):
    """Light preprocessing to help OCR.space."""
    if not HAS_PIL:
        return image_bytes

    img = Image.open(BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')

    w, h = img.size
    # Keep original size for API (OCR.space has size limits)
    # Only upscale if image is very small (< 300px)
    if w < 300:
        scale = 300.0 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    img = img.filter(ImageFilter.SHARPEN)

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def extract_text_from_image(image_bytes):
    """Send image to OCR.space API and return extracted text."""
    if not HAS_REQUESTS:
        return "[Error: requests library not installed]"

    if not OCR_SPACE_API_KEY:
        return "[Error: OCR_SPACE_API_KEY not found in .env]"

    processed = preprocess_image(image_bytes)
    b64_data = base64.b64encode(processed).decode("utf-8")

    headers = {"apikey": OCR_SPACE_API_KEY}
    data = {
        "base64Image": "data:image/png;base64," + b64_data,
        "language": "por",
        "OCREngine": "2",
        "isTable": "false",
        "scale": "true",
    }

    try:
        resp = requests.post(OCR_SPACE_API_URL, headers=headers, data=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
    except requests.exceptions.RequestException as e:
        return "[API Error: " + str(e) + "]"
    except ValueError as e:
        return "[JSON Parse Error: " + str(e) + "]"

    if result.get("IsErroredOnProcessing"):
        return "[OCR.space Error: " + result.get("ErrorMessage", "Unknown") + "]"

    ocr_exit = result.get("OCRExitCode", 3)
    if ocr_exit == 3 or ocr_exit == 4:
        return "[OCR.space Error: " + result.get("ErrorMessage", "Exit code " + str(ocr_exit)) + "]"

    parsed = result.get("ParsedResults", [])
    if not parsed:
        return "[OCR.space Error: No parsed results]"

    texts = [p.get("ParsedText", "") for p in parsed]
    return "\n".join(t for t in texts if t) or "[OCR.space: No text extracted]"


def _find_profession(text):
    """Fuzzy-find a known profession name in text."""
    lower = text.lower()
    for canon, variants in PROFESSION_VARIANTS.items():
        for variant in variants:
            if variant.lower() in lower:
                return canon
    for prof in KNOWN_PROFESSIONS:
        if prof.lower() in lower:
            return prof
    return None


def _find_rank(text):
    """Find rank (name + number) in text."""
    clean = text.replace(".", " ").replace(":", " ").replace("&", "8").replace("@", "0")
    for rank in RANKS:
        m = re.search(re.escape(rank) + r"\s*(\d+)", clean, re.IGNORECASE)
        if m:
            return rank, m.group(1), m.end()

    for ocr_rank, canon_rank in RANK_VARIANTS.items():
        if ocr_rank != canon_rank:
            m = re.search(re.escape(ocr_rank) + r"\s*(\d+)", clean, re.IGNORECASE)
            if m:
                return canon_rank, m.group(1), m.end()

    rank_joined = "|".join(re.escape(r) for r in RANKS)
    m = re.search(rf"(?:{rank_joined})\s*(\d+)", clean, re.IGNORECASE)
    if m:
        for rank in RANKS:
            if rank.lower() in m.group(0).lower():
                return rank, m.group(1), m.end()
    return None


def _find_percentage(text):
    """Extract percentage from text."""
    m = re.search(r"(\d+)[.,](\d+)\s*%", text)
    if m:
        try:
            val = float(f"{m.group(1)}.{m.group(2)}")
            if val <= 100:
                return val
        except ValueError:
            pass

    rank_joined = "|".join(re.escape(r) for r in RANKS)
    m = re.search(rf"(?:{rank_joined})\s*\d+\s+(\d+[.,]\d+)", text, re.IGNORECASE)
    if m:
        try:
            val = float(m.group(1).replace(",", "."))
            if val <= 100:
                return val
        except ValueError:
            pass

    decimals = re.findall(r"(\d+)[.,](\d+)", text)
    for whole, dec in decimals:
        try:
            val = float(f"{whole}.{dec}")
            if 0 < val <= 100:
                return val
        except ValueError:
            continue
    return 0.0


def parse_professions_from_text(text):
    """Parse OCR text into structured profession data.

    Handles:
    - Columnar format: professions, then %, then ranks on separate lines (OCR.space)
    - Single-line: "Profissao Rank X 45.5%" (Tesseract format)
    - Multi-line: prof on line 1, rank on line 2
    """
    if not text or text.startswith("[Error") or text.startswith("[OCR"):
        return [], text

    lines = text.split("\n")

    # Phase 1: Tag all items in order of appearance
    tagged_profs = []  # list of (name, position_index)
    tagged_pcts = []   # list of (value, position_index)
    tagged_ranks = []  # list of (rank_name, level_num, position_index)

    for pos, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue

        r = _find_rank(line)
        if r:
            tagged_ranks.append((r[0], r[1], pos))
            continue

        pc = _find_percentage(line)
        if pc > 0:
            tagged_pcts.append((pc, pos))
            continue

        # Any remaining text is a potential profession name
        clean_line = re.sub(r"^[\s\-\_\.\,A-Za-z]\s+", "", line).strip()
        if clean_line and len(clean_line) > 1:
            tagged_profs.append((clean_line, pos))
            continue

    # Phase 2: Detect format type and match
    results = []

    # Check if this is columnar format (professions come in a block before other types)
    is_columnar = False
    if tagged_profs and tagged_ranks:
        first_prof_pos = tagged_profs[0][1]
        last_prof_pos = tagged_profs[-1][1]
        first_rank_pos = tagged_ranks[0][2]
        first_pct_pos = tagged_pcts[0][1] if tagged_pcts else float('inf')

        # Columnar if professions all appear before first rank and first pct
        if last_prof_pos < first_rank_pos and last_prof_pos < first_pct_pos:
            is_columnar = True

    if is_columnar:
        # Match by index: profession[i] gets percentage[i] and rank[i]
        for idx, (raw_name, _) in enumerate(tagged_profs):
            # Find canonical profession name (with accents for CP system)
            prof_name = _find_profession(raw_name)
            if not prof_name or prof_name not in KNOWN_PROFESSIONS:
                continue

            pct_val = tagged_pcts[idx][0] if idx < len(tagged_pcts) else 0.0
            rank_info = tagged_ranks[idx] if idx < len(tagged_ranks) else None

            if rank_info:
                results.append({
                    "profession": prof_name,
                    "level": rank_info[0] + " " + rank_info[1],
                    "pct": pct_val,
                })
            else:
                results.append({
                    "profession": prof_name,
                    "level": "Desconhecido",
                    "pct": pct_val,
                })
    else:
        # Phase 3: Greedy matcher for inline/multi-line format
        pending_prof = None
        pending_pct = None

        for item_type, value in [
            ("prof", p[0]) for p in tagged_profs
        ] + [
            ("pct", p[0]) for p in tagged_pcts
        ] + [
            ("rank", (r[0], r[1])) for r in tagged_ranks
        ]:
            # Sort by position (they're already in order since we append in order)
            pass  # The combined list is already sorted by position

        # Actually, redo properly: combine all tagged items sorted by position
        all_items = []
        for p in tagged_profs:
            all_items.append(("prof", p[0], p[1]))
        for p in tagged_pcts:
            all_items.append(("pct", p[0], p[1]))
        for r in tagged_ranks:
            all_items.append(("rank", (r[0], r[1]), r[2]))
        all_items.sort(key=lambda x: x[2])

        for item_type, value, _ in all_items:
            if item_type == "prof":
                if pending_prof and pending_pct is not None:
                    pass  # Do nothing, just overwrite
                pending_prof = value
            elif item_type == "rank" and pending_prof:
                rank_name, level_num = value
                results.append({
                    "profession": pending_prof,
                    "level": rank_name + " " + level_num,
                    "pct": pending_pct if pending_pct is not None else 0.0,
                })
                pending_prof = None
                pending_pct = None
            elif item_type == "pct":
                if pending_prof:
                    pending_pct = value

        # Phase 4: Fallback to line-by-line if nothing found
        if not results:
            i = 0
            while i < len(lines):
                raw_line = lines[i].strip()
                i += 1
                if not raw_line:
                    continue
                p = _find_profession(raw_line)
                if not p:
                    continue
                r = _find_rank(raw_line)
                pc = _find_percentage(raw_line)
                if not r:
                    peek = i
                    while peek < len(lines):
                        pl = lines[peek].strip()
                        if pl:
                            r = _find_rank(pl)
                            if r and pc == 0.0:
                                pc = _find_percentage(pl)
                            break
                        peek += 1
                if r:
                    results.append({
                        "profession": p,
                        "level": r[0] + " " + r[1],
                        "pct": pc,
                    })

    return results, text
def ocr_from_image(image_bytes):
    """Main: send image to OCR.space and return structured profession data."""
    text = extract_text_from_image(image_bytes)

    if text.startswith("[Error") or text.startswith("[OCR"):
        return {
            "success": False,
            "error": text.strip("[]"),
            "raw_text": text,
            "data": None,
            "count": 0,
        }

    professions, raw_text = parse_professions_from_text(text)

    if professions:
        return {
            "success": True,
            "data": professions,
            "raw_text": raw_text,
            "error": None,
            "count": len(professions),
        }
    else:
        return {
            "success": False,
            "error": "Nao foi possivel extrair dados. Texto OCR abaixo:",
            "raw_text": raw_text,
            "data": None,
            "count": 0,
        }



def ocr_inventory_from_image(image_bytes):
    """Extract raw text from an inventory screenshot via OCR.space.
    Returns raw text for analysis (no professions parsing)."""
    text = extract_text_from_image(image_bytes)
    # Log raw text for debugging
    import sys
    print(f"[OCR-INVENTORY] raw_text: {repr(text)}", flush=True)

    if text.startswith("[Error") or text.startswith("[OCR"):
        return {
            "success": False,
            "error": text.strip("[]"),
            "raw_text": text,
        }

    # Return raw text for now - we'll build parsing once we see sample images
    if text and text != "[OCR.space: No text extracted]":
        return {
            "success": True,
            "raw_text": text,
            "data": None,
            "message": "Texto extraído. Aguardando parser de inventário.",
        }
    else:
        return {
            "success": False,
            "error": text.strip("[]"),
            "raw_text": text,
        }


def ocr_from_base64(b64_string):
    """Entry point for base64-encoded images."""
    try:
        image_bytes = base64.b64decode(b64_string)
        return ocr_from_image(image_bytes)
    except Exception as e:
        return {"success": False, "error": str(e), "data": None, "count": 0}
