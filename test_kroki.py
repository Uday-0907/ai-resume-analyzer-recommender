import urllib.request

dot = "digraph G { Hello -> World }"

try:
    req = urllib.request.Request("https://kroki.io/graphviz/png", data=dot.encode("utf-8"), headers={"Content-Type": "text/plain"})
    with urllib.request.urlopen(req) as resp:
        with open("test.png", "wb") as f:
            f.write(resp.read())
    print("Success")
except Exception as e:
    print(e)
