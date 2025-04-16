from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
import os
import json
import re
import sqlite3
from flaskr.src.FacebookAPI import API

api = API(dbConnection=sqlite3.connect(
            "instance/flaskr.sqlite", detect_types=sqlite3.PARSE_DECLTYPES,
            
        ),
        CookiesRoute="flaskr/sessions",
        invisible=True
          
    )

bp = Blueprint("blog", __name__)


def es_enlace(url):
    patron = re.compile(
        r"^(?:http|ftp)s?://"  # http:// o https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # dominio
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # direcciones IP
        r"(?::\d+)?"  # puerto opcional
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(patron.match(url))


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id,  created, author_id, accUsername,accCookieName"
        " FROM asociatedAccounts p JOIN user u ON p.author_id = u.id"
        " WHERE p.author_id = ?"
        " ORDER BY created DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        accCookieName = request.form["CookieName"]
        accUsername = request.form["AccUser"]
        accPassword = request.form["AccPass"]
        file = request.files["file"]

        error = None

        if not accCookieName:
            error = "Cokkie name is required"

        if not accUsername:
            error = "Account username is required"
        if os.path.exists(f"flaskr/sessions/{accCookieName}.pkl"):
            error = "This cookie name  is already in use"

        else:
            if file.filename.endswith(".pkl"):
                file.save(f"flaskr/sessions/{accCookieName}.pkl")
            else:
                error = "Your file extension is not valid"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO asociatedAccounts (accUsername,accPassword, accCookieName,author_id)"
                " VALUES (?, ?, ?,?)",
                (accUsername, accPassword, accCookieName, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id,  created, author_id, accUsername,accPassword,accCookieName, publicationText,groupsConf,publicationConf,logs"
            " FROM asociatedAccounts p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        accCookieName = request.form["CookieName"]
        accUsername = request.form["AccUser"]
        accPassword = request.form["AccPass"]
        file = request.files["file"]
        error = None

        if not accCookieName:
            error = "Cokkie name is required"

        if not accUsername:
            error = "Account username is required"

        if file.filename.endswith(".pkl"):
            os.remove(f"flaskr/sessions/{post['accCookieName']}.pkl")
            file.save(f"flaskr/sessions/{accCookieName}.pkl")
        else:
            error = "Your file extension is not valid"
        if error is not None:
            flash(error)
        else:
            db = get_db()
            post = db.execute(
                "SELECT * FROM asociatedAccounts WHERE id = ?", (id,)
            ).fetchone()

            db.execute(
                "UPDATE asociatedAccounts SET accCookieName = ?,  accPassword = ? , accUsername = ?"
                " WHERE id = ?",
                (accCookieName, accUsername, accPassword, id),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    post = db.execute("SELECT * FROM asociatedAccounts WHERE id = ?", (id,)).fetchone()
    os.remove(f"sessions/{post['accCookieName']}.pkl")
    db.execute("DELETE FROM asociatedAccounts WHERE id = ?", (id,))
    db.commit()
    flash(f"Account  {post['accUsername']} deleted")

    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/config", methods=("GET", "POST"))
@login_required
def config(id):
    post = get_post(id)
    try:
        groups = json.loads(post["groupsConf"])
    except json.JSONDecodeError:
        groups = {}
    try:
        publications = json.loads(post["publicationConf"])
    except json.JSONDecodeError:
        publications = {}

    groupsList = ""
    publicationsList = ""

    for key in groups:
        groupsList += f"{key}\n"
    for key in publications:
        publicationsList += f"{key}\n"

    if request.method == "POST":
        groupsConf = request.form["groups"]
        publicationConf = request.form["publication"]
        publicationText = request.form["text"]
        error = None
        groupsInput = {}
        publicationInput = {}
        if not groupsConf:
            error = "Group list is NULL"

        if not publicationConf:
            error = "Publication list is NULL"
        if publicationText == "None":
            error = "Text is NULL"

        groupsConf = groupsConf.replace("\r", "")
        publicationConf = publicationConf.replace("\r", "")
        for url in groupsConf.split("\n"):
            if es_enlace(url):
                groupsInput[url] = {"name": "None", "state": "ok"}

        for url in publicationConf.split("\n"):
            if es_enlace(url):
                publicationInput[url] = {"state": "ok"}

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE asociatedAccounts SET  groupsConf = ?,  publicationConf = ?, publicationText = ?"
                " WHERE id = ?",
                (
                    json.dumps(groupsInput),
                    json.dumps(publicationInput),
                    publicationText,
                    id,
                ),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template(
        "blog/config.html", groups=groupsList, publications=publicationsList, post=post
    )


@bp.route("/<int:id>/send", methods=("GET", "POST"))
@login_required
def send(id):
    post = get_post(id)
    try:
        groups = json.loads(post["groupsConf"])
    except json.JSONDecodeError:
        groups = {}
    try:
        publications = json.loads(post["publicationConf"])
    except json.JSONDecodeError:
        publications = {}

    groupsList = []
    publicationsList = []
    cookie_ = post["accCookieName"]
    pass_ = post["accPassword"]
    text = post["publicationText"]

    for key in groups:
        groupsList.append(key)
    for key in publications:
        publicationsList.append(key)
        
    if api.CheckThreadState(post["accCookieName"]):
        flash("Esa cuenta tiene un proceso asociado en ejecucion")
        
        return redirect(url_for("blog.index"))
    api.PublicationProcess(cookie_, pass_, groupsList, text)
    flash("Tarea agregada con exito")
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/share", methods=("GET", "POST"))
@login_required
def share(id):
    post = get_post(id)
    try:
        groups = json.loads(post["groupsConf"])
    except json.JSONDecodeError:
        groups = {}
    try:
        publications = json.loads(post["publicationConf"])
    except json.JSONDecodeError:
        publications = {}

    groupsList = []
    publicationsList = []
    cookie_ = post["accCookieName"]
    pass_ = post["accPassword"]

    for key in groups:
        groupsList.append(key)
    for key in publications:
        publicationsList.append(key)
        
    if api.CheckThreadState(post["accCookieName"]):
        flash("Esa cuenta tiene un proceso asociado en ejecucion")
        
        return redirect(url_for("blog.index"))
        
    api.ShareProcess(f"{cookie_}", pass_, groupsList, publicationsList)
    flash("Tarea agregada con exito")
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/logs", methods=("GET", "POST"))
@login_required
def logs(id):
    post = get_post(id)

    return render_template(
        "blog/logs.html", post=post, state=api.CheckThreadState(post["accCookieName"])
    )
