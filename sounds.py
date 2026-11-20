import re
s = open('library.py').read()
a = s.index('def kana_chain(ch):')
b = s.index('# ------------------------------------------------------------------ state machine')
new = '''def kana_chain(ch):
    """kanji etymology -> man'yogana (kanji used for sound) -> kana -> literal translation (the sound)"""
    import meanings as M
    is_kata = "\\u30A1" <= ch <= "\\u30FA"
    src = None
    try:
        import symbolism as _S
        src = (getattr(_S, "KATA_ORIGIN", {}) if is_kata else getattr(_S, "HIRA_ORIGIN", {})).get(ch)
    except Exception:
        pass
    src = src or getattr(R, "KANA_ORIGIN", {}).get(ch)
    SRC = "Wikipedia (kana pages), Wiktionary, EBSCO Research Starters: kana syllabary"
    out = []
    if not src:
        return [{"role": "kana", "label": ch, "provenance": "traced", "sticks": R.traced(ch)["sticks"],
                 "note": "No source kanji on record."}]
    # 1. etymology of the source kanji (and its traced form), from symbolism.chain
    out += SY.chain(src) if SY else []
    # 2. man'yogana
    out.append({"role": "etymology", "label": f"{src} used for its SOUND only (man'yogana)",
                "provenance": "traced", "confidence": "standard", "source": SRC,
                "sticks": R.traced(src)["sticks"],
                "note": f"Man'yogana: kanji used phonetically for their sounds, not their meanings. "
                        f"{src} was borrowed for the sound, so its meaning "
                        f"({M.GLOSS.get(src, '?')}) is ignored. Kana developed from these in the Heian period."})
    # 3. the kana
    how = ("a fragment of the kanji, taken as shorthand (katakana)" if is_kata
           else "the whole kanji written in flowing cursive (hiragana)")
    k = R.traced(ch)
    out.append({"role": "kana", "label": f"{src} \\u2192 {ch}", "provenance": "traced",
                "confidence": "standard", "source": SRC, "sticks": k["sticks"],
                "note": f"{ch} is {how}."})
    # 4. literal translation
    import sounds as SN
    hk = [c for c in (chr(x) for x in range(0x3042, 0x3094)) if c not in "\\u3041\\u3043\\u3045\\u3047\\u3049\\u3063\\u3083\\u3085\\u3087\\u308e\\u3090\\u3091"]
    kk = [c for c in (chr(x) for x in range(0x30A2, 0x30F4)) if c not in "\\u30a1\\u30a3\\u30a5\\u30a7\\u30a9\\u30c3\\u30e3\\u30e5\\u30e7\\u30ee\\u30f0\\u30f1"]
    r = (dict(zip(hk, SN.ORDER)) | dict(zip(kk, SN.ORDER))).get(ch, "?")
    out.append({"role": "translation", "provenance": "designed", "sticks": {"w": 100, "h": 100, "s": []},
                "label": f"{ch} = the sound '{r}'",
                "note": f"Literal: the sound '{r}'. Not a word. Borrowed from {src}, which means {M.GLOSS.get(src, '?')}."})
    return out

'''
s = s[:a] + new + s[b:]
open('library.py', 'w').write(s)