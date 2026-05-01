from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from utils.captcha import generate_captcha, verify_captcha

from utils.db import get_connection
from utils.fraud import evaluate_vigilante_risk, get_client_ip, get_user_agent, is_disposable_email, looks_like_test_name
from utils.validators import (
    format_cep,
    format_cpf,
    format_phone,
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

public_bp = Blueprint("public", __name__)


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


@public_bp.route("/")
def index():
    conn = get_connection()
    vagas = conn.execute(
        """
        SELECT
            v.*,
            COALESCE(LOWER(r.status), 'validado') AS recrutador_status,
            r.site_empresa,
            r.descricao_empresa,
            CASE WHEN LOWER(COALESCE(r.status, 'validado')) = 'verificado' THEN 1 ELSE 0 END AS empresa_verificada
        FROM vagas v
        LEFT JOIN recrutadores r ON r.id = v.recrutador_id
        WHERE v.status = 'ativa'
        ORDER BY empresa_verificada DESC, v.created_at DESC, v.id DESC
        LIMIT 12
        """
    ).fetchall()
    conn.close()
    return render_template("public/index.html", vagas=vagas)



@public_bp.route("/privacidade")
def privacidade():
    return render_template("public/privacidade.html")


@public_bp.route("/termos")
def termos():
    return render_template("public/termos.html")

@public_bp.route("/candidato", methods=["GET"])
def candidato():
    if session.get("vigilante_id"):
        flash("Você já está autenticado como vigilante.", "info")
        return redirect(url_for("vigilante.dashboard"))
    if session.pop("public_cadastro_concluido", False):
        flash("Seu cadastro inicial já foi enviado. Agora acompanhe pela área do vigilante quando houver migração do perfil.", "info")
    return render_template("public/candidato.html", captcha_question=generate_captcha("public_candidato"))


@public_bp.route("/cadastrar", methods=["POST"])
def cadastrar():
    if session.get("vigilante_id"):
        flash("Você já está autenticado como vigilante.", "info")
        return redirect(url_for("vigilante.dashboard"))

    if request.form.get("aceite_lgpd") != "1":
        flash("Para continuar, aceite a Política de Privacidade e os Termos de Uso.", "error")
        return redirect(url_for("public.candidato"))

    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    dados = {
        "nome": normalize_upper(request.form.get("nome", "")),
        "cpf": format_cpf(request.form.get("cpf", "")),
        "telefone": format_phone(request.form.get("telefone", "")),
        "email": normalize_email(request.form.get("email", "")),
        "cidade": normalize_upper(request.form.get("cidade", "")),
        "estado": normalize_upper(request.form.get("estado", ""))[:2],
        "endereco": normalize_upper(request.form.get("endereco", "")),
        "cep": format_cep(request.form.get("cep", "")),
        "curso": normalize_upper(request.form.get("curso", "")),
        "reciclagem": normalize_upper(request.form.get("reciclagem", "")),
        "area": normalize_upper(request.form.get("area", "")),
        "mensagem": normalize_textarea_upper(request.form.get("mensagem", "")),
    }

    captcha_resposta = request.form.get("captcha_resposta", "")

    obrigatorios = ["nome", "cpf", "telefone", "email", "cidade", "estado", "endereco", "cep", "curso", "reciclagem"]
    faltando = [campo for campo in obrigatorios if not dados[campo]]
    if faltando:
        flash("Preencha todos os campos obrigatórios antes de enviar.", "error")
        return redirect(url_for("public.candidato"))

    if not verify_captcha("public_candidato", captcha_resposta):
        flash("CAPTCHA inválido. Resolva a conta corretamente para continuar.", "error")
        return redirect(url_for("public.candidato"))

    if not is_valid_cpf(dados["cpf"]):
        flash("Informe um CPF válido. O sistema bloqueia CPF falso.", "error")
        return redirect(url_for("public.candidato"))

    if not is_valid_phone(dados["telefone"]):
        flash("Informe um telefone válido com DDD.", "error")
        return redirect(url_for("public.candidato"))

    if not is_valid_cep(dados["cep"]):
        flash("Informe um CEP válido com 8 dígitos.", "error")
        return redirect(url_for("public.candidato"))

    if not is_valid_state_code(dados["estado"]):
        flash("Informe uma UF válida com 2 letras.", "error")
        return redirect(url_for("public.candidato"))

    if not has_meaningful_length(dados["nome"], 8) or looks_like_test_name(dados["nome"]):
        flash("Informe um nome completo real. Cadastros de teste ou incompletos são bloqueados.", "error")
        return redirect(url_for("public.candidato"))

    if not has_meaningful_length(dados["endereco"], 10):
        flash("Informe um endereço mais completo para reduzir cadastros fantasmas.", "error")
        return redirect(url_for("public.candidato"))

    if is_disposable_email(dados["email"]):
        flash("E-mails temporários ou descartáveis não são aceitos.", "error")
        return redirect(url_for("public.candidato"))

    valido, mensagem = validate_vigilante_requirements(dados["curso"], dados["reciclagem"])
    if not valido:
        flash(mensagem, "error")
        return redirect(url_for("public.candidato"))

    conn = get_connection()

    cpf_existente = conn.execute(
        "SELECT id FROM candidatos WHERE cpf = ? UNION SELECT id FROM vigilantes WHERE cpf = ?",
        (dados["cpf"], dados["cpf"]),
    ).fetchone()
    if cpf_existente:
        conn.close()
        flash("Já existe cadastro com este CPF. Entre na área do vigilante para acompanhar seu perfil.", "error")
        return redirect(url_for("vigilante.login"))

    email_existente = conn.execute(
        "SELECT id FROM candidatos WHERE email = ? UNION SELECT id FROM vigilantes WHERE email = ?",
        (dados["email"], dados["email"]),
    ).fetchone()
    if email_existente:
        conn.close()
        flash("Já existe cadastro com este e-mail. Use a área do vigilante para entrar.", "error")
        return redirect(url_for("vigilante.login"))

    antifraude_score, antifraude_flags, antifraude_status = evaluate_vigilante_risk(
        conn,
        dados["nome"],
        dados["email"],
        dados["telefone"],
        client_ip,
        user_agent,
    )

    conn.execute(
        """
        INSERT INTO candidatos
        (nome, cpf, telefone, email, cidade, estado, endereco, cep, curso, reciclagem, area, mensagem, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            dados["curso"],
            dados["reciclagem"],
            dados["area"],
            dados["mensagem"],
            client_ip,
            user_agent,
            antifraude_score,
            antifraude_flags,
            antifraude_status,
        ),
    )
    novo_candidato = conn.execute("SELECT id FROM candidatos WHERE email = ?", (dados["email"],)).fetchone()
    _registrar_consentimento_lgpd(conn, "candidato", novo_candidato["id"] if novo_candidato else None, dados["email"])
    conn.commit()
    conn.close()

    session["public_cadastro_concluido"] = True
    flash("Cadastro enviado com sucesso. Seus dados foram validados e salvos no banco.", "success")
    if antifraude_status == "suspeito":
        flash("O cadastro foi salvo com sinalização preventiva para revisão administrativa.", "info")
    return redirect(url_for("public.candidato"))
