from functools import wraps
from flask import session, redirect, url_for, flash


def clear_user_sessions():
    for key in [
        "admin_id", "mauricio_id", "mauricio_nome",
        "recrutador_id", "recrutador_nome", "recrutador_empresa", "recrutador_status",
        "vigilante_id", "vigilante_nome",
    ]:
        session.pop(key, None)
from utils.db import get_connection


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            flash("Faça login para acessar o painel administrativo.", "info")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    return wrapped


def mauricio_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "mauricio_id" not in session:
            flash("Faça login para acessar o painel do Maurício.", "info")
            return redirect(url_for("mauricio.login"))
        return view_func(*args, **kwargs)

    return wrapped


def recrutador_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        recrutador_id = session.get("recrutador_id")
        if not recrutador_id:
            flash("Faça login para acessar o painel dos recrutadores.", "info")
            return redirect(url_for("recrutador.login"))

        conn = get_connection()
        recrutador = conn.execute(
            "SELECT id, nome_responsavel, nome_empresa, status, email_verificado, antifraude_status FROM recrutadores WHERE id = ?",
            (recrutador_id,),
        ).fetchone()
        conn.close()

        if not recrutador:
            session.pop("recrutador_id", None)
            session.pop("recrutador_nome", None)
            session.pop("recrutador_empresa", None)
            session.pop("recrutador_status", None)
            flash("Recrutador não encontrado. Faça login novamente.", "error")
            return redirect(url_for("recrutador.login"))

        status = (recrutador["status"] or "").strip().lower()
        if status == "ativo":
            status = "validado"

        session["recrutador_nome"] = recrutador["nome_responsavel"]
        session["recrutador_empresa"] = recrutador["nome_empresa"]
        session["recrutador_status"] = status

        if (recrutador["antifraude_status"] or "normal").strip().lower() == "bloqueado":
            clear_user_sessions()
            flash("Seu cadastro de recrutador foi bloqueado para revisão de segurança.", "error")
            return redirect(url_for("recrutador.login"))

        if int(recrutador["email_verificado"] or 0) != 1:
            session.pop("recrutador_id", None)
            session.pop("recrutador_nome", None)
            session.pop("recrutador_empresa", None)
            session.pop("recrutador_status", None)
            flash("Valide o e-mail do recrutador antes de acessar o painel.", "error")
            return redirect(url_for("recrutador.login"))

        if status not in {"validado", "verificado"}:
            session.pop("recrutador_id", None)
            session.pop("recrutador_nome", None)
            session.pop("recrutador_empresa", None)
            session.pop("recrutador_status", None)
            flash("Seu acesso de recrutador ainda não foi liberado pelo painel do Maurício.", "error")
            return redirect(url_for("recrutador.login"))

        return view_func(*args, **kwargs)

    return wrapped


def vigilante_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        vigilante_id = session.get("vigilante_id")
        if not vigilante_id:
            flash("Faça login para acessar sua área de candidato.", "info")
            return redirect(url_for("vigilante.login"))

        conn = get_connection()
        vigilante = conn.execute(
            "SELECT id, nome, status, antifraude_status FROM vigilantes WHERE id = ?",
            (vigilante_id,),
        ).fetchone()
        conn.close()

        if not vigilante:
            clear_user_sessions()
            flash("Vigilante não encontrado. Faça login novamente.", "error")
            return redirect(url_for("vigilante.login"))

        if (vigilante["antifraude_status"] or "normal").strip().lower() == "bloqueado":
            clear_user_sessions()
            flash("Seu cadastro de vigilante foi bloqueado para revisão de segurança.", "error")
            return redirect(url_for("vigilante.login"))

        if (vigilante["status"] or "").strip().lower() != "ativo":
            clear_user_sessions()
            flash("Seu acesso de vigilante não está ativo neste momento.", "error")
            return redirect(url_for("vigilante.login"))

        session["vigilante_nome"] = vigilante["nome"]
        return view_func(*args, **kwargs)

    return wrapped
