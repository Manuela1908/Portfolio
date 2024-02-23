from flask import Flask, render_template, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import dotenv

dotenv.load_dotenv()


app = Flask(__name__, template_folder=r'C:\Users\Manuela.DESKTOP-H5K2INA\Desktop\PROGRAMAS\Python\portfolio\templates')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_PASSWORD")
to_email = gmail_user

def enviar_email_erro(descricao_erro):
    try:
        subject = "Erro no Aplicativo"
        body = descricao_erro

        message = MIMEMultipart()
        message["From"] = gmail_user
        message["To"] = to_email
        message["Subject"] = "Erro API GPT - Portfolio"
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = message.as_string()
            server.sendmail(gmail_user, to_email, text)

        return 200
    except Exception as e:
        enviar_email_erro(str(e))

        return jsonify({
            "error": "Erro interno do servidor. Detalhes do erro foram enviados por e-mail.",
            "details": str(e)
        }), 500
    
openai_api_key = os.getenv("OPENAI_API_KEY")
url_gpt = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gerar_receita", methods=["POST"])
def gerar_receita():
    try:
        receita = request.form.get("receita")

        receita_gerada = obter_receita_gpt(receita)

        return jsonify({"receita": receita_gerada})

    except Exception as e:
        print(f"Erro interno do servidor: {str(e)}")

        enviar_email_erro(str(e))

        return jsonify({"error": "Erro interno do servidor. Detalhes do erro foram enviados por e-mail."}), 500

def obter_receita_gpt(receita):
    data_gpt = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Gere receitas culinárias"},
            {"role": "user", "content": receita}
        ],
        "temperature": 1,
        "max_tokens": 500,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    response_gpt = requests.post(url_gpt, headers=headers, data=json.dumps(data_gpt))
    
    response_gpt.raise_for_status()
    
    recipe_result = response_gpt.json()
    return recipe_result["choices"][0]["message"]["content"]

if __name__ == "__main__":
    app.run(debug=True)