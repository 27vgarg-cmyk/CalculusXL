"""EXE Runner - upload a Windows .exe (or a .zip of a game folder) and run it with Wine.

The game draws onto a virtual X display (:1). x11vnc + noVNC stream that display
to your browser on port 6080, which this page embeds.
"""
import os
import shutil
import signal
import subprocess
import zipfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

GAMES_DIR = Path(os.environ.get("EXE_GAMES_DIR", Path.home() / "exe-games"))
LOG_FILE = GAMES_DIR / "wine.log"
DISPLAY = os.environ.get("EXE_DISPLAY", ":1")
VNC_PORT = int(os.environ.get("EXE_NOVNC_PORT", 6080))

GAMES_DIR.mkdir(parents=True, exist_ok=True)
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024 * 1024  # 4 GB

current = {"proc": None, "exe": None}


def list_exes():
    """Every .exe under the games folder, skipping obvious installers/uninstallers."""
    out = []
    for p in sorted(GAMES_DIR.rglob("*")):
        if p.suffix.lower() == ".exe" and p.is_file():
            rel = p.relative_to(GAMES_DIR).as_posix()
            name = p.name.lower()
            hint = "uninstaller" if "unins" in name else ("crash handler" if "crash" in name else "")
            out.append({"path": rel, "size_mb": round(p.stat().st_size / 1e6, 1), "hint": hint})
    return out


def safe_path(rel):
    p = (GAMES_DIR / rel).resolve()
    if GAMES_DIR.resolve() not in p.parents:
        raise ValueError("bad path")
    return p


def safe_extract(zf: zipfile.ZipFile, dest: Path):
    dest = dest.resolve()
    for member in zf.infolist():
        target = (dest / member.filename).resolve()
        if dest != target and dest not in target.parents:
            raise ValueError(f"unsafe path in zip: {member.filename}")
    zf.extractall(dest)


def stop_game():
    proc = current["proc"]
    if proc and proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    # wineserver -k kills every Windows process in the prefix (games often spawn children)
    subprocess.run(["wineserver", "-k"], capture_output=True)
    current["proc"], current["exe"] = None, None


@app.route("/")
def index():
    return render_template("index.html", vnc_port=VNC_PORT)


@app.route("/api/games")
def games():
    running = current["proc"] is not None and current["proc"].poll() is None
    return jsonify(games=list_exes(), running=current["exe"] if running else None)


@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify(error="No file"), 400
    name = secure_filename(f.filename)
    ext = Path(name).suffix.lower()
    if ext == ".exe":
        folder = GAMES_DIR / Path(name).stem
        folder.mkdir(exist_ok=True)
        f.save(folder / name)
    elif ext == ".zip":
        folder = GAMES_DIR / Path(name).stem
        folder.mkdir(exist_ok=True)
        tmp = folder / name
        f.save(tmp)
        try:
            with zipfile.ZipFile(tmp) as zf:
                safe_extract(zf, folder)
        except (zipfile.BadZipFile, ValueError) as e:
            shutil.rmtree(folder, ignore_errors=True)
            return jsonify(error=f"Bad zip: {e}"), 400
        tmp.unlink()
        # Zip had one top-level folder (MyGame/...)? Flatten so we don't get MyGame/MyGame/
        kids = list(folder.iterdir())
        if len(kids) == 1 and kids[0].is_dir():
            inner = kids[0]
            for item in list(inner.iterdir()):
                shutil.move(str(item), folder / item.name)
            inner.rmdir()
    else:
        return jsonify(error="Upload a .exe or a .zip of the game folder"), 400
    return jsonify(ok=True, games=list_exes())


@app.route("/api/run", methods=["POST"])
def run():
    rel = (request.json or {}).get("path", "")
    try:
        exe = safe_path(rel)
    except ValueError:
        return jsonify(error="Bad path"), 400
    if not exe.is_file():
        return jsonify(error="Not found"), 404
    stop_game()
    env = dict(os.environ, DISPLAY=DISPLAY, WINEDEBUG="-all")
    log = open(LOG_FILE, "w")
    # Run from the exe's own folder: most games load data files by relative path.
    current["proc"] = subprocess.Popen(
        ["wine", exe.name], cwd=exe.parent, env=env,
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
    )
    current["exe"] = rel
    return jsonify(ok=True, running=rel)


@app.route("/api/stop", methods=["POST"])
def stop():
    stop_game()
    return jsonify(ok=True)


@app.route("/api/delete", methods=["POST"])
def delete():
    rel = (request.json or {}).get("path", "")
    try:
        top = safe_path(rel.split("/")[0])
    except ValueError:
        return jsonify(error="Bad path"), 400
    if current["exe"] and current["exe"].split("/")[0] == rel.split("/")[0]:
        stop_game()
    shutil.rmtree(top, ignore_errors=True)
    return jsonify(ok=True, games=list_exes())


@app.route("/api/log")
def log():
    if not LOG_FILE.exists():
        return jsonify(log="")
    return jsonify(log=LOG_FILE.read_text(errors="replace")[-6000:])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("EXE_UI_PORT", 8080)), threaded=True)
