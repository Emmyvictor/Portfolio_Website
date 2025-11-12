from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from threading import Thread

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# Email configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

# Debug config
print("=" * 50)
print("EMAIL CONFIGURATION DEBUG:")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_PASSWORD: {'*' * 10 if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
print("=" * 50)

# Initialize extensions
mail = Mail(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


# ---------- HELPER TO SEND EMAIL ASYNC ----------
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"❌ Failed to send email: {e}")


def send_email(subject, recipients, html_content, sender=None):
    msg = Message(
        subject=subject,
        sender=sender or app.config["MAIL_DEFAULT_SENDER"],
        recipients=recipients,
    )
    msg.html = html_content
    Thread(target=send_async_email, args=(app, msg)).start()


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/research")
def research():
    return render_template("research.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------- CONTACT FORM API ----------
@app.route("/api/contact", methods=["POST"])
@limiter.limit("5 per hour")
@csrf.exempt
def send_contact():
    try:
        data = request.get_json() if request.is_json else request.form
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        if not all([name, email, subject, message]):
            return (
                jsonify({"success": False, "message": "All fields are required."}),
                400,
            )
        if "@" not in email or "." not in email:
            return jsonify({"success": False, "message": "Invalid email address."}), 400

        admin_email = app.config["MAIL_DEFAULT_SENDER"]
        if not admin_email:
            return (
                jsonify({"success": False, "message": "Email configuration error."}),
                500,
            )

        # Send email to admin
        admin_html = f"""
        <p><strong>From:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong><br>{message}</p>
        """
        send_email(
            subject=f"📩 Portfolio Contact: {subject}",
            recipients=[admin_email],
            html_content=admin_html,
            sender=admin_email,
        )

        # Send auto-reply to user
        user_html = f"""
        <p>Hi {name},</p>
        <p>Thank you for contacting me. I've received your message about "<strong>{subject}</strong>".</p>
        <p>I'll get back to you as soon as possible.</p>
        <p>Best regards,<br>Emmanuel Victor Itopa</p>
        """
        send_email(
            subject="✅ Thank you for contacting me!",
            recipients=[email],
            html_content=user_html,
            sender=admin_email,
        )

        return jsonify({"success": True, "message": "Message sent successfully!"}), 200

    except Exception as e:
        print(f"❌ ERROR sending contact email: {e}")
        return (
            jsonify({"success": False, "message": f"Failed to send message: {str(e)}"}),
            500,
        )


# ---------- TEST EMAIL ----------
@app.route("/api/test-email")
def test_email():
    try:
        admin_email = app.config["MAIL_DEFAULT_SENDER"]
        html_content = "<p>This is a test email. If you receive this, your email configuration is working!</p>"
        send_email(
            subject="✅ Test Email from Portfolio",
            recipients=[admin_email],
            html_content=html_content,
        )
        return (
            jsonify({"success": True, "message": "Test email sent successfully!"}),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Test email failed: {e}"}), 500


# ---------- DOWNLOAD RESUME ----------
@app.route("/download/resume")
def download_resume():
    try:
        return send_from_directory(
            os.path.join(app.root_path, "static", "resume"),
            "your_resume.pdf",
            as_attachment=True,
            download_name="Emmanuel_Victor_Itopa_Resume.pdf",
        )
    except Exception:
        return jsonify({"error": "Resume not found"}), 404


# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return (
        jsonify(
            {"success": False, "message": "Too many requests. Please try again later."}
        ),
        429,
    )


@app.errorhandler(500)
def internal_error(e):
    return (
        jsonify(
            {
                "success": False,
                "message": "Internal server error. Please try again later.",
            }
        ),
        500,
    )


# ---------- MAIN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port if available
    app.run(debug=False, host="0.0.0.0", port=port)
