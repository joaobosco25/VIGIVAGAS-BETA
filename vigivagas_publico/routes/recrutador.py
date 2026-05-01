import hashlib
import os
import secrets
from datetime import datetime, timedelta
from secrets import randbelow

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from utils.auth import clear_user_sessions, recrutador_required
from utils.captcha import generate_captcha, verify_captcha
from utils.cnpj_service import consultar_cnpj
from utils.db import get_connection
from utils.fraud import evaluate_recrutador_risk, get_client_ip, get_user_agent, is_disposable_email, looks_like_test_company, looks_like_test_name
from utils.email_service import send_email_token, send_password_reset_link
from utils.validators import (
    format_cnpj,
    format_phone,
    is_strong_password,
    is_valid_phone,
    is_valid_state_code,
    has_meaningful_length,
    normalize_email,
    normalize_textarea_upper,
    normalize_upper,
)

recrutador_bp = Blueprint("recrutador", __name__, url_prefix="/recrutador")


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _base_url() -> str:
    configured = (os.getenv("APP_BASE_URL", "") or "").strip().rstrip("/")
    if configured:
        return configured
    return request.url_root.rstrip("/")


def _create_password_reset(conn, user_type: str, user_id: int) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = _hash_reset_token(token)
    expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    conn.execute(
        """
        INSERT INTO password_resets (user_type, user_id, token_hash, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_type, user_id, token_hash, expires_at),
    )
    return token


def _find_valid_password_reset(conn, user_type: str, token: str):
    token_hash = _hash_reset_token(token)
    reset = conn.execute(
        """
        SELECT * FROM password_resets
        WHERE user_type = ? AND token_hash = ? AND used_at IS NULL
        """,
        (user_type, token_hash),
    ).fetchone()
    if not reset:
        return None
    try:
        expires_at = datetime.fromisoformat(str(reset["expires_at"]))
    except Exception:
        return None
    if expires_at < datetime.utcnow():
        return None
    return reset


STATUS_CANDIDATURA = [
    "Recebida",
    "Em análise",
    "Entrevista",
    "Aprovado",
    "Reprovado",
]

LIMITE_VAGAS_ATIVAS = {
    "validado": 5,
    "verificado": 15,
}



def _resolve_recrutador_status(raw_status: str | None) -> str:
    status = (raw_status or "").strip().lower()
    return "validado" if status == "ativo" else status


def _can_manage_vagas(raw_status: str | None) -> bool:
    return _resolve_recrutador_status(raw_status) in {"validado", "verificado"}


def _generate_email_token() -> tuple[str, str]:
    # Código numérico de 5 dígitos para validação por e-mail.
    token = f"{randbelow(100000):05d}"
    expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
    return token, expires_at


def _emitir_token_para_recrutador(conn, recrutador_id: int, email: str) -> str:
    token, expires_at = _generate_email_token()
    conn.execute(
        """
        UPDATE recrutadores
        SET email_token = ?,
            email_token_expires_at = ?,
            email_ultimo_envio_em = ?,
            email_verificado = 0
        WHERE id = ?
        """,
        (token, expires_at, datetime.utcnow().isoformat(), recrutador_id),
    )
    conn.commit()
    _, mensagem_envio = send_email_token(email, token)
    return mensagem_envio


def _registrar_consentimento_lgpd(conn, user_type: str, user_id, email: str):
    texto = "Aceite da Política de Privacidade e Termos de Uso do VigiVagas."
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "")[:500]
    conn.execute(
        """
        INSERT INTO lgpd_consents (user_type, user_id, email, policy_version, terms_version, consent_text, ip_address, user_agent)
        VALUES (?, ?, ?, '1.0', '1.0', ?, ?, ?)
        """,
        (user_type, user_id, email, texto, ip, ua),
    )


@recrutador_bp.route("/")
def root():
    return redirect(url_for("recrutador.login"))


@recrutador_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if session.get("recrutador_id"):
        flash("Você já está autenticado como recrutador.", "info")
        return redirect(url_for("recrutador.dashboard"))

    if request.method == "GET" and session.pop("recrutador_cadastro_concluido", False):
        flash("Seu cadastro já foi concluído. Faça login para continuar.", "info")
        return redirect(url_for("recrutador.login"))

    if request.method == "POST":
        if request.form.get("aceite_lgpd") != "1":
            flash("Para continuar, aceite a Política de Privacidade e os Termos de Uso.", "error")
            return redirect(url_for("recrutador.cadastro"))

        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)

        dados = {
            "nome_empresa": normalize_upper(request.form.get("nome_empresa", "")),
            "nome_responsavel": normalize_upper(request.form.get("nome_responsavel", "")),
            "email": normalize_email(request.form.get("email", "")),
            "telefone": format_phone(request.form.get("telefone", "")),
            "cidade": normalize_upper(request.form.get("cidade", "")),
            "estado": normalize_upper(request.form.get("estado", ""))[:2],
            "cnpj": format_cnpj(request.form.get("cnpj", "")),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", ""),
        }
        captcha_resposta = request.form.get("captcha_resposta", "")

        obrigatorios = ["nome_empresa", "nome_responsavel", "email", "telefone", "cidade", "estado", "cnpj", "password", "confirm_password"]
        faltando = [campo for campo in obrigatorios if not dados[campo]]
        if faltando:
            flash("Preencha todos os campos obrigatórios do recrutador.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if not verify_captcha("recrutador_cadastro", captcha_resposta):
            flash("CAPTCHA inválido. Resolva a conta corretamente para continuar.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if not is_valid_phone(dados["telefone"]):
            flash("Informe um telefone válido com DDD.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if not is_valid_state_code(dados["estado"]):
            flash("Informe uma UF válida com 2 letras.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if not has_meaningful_length(dados["nome_empresa"], 5) or looks_like_test_company(dados["nome_empresa"]):
            flash("Informe uma empresa real. Cadastros de teste ou genéricos são bloqueados.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if not has_meaningful_length(dados["nome_responsavel"], 8) or looks_like_test_name(dados["nome_responsavel"]):
            flash("Informe o nome completo real do responsável pela empresa.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if is_disposable_email(dados["email"]):
            flash("E-mails temporários ou descartáveis não são aceitos para empresas.", "error")
            return redirect(url_for("recrutador.cadastro"))

        cnpj_ok, cnpj_msg, cnpj_dados = consultar_cnpj(dados["cnpj"])
        if not cnpj_ok:
            flash(cnpj_msg, "error")
            return redirect(url_for("recrutador.cadastro"))

        if dados["password"] != dados["confirm_password"]:
            flash("As senhas do recrutador não conferem.", "error")
            return redirect(url_for("recrutador.cadastro"))

        if not is_strong_password(dados["password"]):
            flash("A senha deve ter no mínimo 10 caracteres, letra maiúscula, minúscula, número e caractere especial.", "error")
            return redirect(url_for("recrutador.cadastro"))

        conn = get_connection()
        existente = conn.execute(
            "SELECT id FROM recrutadores WHERE email = ?",
            (dados["email"],),
        ).fetchone()
        if existente:
            conn.close()
            flash("Já existe recrutador cadastrado com este e-mail.", "error")
            return redirect(url_for("recrutador.login"))

        cnpj_existente = conn.execute(
            "SELECT id FROM recrutadores WHERE cnpj = ?",
            (cnpj_dados["cnpj"],),
        ).fetchone()
        if cnpj_existente:
            conn.close()
            flash("Já existe solicitação de recrutador para este CNPJ. Isso ajuda a impedir empresas fantasmas ou duplicadas.", "error")
            return redirect(url_for("recrutador.login"))

        antifraude_score, antifraude_flags, antifraude_status = evaluate_recrutador_risk(
            conn,
            dados["nome_empresa"],
            dados["nome_responsavel"],
            dados["email"],
            dados["telefone"],
            cnpj_dados["cnpj"],
            client_ip,
            user_agent,
        )

        conn.execute(
            """
            INSERT INTO recrutadores (
                nome_empresa,
                nome_responsavel,
                email,
                telefone,
                cidade,
                estado,
                cnpj,
                razao_social,
                situacao_cadastral,
                cnpj_modo_validacao,
                ip_cadastro,
                user_agent,
                antifraude_score,
                antifraude_flags,
                antifraude_status,
                password,
                status,
                email_verificado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendente', 0)
            """,
            (
                dados["nome_empresa"],
                dados["nome_responsavel"],
                dados["email"],
                dados["telefone"],
                dados["cidade"],
                dados["estado"],
                cnpj_dados["cnpj"],
                cnpj_dados["razao_social"] or dados["nome_empresa"],
                cnpj_dados["situacao_cadastral"],
                cnpj_dados.get("modo_validacao", "online"),
                client_ip,
                user_agent,
                antifraude_score,
                antifraude_flags,
                antifraude_status,
                generate_password_hash(dados["password"]),
            ),
        )
        recrutador_id = conn.execute(
            "SELECT id FROM recrutadores WHERE email = ?",
            (dados["email"],),
        ).fetchone()["id"]
        mensagem_envio = _emitir_token_para_recrutador(conn, recrutador_id, dados["email"])
        conn.close()
        session["recrutador_cadastro_concluido"] = True
        flash(cnpj_msg, "info")
        flash("Cadastro de recrutador enviado com sucesso. Enviamos um código de 5 números para validar seu e-mail.", "success")
        if antifraude_status == "suspeito":
            flash("O cadastro da empresa foi sinalizado para revisão preventiva de segurança.", "info")
        flash(mensagem_envio, "info")
        return redirect(url_for("recrutador.validar_email", email=dados["email"]))

    return render_template("recrutador/cadastro.html", captcha_question=generate_captcha("recrutador_cadastro"))


@recrutador_bp.route("/validar-email", methods=["GET", "POST"])
def validar_email():
    email = normalize_email(request.values.get("email", ""))
    token = (request.values.get("token", "") or "").strip()

    if request.method == "GET":
        return render_template("recrutador/validar_email.html", email=email)

    if not email:
        flash("Informe o e-mail do recrutador para validar.", "error")
        return redirect(url_for("recrutador.validar_email"))

    if not token or len(token) != 5 or not token.isdigit():
        flash("Informe o código de 5 números enviado para o e-mail.", "error")
        return redirect(url_for("recrutador.validar_email", email=email))

    conn = get_connection()
    recrutador = conn.execute(
        """
        SELECT id, email, email_verificado, email_token, email_token_expires_at
        FROM recrutadores
        WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if not recrutador:
        conn.close()
        flash("Não encontramos recrutador com esse e-mail.", "error")
        return redirect(url_for("recrutador.validar_email"))

    if int(recrutador["email_verificado"] or 0) == 1:
        conn.close()
        flash("Este e-mail já está validado. Faça login para continuar.", "info")
        return redirect(url_for("recrutador.login"))

    if (recrutador["email_token"] or "").strip() != token:
        conn.close()
        flash("Código de validação inválido.", "error")
        return redirect(url_for("recrutador.validar_email", email=email))

    expires_at = recrutador["email_token_expires_at"] or ""
    try:
        expirado = datetime.utcnow() > datetime.fromisoformat(expires_at)
    except Exception:
        expirado = True

    if expirado:
        conn.close()
        flash("O código de validação expirou. Solicite um novo envio.", "error")
        return redirect(url_for("recrutador.validar_email", email=email))

    conn.execute(
        """
        UPDATE recrutadores
        SET email_verificado = 1,
            email_token = NULL,
            email_token_expires_at = NULL
        WHERE id = ?
        """,
        (recrutador["id"],),
    )
    conn.commit()
    conn.close()
    flash("E-mail validado com sucesso. Agora o acesso continua pendente até a análise do Maurício.", "success")
    return redirect(url_for("recrutador.login"))


@recrutador_bp.route("/reenviar-validacao", methods=["POST"])
def reenviar_validacao():
    email = normalize_email(request.form.get("email", ""))
    if not email:
        flash("Informe o e-mail do recrutador para reenviar a validação.", "error")
        return redirect(url_for("recrutador.login"))

    conn = get_connection()
    recrutador = conn.execute(
        "SELECT id, email, email_verificado FROM recrutadores WHERE email = ?",
        (email,),
    ).fetchone()
    if not recrutador:
        conn.close()
        flash("Não encontramos recrutador com esse e-mail.", "error")
        return redirect(url_for("recrutador.login"))

    if int(recrutador["email_verificado"] or 0) == 1:
        conn.close()
        flash("Este e-mail já está validado.", "info")
        return redirect(url_for("recrutador.login"))

    mensagem_envio = _emitir_token_para_recrutador(conn, recrutador["id"], recrutador["email"])
    conn.close()
    flash(mensagem_envio, "info")
    return redirect(url_for("recrutador.validar_email", email=email))


@recrutador_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("recrutador_id"):
        return redirect(url_for("recrutador.dashboard"))

    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")

        conn = get_connection()
        recrutador = conn.execute(
            "SELECT * FROM recrutadores WHERE email = ?",
            (email,),
        ).fetchone()
        conn.close()

        if recrutador and check_password_hash(recrutador["password"], password):
            if int(recrutador["email_verificado"] or 0) != 1:
                flash("Antes de acessar, valide o e-mail do recrutador com o código enviado.", "error")
                return redirect(url_for("recrutador.validar_email", email=email))

            status = (recrutador["status"] or "").strip().lower()
            if status == "ativo":
                status = "validado"

            if status not in {"validado", "verificado"}:
                flash("Seu cadastro foi recebido, mas ainda está pendente de análise pelo painel do Maurício.", "info")
                return redirect(url_for("recrutador.login"))

            if (recrutador["antifraude_status"] or "normal").strip().lower() == "bloqueado":
                flash("O cadastro da empresa foi bloqueado para revisão de segurança.", "error")
                return redirect(url_for("recrutador.login"))

            clear_user_sessions()
            session["recrutador_id"] = recrutador["id"]
            session["recrutador_nome"] = recrutador["nome_responsavel"]
            session["recrutador_empresa"] = recrutador["nome_empresa"]
            session["recrutador_status"] = status
            return redirect(url_for("recrutador.dashboard"))

        flash("E-mail ou senha inválidos para o recrutador.", "error")

    return render_template("recrutador/login.html")


@recrutador_bp.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        if not email:
            flash("Informe o e-mail do recrutador para redefinir a senha.", "error")
            return redirect(url_for("recrutador.esqueci_senha"))

        conn = get_connection()
        recrutador = conn.execute("SELECT id, email FROM recrutadores WHERE email = ?", (email,)).fetchone()
        if recrutador:
            token = _create_password_reset(conn, "recrutador", recrutador["id"])
            conn.commit()
            reset_url = f"{_base_url()}{url_for('recrutador.redefinir_senha', token=token)}"
            ok, mensagem = send_password_reset_link(recrutador["email"], reset_url, "recrutador")
            flash(mensagem, "success" if ok else "error")
        else:
            flash("Se o e-mail estiver cadastrado, enviaremos um link de redefinição de senha.", "success")
        conn.close()
        return redirect(url_for("recrutador.login"))

    return render_template("recrutador/esqueci_senha.html")


@recrutador_bp.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    conn = get_connection()
    reset = _find_valid_password_reset(conn, "recrutador", token)
    if not reset:
        conn.close()
        flash("Link de redefinição inválido ou expirado. Solicite um novo link.", "error")
        return redirect(url_for("recrutador.esqueci_senha"))

    if request.method == "POST":
        senha = request.form.get("password", "")
        confirmar = request.form.get("confirm_password", "")
        if senha != confirmar:
            conn.close()
            flash("A confirmação de senha não confere.", "error")
            return redirect(url_for("recrutador.redefinir_senha", token=token))
        if not is_strong_password(senha):
            conn.close()
            flash("Use uma senha forte com pelo menos 10 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial.", "error")
            return redirect(url_for("recrutador.redefinir_senha", token=token))

        conn.execute("UPDATE recrutadores SET password = ? WHERE id = ?", (generate_password_hash(senha), reset["user_id"]))
        conn.execute("UPDATE password_resets SET used_at = ? WHERE id = ?", (datetime.utcnow().isoformat(), reset["id"]))
        conn.commit()
        conn.close()
        clear_user_sessions()
        flash("Senha alterada com sucesso. Faça login com a nova senha.", "success")
        return redirect(url_for("recrutador.login"))

    conn.close()
    return render_template("recrutador/redefinir_senha.html", token=token)


@recrutador_bp.route("/dashboard")
@recrutador_required
def dashboard():
    recrutador_id = session["recrutador_id"]
    vagas_limit = max(5, min(request.args.get("vagas_limit", 10, type=int), 100))
    conn = get_connection()

    recrutador = conn.execute(
        "SELECT id, nome_empresa, nome_responsavel, status, site_empresa, descricao_empresa FROM recrutadores WHERE id = ?",
        (recrutador_id,),
    ).fetchone()
    recrutador_status = _resolve_recrutador_status(
        (recrutador["status"] if recrutador else session.get("recrutador_status", ""))
    )

    resumo = {
        "vagas_publicadas": conn.execute(
            "SELECT COUNT(*) AS total FROM vagas WHERE recrutador_id = ?",
            (recrutador_id,),
        ).fetchone()["total"],
        "candidaturas": conn.execute(
            "SELECT COUNT(*) AS total FROM candidaturas c JOIN vagas v ON v.id = c.vaga_id WHERE v.recrutador_id = ?",
            (recrutador_id,),
        ).fetchone()["total"],
        "vagas_ativas": conn.execute(
            "SELECT COUNT(*) AS total FROM vagas WHERE recrutador_id = ? AND status = 'ativa'",
            (recrutador_id,),
        ).fetchone()["total"],
    }

    vagas = conn.execute(
        """
        SELECT
            v.id,
            v.titulo,
            v.empresa,
            v.cidade,
            v.estado,
            v.status,
            v.created_at,
            COUNT(c.id) AS total_candidaturas
        FROM vagas v
        LEFT JOIN candidaturas c ON c.vaga_id = v.id
        WHERE v.recrutador_id = ?
        GROUP BY v.id, v.titulo, v.empresa, v.cidade, v.estado, v.status, v.created_at
        ORDER BY v.id DESC
        LIMIT ?
        """,
        (recrutador_id, vagas_limit),
    ).fetchall()
    conn.close()

    return render_template(
        "recrutador/dashboard.html",
        resumo=resumo,
        vagas=vagas,
        recrutador=recrutador,
        recrutador_status=recrutador_status,
        limite_vagas_ativas=LIMITE_VAGAS_ATIVAS.get(recrutador_status, 0),
        vagas_limit=vagas_limit,
        pode_mostrar_mais_vagas=resumo["vagas_publicadas"] > vagas_limit,
    )


@recrutador_bp.route("/vagas/nova", methods=["POST"])
@recrutador_required
def nova_vaga():
    conn = get_connection()
    recrutador = conn.execute(
        "SELECT status FROM recrutadores WHERE id = ?",
        (session["recrutador_id"],),
    ).fetchone()
    conn.close()

    status = ((recrutador["status"] if recrutador else "") or "").strip().lower()
    if status == "ativo":
        status = "validado"

    if status not in {"validado", "verificado"}:
        flash("Seu perfil de recrutador não está liberado para publicar vagas.", "error")
        return redirect(url_for("recrutador.dashboard"))

    conn = get_connection()
    vagas_ativas = conn.execute(
        "SELECT COUNT(*) AS total FROM vagas WHERE recrutador_id = ? AND status = 'ativa'",
        (session["recrutador_id"],),
    ).fetchone()["total"]
    limite = LIMITE_VAGAS_ATIVAS.get(status, 0)
    if limite and vagas_ativas >= limite:
        conn.close()
        flash(f"Seu plano atual permite até {limite} vagas ativas simultâneas.", "error")
        return redirect(url_for("recrutador.dashboard"))

    dados = {
        "titulo": normalize_upper(request.form.get("titulo", "")),
        "empresa": normalize_upper(request.form.get("empresa", "")),
        "cidade": normalize_upper(request.form.get("cidade", "")),
        "estado": normalize_upper(request.form.get("estado", ""))[:2],
        "escala": normalize_upper(request.form.get("escala", "")),
        "salario": normalize_upper(request.form.get("salario", "")),
        "descricao": normalize_textarea_upper(request.form.get("descricao", "")),
        "requisitos": normalize_textarea_upper(request.form.get("requisitos", "")),
        "contato": normalize_upper(request.form.get("contato", "")),
    }

    obrigatorios = ["titulo", "empresa", "cidade", "estado", "descricao"]
    faltando = [campo for campo in obrigatorios if not dados[campo]]
    if faltando:
        flash("Preencha todos os campos obrigatórios da vaga.", "error")
        return redirect(url_for("recrutador.dashboard"))

    conn.execute(
        """
        INSERT INTO vagas (
            titulo,
            empresa,
            cidade,
            estado,
            escala,
            salario,
            descricao,
            requisitos,
            contato,
            recrutador_id,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ativa')
        """,
        (
            dados["titulo"],
            dados["empresa"],
            dados["cidade"],
            dados["estado"],
            dados["escala"],
            dados["salario"],
            dados["descricao"],
            dados["requisitos"],
            dados["contato"],
            session["recrutador_id"],
        ),
    )
    conn.commit()
    conn.close()

    flash("Vaga publicada com sucesso.", "success")
    return redirect(url_for("recrutador.dashboard"))



@recrutador_bp.route("/vaga/<int:vaga_id>/editar", methods=["GET", "POST"])
@recrutador_required
def editar_vaga(vaga_id: int):
    recrutador_id = session["recrutador_id"]
    conn = get_connection()
    recrutador = conn.execute(
        "SELECT id, status, nome_empresa FROM recrutadores WHERE id = ?",
        (recrutador_id,),
    ).fetchone()
    recrutador_status = _resolve_recrutador_status(recrutador["status"] if recrutador else "")

    if not _can_manage_vagas(recrutador_status):
        conn.close()
        flash("Seu perfil de recrutador não está liberado para editar vagas.", "error")
        return redirect(url_for("recrutador.dashboard"))

    vaga = conn.execute(
        "SELECT * FROM vagas WHERE id = ? AND recrutador_id = ?",
        (vaga_id, recrutador_id),
    ).fetchone()
    if not vaga:
        conn.close()
        flash("Vaga não encontrada para este recrutador.", "error")
        return redirect(url_for("recrutador.dashboard"))

    if request.method == "POST":
        dados = {
            "titulo": normalize_upper(request.form.get("titulo", "")),
            "empresa": normalize_upper(request.form.get("empresa", "")),
            "cidade": normalize_upper(request.form.get("cidade", "")),
            "estado": normalize_upper(request.form.get("estado", ""))[:2],
            "escala": normalize_upper(request.form.get("escala", "")),
            "salario": normalize_upper(request.form.get("salario", "")),
            "descricao": normalize_textarea_upper(request.form.get("descricao", "")),
            "requisitos": normalize_textarea_upper(request.form.get("requisitos", "")),
            "contato": normalize_upper(request.form.get("contato", "")),
        }

        obrigatorios = ["titulo", "empresa", "cidade", "estado", "descricao"]
        faltando = [campo for campo in obrigatorios if not dados[campo]]
        if faltando:
            conn.close()
            flash("Preencha todos os campos obrigatórios da vaga.", "error")
            return redirect(url_for("recrutador.editar_vaga", vaga_id=vaga_id))

        conn.execute(
            """
            UPDATE vagas
            SET titulo = ?,
                empresa = ?,
                cidade = ?,
                estado = ?,
                escala = ?,
                salario = ?,
                descricao = ?,
                requisitos = ?,
                contato = ?
            WHERE id = ?
              AND recrutador_id = ?
            """,
            (
                dados["titulo"],
                dados["empresa"],
                dados["cidade"],
                dados["estado"],
                dados["escala"],
                dados["salario"],
                dados["descricao"],
                dados["requisitos"],
                dados["contato"],
                vaga_id,
                recrutador_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Vaga atualizada com sucesso.", "success")
        return redirect(url_for("recrutador.dashboard", _anchor="gestao-vagas"))

    conn.close()
    return render_template(
        "recrutador/editar_vaga.html",
        vaga=vaga,
        recrutador_status=recrutador_status,
    )


@recrutador_bp.route("/perfil-empresa", methods=["POST"])
@recrutador_required
def atualizar_perfil_empresa():
    if (session.get("recrutador_status") or "").strip().lower() != "verificado":
        flash("Somente recrutadores verificados podem personalizar o perfil público da empresa.", "error")
        return redirect(url_for("recrutador.dashboard"))

    site_empresa = request.form.get("site_empresa", "").strip()
    descricao_empresa = normalize_textarea_upper(request.form.get("descricao_empresa", ""))

    if site_empresa and not (site_empresa.startswith("http://") or site_empresa.startswith("https://")):
        site_empresa = f"https://{site_empresa}"

    if site_empresa and len(site_empresa) < 10:
        flash("Informe um site corporativo válido ou deixe o campo em branco.", "error")
        return redirect(url_for("recrutador.dashboard"))

    if descricao_empresa and len(descricao_empresa) < 30:
        flash("A apresentação pública da empresa precisa ter pelo menos 30 caracteres.", "error")
        return redirect(url_for("recrutador.dashboard"))

    conn = get_connection()
    conn.execute(
        "UPDATE recrutadores SET site_empresa = ?, descricao_empresa = ? WHERE id = ?",
        (site_empresa or None, descricao_empresa or None, session["recrutador_id"]),
    )
    conn.commit()
    conn.close()
    flash("Perfil público da empresa atualizado com sucesso.", "success")
    return redirect(url_for("recrutador.dashboard"))


@recrutador_bp.route("/vaga/<int:vaga_id>/candidatos", methods=["GET", "POST"])
@recrutador_required
def candidatos_da_vaga(vaga_id: int):
    recrutador_id = session["recrutador_id"]
    conn = get_connection()

    vaga = conn.execute(
        "SELECT * FROM vagas WHERE id = ? AND recrutador_id = ?",
        (vaga_id, recrutador_id),
    ).fetchone()
    if not vaga:
        conn.close()
        flash("Vaga não encontrada para este recrutador.", "error")
        return redirect(url_for("recrutador.dashboard"))

    if request.method == "POST":
        candidatura_id = request.form.get("candidatura_id", type=int)
        novo_status = request.form.get("status", "").strip()
        observacoes = normalize_textarea_upper(request.form.get("observacoes", ""))

        if novo_status not in STATUS_CANDIDATURA:
            conn.close()
            flash("Status de candidatura inválido.", "error")
            return redirect(url_for("recrutador.candidatos_da_vaga", vaga_id=vaga_id))

        conn.execute(
            """
            UPDATE candidaturas
            SET status = ?,
                observacoes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND vaga_id = ?
            """,
            (novo_status, observacoes, candidatura_id, vaga_id),
        )
        conn.commit()
        flash("Candidatura atualizada com sucesso.", "success")

    candidatos = conn.execute(
        """
        SELECT
            c.id AS candidatura_id,
            c.status,
            c.observacoes,
            c.created_at,
            vgl.id AS vigilante_id,
            vgl.nome,
            vgl.email,
            vgl.telefone,
            vgl.cidade,
            vgl.curso,
            vgl.reciclagem,
            vgl.area_interesse,
            vgl.resumo_profissional
        FROM candidaturas c
        JOIN vigilantes vgl ON vgl.id = c.vigilante_id
        WHERE c.vaga_id = ?
        ORDER BY c.id DESC
        """,
        (vaga_id,),
    ).fetchall()
    conn.close()

    return render_template(
        "recrutador/candidatos_vaga.html",
        vaga=vaga,
        candidatos=candidatos,
        status_opcoes=STATUS_CANDIDATURA,
    )


@recrutador_bp.route("/logout", methods=["POST"])
@recrutador_required
def logout():
    clear_user_sessions()
    flash("Sessão do recrutador encerrada com sucesso.", "success")
    return redirect(url_for("recrutador.login"))


@recrutador_bp.route("/meus-dados.json")
@recrutador_required
def meus_dados_json():
    import json
    from flask import Response
    conn = get_connection()
    recrutador = conn.execute("SELECT id, nome_empresa, nome_responsavel, email, telefone, cidade, estado, cnpj, razao_social, situacao_cadastral, site_empresa, descricao_empresa, status, email_verificado, created_at FROM recrutadores WHERE id = ?", (session["recrutador_id"],)).fetchone()
    vagas = conn.execute("SELECT id, titulo, empresa, cidade, estado, escala, salario, descricao, requisitos, status, created_at FROM vagas WHERE recrutador_id = ? ORDER BY id DESC", (session["recrutador_id"],)).fetchall()
    conn.close()
    payload = {"perfil_empresa": dict(recrutador) if recrutador else {}, "vagas": [dict(x) for x in vagas]}
    return Response(json.dumps(payload, ensure_ascii=False, default=str, indent=2), mimetype="application/json", headers={"Content-Disposition":"attachment; filename=recrutador_meus_dados.json"})


@recrutador_bp.route("/excluir-conta", methods=["POST"])
@recrutador_required
def excluir_conta():
    recrutador_id = session["recrutador_id"]
    conn = get_connection()
    conn.execute("UPDATE vagas SET status='inativa' WHERE recrutador_id = ?", (recrutador_id,))
    conn.execute("UPDATE recrutadores SET nome_empresa='EMPRESA ANONIMIZADA', nome_responsavel='RESPONSAVEL ANONIMIZADO', email='anonimizado-' || id || '@vigivagas.local', telefone='', cnpj='', razao_social='', site_empresa='', descricao_empresa='', status='excluido' WHERE id = ?", (recrutador_id,))
    conn.commit(); conn.close()
    clear_user_sessions()
    flash("Conta de recrutador anonimizada e vagas desativadas conforme solicitação LGPD.", "success")
    return redirect(url_for("public.index"))
