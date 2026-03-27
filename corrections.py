# ---------------------------------------------------------------
# Custom word corrections applied AFTER Whisper transcription.
# Add your own entries as needed: "wrong" -> "correct"
# Case-insensitive matching, preserves original casing style.
# ---------------------------------------------------------------
import re

CORRECTIONS = {
    # Names
    "zishan":     "Zeeshan",
    "zeeshan":    "Zeeshan",
    "zeshan":     "Zeeshan",
    "yarrid":     "Yarrid",
    "litton":     "Litens",
    "litens":     "Litens",
    "liten":      "Litens",
    "litten":     "Litens",
    "litans":     "Litens",

    # Misheard words
    "love me":    "Navmi",
    "navmi":      "Navmi",
    "hit":        "it",       # context-dependent — remove if causes issues
    "mini":       "May",      # "29th of mini" -> "29th of May"
    "klein and zigen": "Kleinanzeigen",
    "client and zagon": "Kleinanzeigen",
    "klein and zagon":  "Kleinanzeigen",
    "kleinanzeigen":    "Kleinanzeigen",
    "jimmy now":  "Gemini",
    "jimmy":      "Gemini",
    "berlin":     "Bremen",   # you said you’re in Bremen, not Berlin

    # Tech / brand names
    "llm's":      "LLMs",
    "llms":       "LLMs",
    "vs code":    "VS Code",
    "gpt":        "GPT",
    "claude":     "Claude",
    "anthropic":  "Anthropic",
    "perplexity": "Perplexity",
    "youtube":    "YouTube",
    "instagram":  "Instagram",
    "snapchat":   "Snapchat",
    "reddit":     "Reddit",
    "ebay":       "eBay",
    "clash royale": "Clash Royale",
    "peca":       "PEKKA",
    "hdmi":       "HDMI",
    "edge dmi":   "HDMI",
    "edge DMI":   "HDMI",
}


def apply_corrections(text: str) -> str:
    """Apply all corrections to a transcript segment text."""
    for wrong, right in CORRECTIONS.items():
        # Word-boundary aware, case-insensitive replace
        pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        text = pattern.sub(right, text)
    return text


def correct_segments(segments: list) -> list:
    """Apply corrections to all Whisper segments in-place."""
    for seg in segments:
        seg["text"] = apply_corrections(seg["text"])
    return segments
