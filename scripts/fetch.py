"""Trage partidele daily dintre cei doi jucători de pe Chess.com și scrie site/data.json."""
import json, re, time, urllib.request

A, B = "marcus7aurelius", "ender6667"
HEADERS = {"User-Agent": "sah-h2h/1.0 (pagina personala de scor)"}


def get(url):
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print("reîncerc", url, e)
            time.sleep(5)
    raise SystemExit("nu am putut descărca " + url)


def tag(pgn, name):
    m = re.search(r'\[%s "([^"]*)"\]' % name, pgn)
    return m and m.group(1)


games = []
for month in get(f"https://api.chess.com/pub/player/{A}/games/archives")["archives"]:
    for g in get(month).get("games", []):
        w, b = g["white"]["username"].lower(), g["black"]["username"].lower()
        if g.get("time_class") != "daily" or {w, b} != {A, B} or "end_time" not in g:
            continue
        if g["white"]["result"] == "win":
            win = w
        elif g["black"]["result"] == "win":
            win = b
        else:
            continue  # remizele nu apar încă în pagină
        pgn = g.get("pgn", "")
        eco = tag(pgn, "ECOUrl") or ""
        acc = g.get("accuracies") or {}
        games.append(dict(
            e=g["end_time"], s=g.get("start_time", g["end_time"]), w=w, win=win,
            op=eco.rsplit("/", 1)[-1].replace("-", " ") if eco else "Deschidere necunoscută",
            mv=len(re.findall(r"\d+\.\s", re.sub(r"\{[^}]*\}", "", pgn.split("\n\n", 1)[-1]))),
            wr=g["white"]["rating"], br=g["black"]["rating"],
            wa=acc.get("white"), ba=acc.get("black"), u=g["url"]))
    time.sleep(0.5)

games.sort(key=lambda x: x["e"])
json.dump({"updated": int(time.time()), "games": games}, open("site/data.json", "w"), separators=(",", ":"))
print(len(games), "partide daily")
