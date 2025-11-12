from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# Email configuration - FIXED
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USE_SSL"] = (
    os.getenv("MAIL_USE_SSL", "False") == "True"
)  # Fixed: Should be False for TLS
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

# Debug: Print config (remove in production)
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
@csrf.exempt  # Add this if testing without CSRF token
def send_contact():
    try:
        # Handle both JSON and form submissions
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        # Validate required fields
        if not all([name, email, subject, message]):
            return (
                jsonify({"success": False, "message": "All fields are required."}),
                400,
            )

        # Basic email validation
        if "@" not in email or "." not in email:
            return (
                jsonify({"success": False, "message": "Invalid email address."}),
                400,
            )

        admin_email = os.getenv("MAIL_DEFAULT_SENDER")

        if not admin_email:
            print("❌ ERROR: MAIL_DEFAULT_SENDER not set in .env")
            return (
                jsonify({"success": False, "message": "Email configuration error."}),
                500,
            )

        # Send email to admin
        msg = Message(
            subject=f"📩 Portfolio Contact: {subject}",
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
                    <div style="margin: 20px 0;">
                        <p style="margin: 10px 0;"><strong>From:</strong> {name}</p>
                        <p style="margin: 10px 0;"><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                        <p style="margin: 10px 0;"><strong>Subject:</strong> {subject}</p>
                    </div>
                    <div style="background: #f9f9f9; padding: 20px; border-left: 4px solid #000; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Message:</strong></p>
                        <p style="margin: 10px 0; line-height: 1.6;">{message}</p>
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        Sent from your portfolio contact form
                    </p>
                </div>
            </body>
        </html>
        """

        print(f"📧 Attempting to send email to {admin_email}...")
        mail.send(msg)
        print("✅ Email to admin sent successfully!")

        # Send auto-reply to user
        auto_reply = Message(
            subject="✅ Thank you for contacting me!",
            sender=admin_email,
            recipients=[email],
        )

        auto_reply.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #333;">Thank You for Reaching Out!</h2>
                    <p>Hi <strong>{name}</strong>,</p>
                    <p style="line-height: 1.6;">
                        Thank you for contacting me through my portfolio. I've received your message 
                        about "<strong>{subject}</strong>" and will get back to you as soon as possible.
                    </p>
                    <p style="line-height: 1.6;">
                        I typically respond within 24 hours during business days.
                    </p>
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee;">
                        <p style="margin: 5px 0;">Best regards,</p>
                        <p style="margin: 5px 0;"><strong>Emmanuel Victor Itopa</strong></p>
                    </div>
                </div>
            </body>
        </html>
        """

        print(f"📧 Attempting to send auto-reply to {email}...")
        mail.send(auto_reply)
        print("✅ Auto-reply sent successfully!")

        return jsonify({"success": True, "message": "Message sent successfully!"}), 200

    except Exception as e:
        print(f"❌ ERROR sending email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Failed to send message: {str(e)}",
                }
            ),
            500,
        )


# ---------- TEST EMAIL ENDPOINT ----------
@app.route("/api/test-email")
def test_email():
    """Test endpoint to verify email configuration"""
    try:
        admin_email = os.getenv("MAIL_DEFAULT_SENDER")

        msg = Message(
            subject="✅ Test Email from Portfolio",
            sender=admin_email,
            recipients=[admin_email],
        )

        msg.body = "This is a test email. If you receive this, your email configuration is working!"

        mail.send(msg)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Test email sent successfully! Check your inbox.",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Test email failed: {str(e)}"}),
            500,
        )


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
    app.run(debug=True, host="0.0.0.0", port=5000)
