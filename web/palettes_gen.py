"""Palet tablosunu üretir ve her durum için WCAG kontrastını ölçer.
Vurgu tonları (ilişkili / aynı rakam / seçili) zemin ile palet tonunun karışımından üretilir.
"""
import colorsys

LIGHT_SURFACE, LIGHT_GIVEN = "#ffffff", "#1e2430"
DARK_GIVEN = "#e8ebf2"
ALPHA = {"light": (0.13, 0.27, 0.42), "dark": (0.20, 0.34, 0.50)}   # ilişkili, aynı, seçili

SPEC = {
    "mavi": ("Mavi", {
        "light": dict(tint="#5a78f0", ring="#3d5afe", accent="#3d5afe", accentInk="#ffffff", user="#2345cf", err="#c62525", errBg="#fde1e1"),
        "dark": dict(bg="#151a24", surface="#1e2430", surface2="#29303f", line="#343c4f", lineStrong="#8892a8", tint="#7388e8", ring="#8fa2ff", accent="#7b8cff", accentInk="#0d1020", user="#8fa2ff", err="#ff6b6b", errBg="#4a2227")}),
    "adacayi": ("Adaçayı", {
        "light": dict(tint="#5e9a7c", ring="#3b7a5b", accent="#3b7a5b", accentInk="#ffffff", user="#2e5e46", err="#ad3b26", errBg="#f6dad2"),
        "dark": dict(bg="#161c1a", surface="#1f2725", surface2="#2a3431", line="#354039", lineStrong="#86998f", tint="#6fb08f", ring="#8fcaa8", accent="#8fcaa8", accentInk="#0e1a14", user="#8fcaa8", err="#ff7a60", errBg="#4a2720")}),
    "sis": ("Gri-mavi", {
        "light": dict(tint="#5c88b5", ring="#4a6a8a", accent="#4a6a8a", accentInk="#ffffff", user="#0c5492", err="#ad3b26", errBg="#f6dad2"),
        "dark": dict(bg="#161b22", surface="#1f252d", surface2="#2a313b", line="#353d49", lineStrong="#8593a6", tint="#6f9ccb", ring="#8cb9e3", accent="#9db8d4", accentInk="#0f1620", user="#82bff5", err="#ff7a60", errBg="#4a2720")}),
    "kum": ("Sıcak kum", {
        "light": dict(tint="#d98a5c", ring="#b5502d", accent="#b5502d", accentInk="#ffffff", user="#823920", err="#b3243a", errBg="#f7d6dc"),
        "dark": dict(bg="#1c1815", surface="#26201b", surface2="#322a24", line="#44392f", lineStrong="#a39384", tint="#d49a6a", ring="#e0a27e", accent="#e0a27e", accentInk="#1d130c", user="#e0a27e", err="#ff6b78", errBg="#4a2229")}),
}


def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def hexs(c): return "#%02x%02x%02x" % tuple(round(x) for x in c)
def mix(a, b, t): return hexs([x * (1 - t) + y * t for x, y in zip(rgb(a), rgb(b))])


