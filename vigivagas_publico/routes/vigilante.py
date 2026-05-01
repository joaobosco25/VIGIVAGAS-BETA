import hashlib
import os
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from utils.captcha import generate_captcha, verify_captcha
from werkzeug.security import generate_password_hash, check_password_hash

from utils.auth import clear_user_sessions, vigilante_required
from utils.db import get_connection
from utils.email_service import send_password_reset_link
from utils.fraud import evaluate_vigilante_risk, get_client_ip, get_user_agent, is_disposable_email, looks_like_test_name
from utils.validators import (
    format_cep,
    format_cpf,
    format_phone,
    is_strong_password,
    is_valid_cep,
    is_valid_cpf,
    is_valid_phone,
    has_meaningful_length,
    normalize_email,
    normalize_textarea_upper,
    normalize_upper,
    validate_vigilante_requirements,
    is_valid_state_code,
)

vigilante_bp = Blueprint("vigilante", __name__, url_prefix="/vigilante")


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


@vigilante_bp.route("/")
def root():
    return redirect(url_for("vigilante.login"))


@vigilante_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        if request.form.get("aceite_lgpd") != "1":
            flash("Para continuar, aceite a Política de Privacidade e os Termos de Uso.", "error")
            return redirect(url_for("vigilante.cadastro"))

        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)

        dados = {
            "email": normalize_email(request.form.get("email", "")),
            "nome": normalize_upper(request.form.get("nome", "")),
            "cpf": format_cpf(request.form.get("cpf", "")),
            "cep": format_cep(request.form.get("cep", "")),
            "endereco": normalize_upper(request.form.get("endereco", "")),
            "cidade": normalize_upper(request.form.get("cidade", "")),
            "estado": normalize_upper(request.form.get("estado", ""))[:2],
            "telefone": format_phone(request.form.get("telefone", "")),
            "objetivo_cargo": normalize_upper(request.form.get("objetivo_cargo", "")),
            "escolaridade": normalize_upper(request.form.get("escolaridade", "")),
            "possui_cfv": normalize_upper(request.form.get("possui_cfv", "")),
            "instituicao_formacao": normalize_upper(request.form.get("instituicao_formacao", "")),
            "ext_ctv": normalize_upper(request.form.get("ext_ctv", "NAO")),
            "ext_cea": normalize_upper(request.form.get("ext_cea", "NAO")),
            "ext_csp": normalize_upper(request.form.get("ext_csp", "NAO")),
            "ext_cnl1": normalize_upper(request.form.get("ext_cnl1", "NAO")),
            "ext_ces": normalize_upper(request.form.get("ext_ces", "NAO")),
            "data_ultima_reciclagem": request.form.get("data_ultima_reciclagem", "").strip(),
            "curso_ultima_reciclagem": normalize_upper(request.form.get("curso_ultima_reciclagem", "")),
            "ultima_experiencia_profissional": normalize_textarea_upper(request.form.get("ultima_experiencia_profissional", "")),
        }

        senha = request.form.get("password", "")
        confirmar_senha = request.form.get("confirm_password", "")
        captcha_resposta = request.form.get("captcha_resposta", "")
        obrigatorios = [
            "email", "nome", "cpf", "cep", "endereco", "cidade", "estado", "telefone", "escolaridade",
            "possui_cfv", "data_ultima_reciclagem", "curso_ultima_reciclagem", "ultima_experiencia_profissional",
        ]
        faltando = [campo for campo in obrigatorios if not dados[campo]]
        if faltando:
            flash("Preencha todos os campos obrigatórios do vigilante.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if dados["possui_cfv"] not in {"SIM", "NAO", "NÃO"}:
            flash("Informe corretamente se possui Curso de Formação de Vigilantes.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if dados["possui_cfv"] == "SIM" and not dados["instituicao_formacao"]:
            flash("Informe a instituição em que você se formou no CFV.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if dados["possui_cfv"] in {"NAO", "NÃO"}:
            dados["instituicao_formacao"] = ""

        if not senha or not confirmar_senha:
            flash("Crie e confirme uma senha para acessar sua área de vigilante.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if senha != confirmar_senha:
            flash("A confirmação de senha não confere.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not is_strong_password(senha):
            flash("Use uma senha forte com pelo menos 10 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not verify_captcha("vigilante_cadastro", captcha_resposta):
            flash("CAPTCHA inválido. Resolva a conta corretamente para continuar.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not is_valid_phone(dados["telefone"]):
            flash("Informe um telefone válido com DDD.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not is_valid_cpf(dados["cpf"]):
            flash("Informe um CPF válido para concluir o cadastro do vigilante.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not is_valid_state_code(dados["estado"]):
            flash("Informe uma UF válida com 2 letras.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not is_valid_cep(dados["cep"]):
            flash("Informe um CEP válido com 8 dígitos.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not has_meaningful_length(dados["nome"], 8) or looks_like_test_name(dados["nome"]):
            flash("Informe um nome completo real. Cadastros de teste ou incompletos são bloqueados.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if not has_meaningful_length(dados["endereco"], 10):
            flash("Informe um endereço mais completo para reduzir cadastros fantasmas.", "error")
            return redirect(url_for("vigilante.cadastro"))

        if is_disposable_email(dados["email"]):
            flash("E-mails temporários ou descartáveis não são aceitos.", "error")
            return redirect(url_for("vigilante.cadastro"))

        conn = get_connection()
        existente = conn.execute(
            "SELECT id FROM vigilantes WHERE email = ?",
            (dados["email"],),
        ).fetchone()
        if existente:
            conn.close()
            flash("Já existe vigilante cadastrado com este e-mail.", "error")
            return redirect(url_for("vigilante.login"))

        cpf_existente = conn.execute(
            "SELECT id FROM vigilantes WHERE cpf = ? UNION SELECT id FROM candidatos WHERE cpf = ?",
            (dados["cpf"], dados["cpf"]),
        ).fetchone()
        if cpf_existente:
            conn.close()
            flash("Já existe cadastro com este CPF. Use o login do vigilante ou contate o suporte para revisão.", "error")
            return redirect(url_for("vigilante.login"))

        antifraude_score, antifraude_flags, antifraude_status = evaluate_vigilante_risk(
            conn,
            dados["nome"],
            dados["email"],
            dados["telefone"],
            client_ip,
            user_agent,
        )

        password_hash = generate_password_hash(senha)

        conn.execute(
            """
            INSERT INTO vigilantes (
                nome, cpf, telefone, email, cidade, estado, endereco, cep, curso, reciclagem,
                area_interesse, resumo_profissional, objetivo_cargo, escolaridade,
                possui_cfv, instituicao_formacao, ext_ctv, ext_cea, ext_csp, ext_cnl1, ext_ces,
                data_ultima_reciclagem, curso_ultima_reciclagem, ultima_experiencia_profissional,
                ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status,
                password, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ativo')
            """,
            (
                dados["nome"],
                dados["cpf"],
                dados["telefone"],
                dados["email"],
                dados["cidade"],
                dados["estado"],
                dados["endereco"],
                dados["cep"],
                dados["possui_cfv"],
                dados["data_ultima_reciclagem"],
                "",
                "",
                dados["objetivo_cargo"],
                dados["escolaridade"],
                dados["possui_cfv"],
                dados["instituicao_formacao"],
                dados["ext_ctv"],
                dados["ext_cea"],
                dados["ext_csp"],
                dados["ext_cnl1"],
                dados["ext_ces"],
                dados["data_ultima_reciclagem"],
                dados["curso_ultima_reciclagem"],
                dados["ultima_experiencia_profissional"],
                client_ip,
                user_agent,
                antifraude_score,
                antifraude_flags,
                antifraude_status,
                password_hash,
            ),
        )
        novo_vigilante = conn.execute("SELECT id FROM vigilantes WHERE email = ?", (dados["email"],)).fetchone()
        _registrar_consentimento_lgpd(conn, "vigilante", novo_vigilante["id"] if novo_vigilante else None, dados["email"])
        conn.commit()
        conn.close()
        flash("Cadastro profissional enviado com sucesso. Faça login para acessar sua área de vigilante.", "success")
        if antifraude_status == "suspeito":
            flash("Cadastro salvo com sinalização preventiva para revisão administrativa.", "info")
        return redirect(url_for("vigilante.login"))

    return render_template("vigilante/cadastro.html", captcha_question=generate_captcha("vigilante_cadastro"))


@vigilante_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("vigilante_id"):
        return redirect(url_for("vigilante.dashboard"))

    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")

        conn = get_connection()
        vigilante = conn.execute(
            "SELECT * FROM vigilantes WHERE email = ?",
            (email,),
        ).fetchone()
        conn.close()

        if vigilante and check_password_hash(vigilante["password"], password):
            if (vigilante["antifraude_status"] or "normal").strip().lower() == "bloqueado":
                flash("Seu cadastro de vigilante foi bloqueado para revisão de segurança.", "error")
                return redirect(url_for("vigilante.login"))

            clear_user_sessions()
            session["vigilante_id"] = vigilante["id"]
            session["vigilante_nome"] = vigilante["nome"]
            return redirect(url_for("vigilante.dashboard"))

        flash("E-mail ou senha inválidos para o vigilante.", "error")

    return render_template("vigilante/login.html")


@vigilante_bp.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        if not email:
            flash("Informe seu e-mail para redefinir a senha.", "error")
            return redirect(url_for("vigilante.esqueci_senha"))

        conn = get_connection()
        vigilante = conn.execute("SELECT id, email FROM vigilantes WHERE email = ?", (email,)).fetchone()
        if vigilante:
            token = _create_password_reset(conn, "vigilante", vigilante["id"])
            conn.commit()
            reset_url = f"{_base_url()}{url_for('vigilante.redefinir_senha', token=token)}"
            ok, mensagem = send_password_reset_link(vigilante["email"], reset_url, "vigilante")
            flash(mensagem, "success" if ok else "error")
        else:
            flash("Se o e-mail estiver cadastrado, enviaremos um link de redefinição de senha.", "success")
        conn.close()
        return redirect(url_for("vigilante.login"))

    return render_template("vigilante/esqueci_senha.html")


@vigilante_bp.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    conn = get_connection()
    reset = _find_valid_password_reset(conn, "vigilante", token)
    if not reset:
        conn.close()
        flash("Link de redefinição inválido ou expirado. Solicite um novo link.", "error")
        return redirect(url_for("vigilante.esqueci_senha"))

    if request.method == "POST":
        senha = request.form.get("password", "")
        confirmar = request.form.get("confirm_password", "")
        if senha != confirmar:
            conn.close()
            flash("A confirmação de senha não confere.", "error")
            return redirect(url_for("vigilante.redefinir_senha", token=token))
        if not is_strong_password(senha):
            conn.close()
            flash("Use uma senha forte com pelo menos 10 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial.", "error")
            return redirect(url_for("vigilante.redefinir_senha", token=token))

        conn.execute("UPDATE vigilantes SET password = ? WHERE id = ?", (generate_password_hash(senha), reset["user_id"]))
        conn.execute("UPDATE password_resets SET used_at = ? WHERE id = ?", (datetime.utcnow().isoformat(), reset["id"]))
        conn.commit()
        conn.close()
        clear_user_sessions()
        flash("Senha alterada com sucesso. Faça login com a nova senha.", "success")
        return redirect(url_for("vigilante.login"))

    conn.close()
    return render_template("vigilante/redefinir_senha.html", token=token)


@vigilante_bp.route("/dashboard")
@vigilante_required
def dashboard():
    vigilante_id = session["vigilante_id"]
    candidaturas_limit = max(5, min(request.args.get("candidaturas_limit", 8, type=int), 100))
    vagas_limit = max(5, min(request.args.get("vagas_limit", 10, type=int), 100))
    conn = get_connection()

    perfil = conn.execute(
        "SELECT * FROM vigilantes WHERE id = ?",
        (vigilante_id,),
    ).fetchone()

    total_candidaturas = conn.execute(
        "SELECT COUNT(*) AS total FROM candidaturas WHERE vigilante_id = ?",
        (vigilante_id,),
    ).fetchone()["total"]

    candidaturas = conn.execute(
        """
        SELECT
            c.id,
            c.status,
            c.observacoes,
            c.created_at,
            c.updated_at,
            v.titulo,
            v.empresa,
            v.cidade,
            v.estado,
            v.salario,
            CASE WHEN LOWER(COALESCE(r.status, 'validado')) = 'verificado' THEN 1 ELSE 0 END AS empresa_verificada
        FROM candidaturas c
        JOIN vagas v ON v.id = c.vaga_id
        LEFT JOIN recrutadores r ON r.id = v.recrutador_id
        WHERE c.vigilante_id = ?
        ORDER BY c.id DESC
        LIMIT ?
        """,
        (vigilante_id, candidaturas_limit),
    ).fetchall()

    vagas_ativas = conn.execute(
        "SELECT COUNT(*) AS total FROM vagas WHERE status = 'ativa'",
    ).fetchone()["total"]

    vagas_disponiveis = conn.execute(
        """
        SELECT
            v.id,
            v.titulo,
            v.empresa,
            v.cidade,
            v.estado,
            v.escala,
            v.salario,
            v.descricao,
            v.requisitos,
            r.site_empresa,
            r.descricao_empresa,
            CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END AS ja_candidatado,
            CASE WHEN LOWER(COALESCE(r.status, 'validado')) = 'verificado' THEN 1 ELSE 0 END AS empresa_verificada
        FROM vagas v
        LEFT JOIN recrutadores r ON r.id = v.recrutador_id
        LEFT JOIN candidaturas c
            ON c.vaga_id = v.id
           AND c.vigilante_id = ?
        WHERE v.status = 'ativa'
        ORDER BY empresa_verificada DESC, v.id DESC
        LIMIT ?
        """,
        (vigilante_id, vagas_limit),
    ).fetchall()
    conn.close()

    return render_template(
        "vigilante/dashboard.html",
        perfil=perfil,
        candidaturas=candidaturas,
        vagas_ativas=vagas_ativas,
        vagas_disponiveis=vagas_disponiveis,
        candidaturas_limit=candidaturas_limit,
        vagas_limit=vagas_limit,
        pode_mostrar_mais_candidaturas=total_candidaturas > candidaturas_limit,
        pode_mostrar_mais_vagas=vagas_ativas > vagas_limit,
    )


@vigilante_bp.route("/candidatar/<int:vaga_id>", methods=["POST"])
@vigilante_required
def candidatar(vaga_id: int):
    vigilante_id = session.get("vigilante_id")
    if not vigilante_id:
        flash("Faça login como vigilante para concluir a candidatura.", "error")
        return redirect(url_for("vigilante.login"))

    conn = get_connection()
    vigilante = conn.execute(
        "SELECT id FROM vigilantes WHERE id = ? AND status = 'ativo'",
        (vigilante_id,),
    ).fetchone()
    if not vigilante:
        conn.close()
        session.pop("vigilante_id", None)
        session.pop("vigilante_nome", None)
        flash("Seu acesso de vigilante não foi validado. Entre novamente para continuar.", "error")
        return redirect(url_for("vigilante.login"))

    vaga = conn.execute(
        "SELECT id, titulo FROM vagas WHERE id = ? AND status = 'ativa'",
        (vaga_id,),
    ).fetchone()
    if not vaga:
        conn.close()
        flash("A vaga selecionada não está disponível para candidatura.", "error")
        return redirect(url_for("vigilante.dashboard"))

    candidatura_existente = conn.execute(
        "SELECT id FROM candidaturas WHERE vigilante_id = ? AND vaga_id = ?",
        (vigilante_id, vaga_id),
    ).fetchone()
    if candidatura_existente:
        conn.close()
        flash("Você já se candidatou a esta vaga.", "error")
        return redirect(url_for("vigilante.dashboard"))

    conn.execute(
        "INSERT INTO candidaturas (vigilante_id, vaga_id, status) VALUES (?, ?, 'Recebida')",
        (vigilante_id, vaga_id),
    )
    conn.commit()
    conn.close()

    flash(f"Sua candidatura para '{vaga['titulo']}' foi registrada com sucesso.", "success")
    return redirect(url_for("vigilante.dashboard"))


@vigilante_bp.route("/logout", methods=["POST"])
@vigilante_required
def logout():
    session.pop("vigilante_id", None)
    session.pop("vigilante_nome", None)
    flash("Sessão do vigilante encerrada com sucesso.", "success")
    return redirect(url_for("vigilante.login"))


@vigilante_bp.route("/meus-dados.json")
@vigilante_required
def meus_dados_json():
    import json
    from flask import Response
    conn = get_connection()
    vigilante = conn.execute("SELECT id, nome, cpf, telefone, email, cidade, estado, endereco, cep, curso, reciclagem, area_interesse, resumo_profissional, objetivo_cargo, escolaridade, possui_cfv, instituicao_formacao, created_at FROM vigilantes WHERE id = ?", (session["vigilante_id"],)).fetchone()
    candidaturas = conn.execute("SELECT c.status, c.observacoes, c.created_at, v.titulo, v.empresa, v.cidade, v.estado FROM candidaturas c JOIN vagas v ON v.id = c.vaga_id WHERE c.vigilante_id = ? ORDER BY c.id DESC", (session["vigilante_id"],)).fetchall()
    conn.close()
    payload = {"perfil": dict(vigilante) if vigilante else {}, "candidaturas": [dict(x) for x in candidaturas]}
    return Response(json.dumps(payload, ensure_ascii=False, default=str, indent=2), mimetype="application/json", headers={"Content-Disposition":"attachment; filename=vigilante_meus_dados.json"})


@vigilante_bp.route("/excluir-conta", methods=["POST"])
@vigilante_required
def excluir_conta():
    vigilante_id = session["vigilante_id"]
    conn = get_connection()
    conn.execute("UPDATE vigilantes SET nome='USUARIO ANONIMIZADO', cpf='ANONIMIZADO-' || id, telefone='', email='anonimizado-' || id || '@vigivagas.local', endereco='', cep='', resumo_profissional='', ultima_experiencia_profissional='', status='excluido' WHERE id = ?", (vigilante_id,))
    conn.execute("UPDATE candidaturas SET observacoes = COALESCE(observacoes, '') || ' | Conta do vigilante anonimizada por solicitação LGPD.' WHERE vigilante_id = ?", (vigilante_id,))
    conn.commit(); conn.close()
    clear_user_sessions()
    flash("Sua conta foi anonimizada conforme solicitação LGPD.", "success")
    return redirect(url_for("public.index"))
