from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret Key
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# ========================================
# MAILTRAP EMAIL CONFIGURATION (Sandbox)
# ========================================
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "2525"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "edfa1a4af2637c")
app.config["MAIL_PASSWORD"] = os.getenv(
    "MAIL_PASSWORD", "your_full_mailtrap_password_here"
)
app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER", "noreply@example.com"
)
app.config["MAIL_MAX_EMAILS"] = None
app.config["MAIL_ASCII_ATTACHMENTS"] = False

# Log configuration (but hide sensitive data)
logger.info("=" * 50)
logger.info("EMAIL CONFIGURATION CHECK:")
logger.info(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
logger.info(f"MAIL_PORT: {app.config['MAIL_PORT']}")
logger.info(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
logger.info(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
logger.info(
    f"MAIL_USERNAME: {app.config['MAIL_USERNAME'][:5] + '***' if app.config['MAIL_USERNAME'] else 'NOT SET'}"
)
logger.info(f"MAIL_PASSWORD: {'SET ✓' if app.config['MAIL_PASSWORD'] else 'NOT SET ✗'}")
logger.info(
    f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER'][:5] + '***' if app.config['MAIL_DEFAULT_SENDER'] else 'NOT SET'}"
)
logger.info("=" * 50)

# Initialize extensions
mail = Mail(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

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
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        if not all([name, email, subject, message]):
            logger.warning("Contact form submission missing required fields")
            return (
                jsonify({"success": False, "message": "All fields are required."}),
                400,
            )

        if "@" not in email or "." not in email:
            logger.warning(f"Invalid email format: {email}")
            return jsonify({"success": False, "message": "Invalid email address."}), 400

        admin_email = app.config.get("MAIL_DEFAULT_SENDER")
        if not admin_email:
            logger.error("MAIL_DEFAULT_SENDER not configured")
            return (
                jsonify({"success": False, "message": "Email configuration error."}),
                500,
            )

        if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
            logger.error("Email credentials not properly configured")
            return (
                jsonify({"success": False, "message": "Email configuration error."}),
                500,
            )

        # Send email to admin
        try:
            msg = Message(
                subject=f"Portfolio Contact: {subject}",
                sender=admin_email,
                recipients=[admin_email],
                reply_to=email,
            )
            msg.html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                        <h2 style="color: #333; border-bottom: 3px solid #000; padding-bottom: 10px;">
                            New Contact Form Submission
                        </h2>
                        <p><strong>From:</strong> {name}</p>
                        <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                        <p><strong>Subject:</strong> {subject}</p>
                        <div style="background: #f9f9f9; padding: 20px; border-left: 4px solid #000;">
                            <p><strong>Message:</strong></p>
                            <p>{message}</p>
                        </div>
                        <p style="color: #666; font-size: 12px; margin-top: 20px;">
                            Sent from your portfolio contact form
                        </p>
                    </div>
                </body>
            </html>
            """
            logger.info(f"Sending email to admin: {admin_email}")
            mail.send(msg)
            logger.info("Admin email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send admin email: {str(e)}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to send message. Please try again later.",
                    }
                ),
                500,
            )

        # Auto-reply
        try:
            auto_reply = Message(
                subject="Thank you for contacting me!",
                sender=admin_email,
                recipients=[email],
            )
            auto_reply.html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Thank You for Reaching Out!</h2>
                    <p>Hi <strong>{name}</strong>,</p>
                    <p>Thank you for contacting me through my portfolio. 
                    I've received your message about "<strong>{subject}</strong>" 
                    and will get back to you as soon as possible.</p>
                    <p>I typically respond within 24 hours during business days.</p>
                    <p>Best regards,<br><strong>Emmanuel Victor Itopa</strong></p>
                </body>
            </html>
            """
            logger.info(f"Sending auto-reply to: {email}")
            mail.send(auto_reply)
            logger.info("Auto-reply sent successfully")
        except Exception as e:
            logger.warning(f"Failed to send auto-reply: {str(e)}")

        return jsonify({"success": True, "message": "Message sent successfully!"}), 200

    except Exception as e:
        logger.error(f"Unexpected error in send_contact: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An error occurred. Please try again later.",
                }
            ),
            500,
        )


# ---------- TEST EMAIL ENDPOINT ----------
@app.route("/api/test-email")
def test_email():
    try:
        admin_email = app.config.get("MAIL_DEFAULT_SENDER")

        if not admin_email:
            return (
                jsonify(
                    {"success": False, "message": "MAIL_DEFAULT_SENDER not configured"}
                ),
                500,
            )

        msg = Message(
            subject="Test Email from Portfolio",
            sender=admin_email,
            recipients=[admin_email],
        )
        msg.body = "This is a test email. If you receive this, your Mailtrap configuration is working!"

        logger.info(f"Sending test email to: {admin_email}")
        mail.send(msg)
        logger.info("Test email sent successfully")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Test email sent successfully! Check your Mailtrap inbox.",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Test email failed: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": f"Test email failed: {str(e)}"}),
            500,
        )


# ---------- DOWNLOAD RESUME ----------
@app.route("/download/resume")
def download_resume():
    try:
        resume_path = os.path.join(app.root_path, "static", "resume", "your_resume.pdf")
        if not os.path.exists(resume_path):
            logger.warning(f"Resume not found at: {resume_path}")
            return jsonify({"error": "Resume not found"}), 404

        return send_from_directory(
            os.path.join(app.root_path, "static", "resume"),
            "your_resume.pdf",
            as_attachment=True,
            download_name="Emmanuel_Victor_Itopa_Resume.pdf",
        )
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        return jsonify({"error": "Resume not found"}), 404


# ---------- HEALTH CHECK ----------
@app.route("/health")
def health_check():
    return (
        jsonify(
            {
                "status": "healthy",
                "mail_configured": bool(
                    app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD")
                ),
            }
        ),
        200,
    )


# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
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
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
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
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Debug mode: {debug}")
    app.run(debug=debug, host="0.0.0.0", port=port)