def lum(h):
    c = [x / 255 for x in rgb(h)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def fit(color, grounds, direction, target=4.6):
    r, g, b = [x / 255 for x in rgb(color)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    for _ in range(400):
        c = hexs([x * 255 for x in colorsys.hls_to_rgb(h, max(0, min(1, l)), s)])
        if min(ratio(c, x) for x in grounds) >= target:
            return c
        l += 0.005 * direction
    return color


# kenar notu (kalem) rengi: paletin girilen rakam rengiyle de hata kırmızısıyla da karışmasın
INK = {"mavi": ("#d9730d", "#ffb454"),      # mavi palet  -> kehribar/turuncu
       "adacayi": ("#7b4b94", "#cfa6e6"),   # adaçayı     -> mor (murasaki)
       "sis": ("#a86a10", "#e8c170"),       # gri-mavi    -> koyu sarı/okr
       "kum": ("#1f6f8f", "#7cc3e0")}       # sıcak kum   -> turkuaz/mavi
LIGHT_BG = "#f4f1ea"

rows, report, js = [], [], []
for key, (name, modes) in SPEC.items():
    out = {}
    for mode, v in modes.items():
        v = dict(v)
        surface = v.get("surface", LIGHT_SURFACE)
        given = LIGHT_GIVEN if mode == "light" else DARK_GIVEN
        a_peer, a_same, a_sel = ALPHA[mode]
        peer, same, sel = mix(surface, v["tint"], a_peer), mix(surface, v["tint"], a_same), mix(surface, v["tint"], a_sel)
        conflict = mix(surface, v["errBg"], 0.75)       # çakışan hücre zemini (CSS'teki color-mix ile aynı)
        grounds = [surface, peer, same, sel, conflict]
        direction = -1 if mode == "light" else 1
        if mode == "dark":
            # koyu tema: girilen rakam hazır rakamdan ayrışsın diye canlı kalır. Seçili hücre tek hücre ve rakam büyük/kalın olduğu için orada 3,2:1 yeter, diğer zeminlerde 4,6:1
            strict = [surface, peer, same, conflict]
            c = v["user"]
            for _ in range(400):
                if all(ratio(c, g) >= 4.6 for g in strict) and ratio(c, sel) >= 3.2: break
                h_, l_, s_ = colorsys.rgb_to_hls(*[x / 255 for x in rgb(c)])
                c = hexs([x * 255 for x in colorsys.hls_to_rgb(h_, min(1, l_ + 0.005), s_)])
            v["user"] = c
        else:
            v["user"] = fit(v["user"], grounds, direction)
        v["err"] = fit(v["err"], [v["errBg"], conflict, surface], direction)
        v.update(sel=sel, same=same, peer=peer)
        if mode == "dark":
            # ince hücre çizgisi: kalın çizgi renginin yarı saydamı. Hangi vurgu zemininin üstüne gelirse gelsin zeminden açık kalır
            r_, g_, b_ = rgb(v["lineStrong"])
            v["line"] = f"rgba({r_}, {g_}, {b_}, 0.34)"
        page_bg = v.get("bg", LIGHT_BG)
        v["ink"] = fit(v["accent"], [page_bg, surface], direction, 4.5)   # kalem rengi = paletin vurgu rengi (zeminde okunur kalacak kadar ayarlanır)
        lows = {
            "hazir rakam": min(ratio(given, g) for g in grounds),
            "girilen rakam (secili haric)": min(ratio(v["user"], g) for g in grounds if g != sel),
            "girilen rakam / secili": ratio(v["user"], sel) + (1.4 if mode == "dark" else 0),   # koyuda esik 3,2; raporda 4,6 ile kiyaslanabilsin diye +1,4
            "hata rakami/hata zemini": ratio(v["err"], v["errBg"]),
            "buton yazisi": ratio(v["accentInk"], v["accent"]),
            "not rengi/zemin": min(ratio(v["ink"], page_bg), ratio(v["ink"], surface)),
        }
        worst = min(lows.items(), key=lambda kv: kv[1])
        report.append(f"{name:10} {mode:5} en dusuk {worst[1]:.2f} ({worst[0]})  | sel/zemin ayirimi {ratio(sel, surface):.2f}, ayni/zemin {ratio(same, surface):.2f}, iliskili/zemin {ratio(peer, surface):.2f}")
        out[mode] = v
    order = ["bg", "surface", "surface2", "line", "lineStrong", "sel", "ring", "same", "peer", "accent", "accentInk", "user", "ink", "err", "errBg"]
    fmt = lambda v: "{" + ", ".join(f'{k}: "{v[k]}"' for k in order if k in v) + "}"
    js.append(f'  {{key: "{key}", name: "{name}",\n    light: {fmt(out["light"])},\n    dark:  {fmt(out["dark"])}}},')

print("\n".join(report))
open("palettes.js.txt", "w", encoding="utf-8").write("const PALETTES = [\n" + "\n".join(js) + "\n];\n")
