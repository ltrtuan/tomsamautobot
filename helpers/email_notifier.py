# helpers/email_notifier.py
"""
Singleton Email Notifier for TomSamAutobot

Usage:
    from helpers.email_notifier import send_email, format_email_content
    
    # Quick send
    send_email(title="Test", content="<p>Hello</p>")
    
    # With template
    # ========== SEND EMAIL ALERT (NEW) ==========
    content = format_email_content(
        title="YouTube Action Failed",
        sections=[
            ("Profile ID", self.profile_id),
            ("Action", action.get('type', 'Unknown')),
            ("Step", f"{self.current_step}/{self.total_steps}"),
            ("Error", "Action execution returned False"),
            ("Chain", "YouTube Auto Actions")
        ]
    )
    send_email(
        title=f"Action Failed: {self.profile_id}",
        content=content,
        throttle_seconds=600  # Max 1 per 10 minutes
    )
"""

import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config
import logging
import socket

logger = logging.getLogger('TomSamAutobot')

# ========== MACHINE INFO HELPERS ==========
def get_machine_name():
    """Get computer name"""
    import socket
    try:
        return socket.gethostname()
    except:
        return "Unknown"


def get_machine_ip():
    """Get local IP address"""
    try:
        # Connect to external server to get local IP (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"


def get_machine_info():
    """
    Get machine info as formatted string
    
    Returns:
        str: Formatted machine info (e.g., "DESKTOP-ABC123 (192.168.1.100)")
    """
    name = get_machine_name()
    ip = get_machine_ip()
    return f"{name} ({ip})"


# ========== SINGLETON STATE ==========
_email_lock = threading.Lock()  # Thread-safe
_last_sent_time = {}  # email_hash → timestamp (for throttling)


# ========== CORE SEND EMAIL FUNCTION (SINGLETON) ==========
def send_email(title, content, content_type="html", throttle_seconds=300):
    """
    Singleton function: Send email alert
    
    Args:
        title (str): Email subject
        content (str): Email body (HTML hoặc plain text)
        content_type (str): "html" hoặc "plain" (default: "html")
        throttle_seconds (int): Throttle duplicate emails (default: 5 minutes)
                                Set to 0 to disable throttling
    
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại hoặc bị throttle
    
    Examples:
        send_email(
            title="Profile Failed",
            content="<h3>Profile abc123 failed</h3>"
        )
    """
    
    # Check if email enabled
    if not config.SMTP_ENABLED:
        logger.debug("Email disabled in config - skipping send")
        print("[EMAIL] Email disabled in config")
        return False
    
    # Validate config
    if not all([config.SMTP_HOST, config.SMTP_USERNAME, config.SMTP_PASSWORD, config.SMTP_TO_EMAIL]):
        logger.warning("SMTP config incomplete - cannot send email")
        print("[EMAIL ERROR] SMTP config incomplete")
        return False
    
    # ========== FIX: IMPROVED THROTTLING WITH LOGGING ==========
    if throttle_seconds > 0:
        email_hash = hash(f"{title}:{content[:100]}")
        
        with _email_lock:
            last_time = _last_sent_time.get(email_hash, 0)
            current_time = datetime.now().timestamp()
            time_since_last = current_time - last_time
            
            if time_since_last < throttle_seconds:
                remaining = throttle_seconds - time_since_last
                print("=" * 80)
                print(f"[EMAIL THROTTLE] ⚠️ Email blocked by throttle")
                print(f"[EMAIL THROTTLE] Title: {title[:60]}...")
                print(f"[EMAIL THROTTLE] Last sent: {int(time_since_last)}s ago")
                print(f"[EMAIL THROTTLE] Throttle period: {throttle_seconds}s")
                print(f"[EMAIL THROTTLE] Remaining cooldown: {int(remaining)}s")
                print("=" * 80)
                logger.debug(f"Email throttled: '{title}' (sent {int(time_since_last)}s ago, need {throttle_seconds}s)")
                return False
            
            # Update last sent time
            _last_sent_time[email_hash] = current_time
            print(f"[EMAIL DEBUG] Throttle check passed (last sent: {int(time_since_last)}s ago)")
    else:
        print(f"[EMAIL DEBUG] Throttle disabled (throttle_seconds={throttle_seconds})")
    # ===========================================================
    
    # ========== KEEP ORIGINAL BACKGROUND THREAD LOGIC ==========
    # Send email in background thread (non-blocking)
    print(f"[EMAIL] Starting background thread to send: '{title}'")
    thread = threading.Thread(
        target=_send_email_sync,
        args=(title, content, content_type),
        daemon=False,
        name="EmailSenderThread"
    )
    thread.start()
    # ===========================================================
    
    return True



def _send_email_sync(title, content, content_type):
    """Internal: Synchronous email sending (called in background thread)"""
    
    print("=" * 80)
    print(f"[EMAIL WORKER] 🚀 Thread started")
    print(f"[EMAIL WORKER] Title: '{title}'")
    print(f"[EMAIL WORKER] Content length: {len(content)} chars")
    print("=" * 80)
    
    try:
        # Create message
        print(f"[EMAIL WORKER] Creating MIME message...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[TomSamAutobot] {title}"
        
        from_email = config.SMTP_FROM_EMAIL if hasattr(config, 'SMTP_FROM_EMAIL') and config.SMTP_FROM_EMAIL else config.SMTP_USERNAME
        msg['From'] = from_email
        msg['To'] = config.SMTP_TO_EMAIL
        
        print(f"[EMAIL WORKER] From: {from_email}")
        print(f"[EMAIL WORKER] To: {config.SMTP_TO_EMAIL}")
        
        # Attach content
        mime_type = 'html' if content_type == 'html' else 'plain'
        msg.attach(MIMEText(content, mime_type, 'utf-8'))
        print(f"[EMAIL WORKER] Content attached (type: {mime_type})")
        
        # Connect to SMTP server
        print(f"[EMAIL WORKER] Connecting to {config.SMTP_HOST}:{config.SMTP_PORT}...")
        
        if hasattr(config, 'SMTP_USE_TLS') and config.SMTP_USE_TLS:
            print(f"[EMAIL WORKER] Using TLS mode...")
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
            print(f"[EMAIL WORKER] Starting TLS...")
            server.starttls()
            print(f"[EMAIL WORKER] TLS started")
        else:
            print(f"[EMAIL WORKER] Using SSL mode...")
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
            print(f"[EMAIL WORKER] SSL connected")
        
        # Login and send
        print(f"[EMAIL WORKER] Logging in as {config.SMTP_USERNAME}...")
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        print(f"[EMAIL WORKER] ✓ Login successful")
        
        print(f"[EMAIL WORKER] Sending message...")
        server.send_message(msg)
        print(f"[EMAIL WORKER] ✓ Message sent")
        
        server.quit()
        print(f"[EMAIL WORKER] SMTP connection closed")
        
        print("=" * 80)
        print(f"[EMAIL WORKER] ✅ SUCCESS - Email sent to {config.SMTP_TO_EMAIL}")
        print("=" * 80)
        
        logger.info(f"✓ Email sent: '{title}' to {config.SMTP_TO_EMAIL}")
        
    except smtplib.SMTPAuthenticationError as e:
        print("=" * 80)
        print(f"[EMAIL WORKER] ❌ AUTHENTICATION FAILED")
        print(f"[EMAIL WORKER] Error: {e}")
        print("=" * 80)
        logger.error(f"✗ Email authentication failed: {e}")
        import traceback
        traceback.print_exc()
        
    except smtplib.SMTPException as e:
        print("=" * 80)
        print(f"[EMAIL WORKER] ❌ SMTP ERROR")
        print(f"[EMAIL WORKER] Error: {e}")
        print("=" * 80)
        logger.error(f"✗ Email send failed (SMTP error): {e}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print("=" * 80)
        print(f"[EMAIL WORKER] ❌ UNEXPECTED ERROR")
        print(f"[EMAIL WORKER] Error type: {type(e).__name__}")
        print(f"[EMAIL WORKER] Error message: {e}")
        print("=" * 80)
        logger.error(f"✗ Email send failed: {e}")
        import traceback
        traceback.print_exc()



# ========== TEST CONNECTION (FOR SETTINGS) ==========
def test_smtp_connection():
    """Test SMTP and send test email"""
    if not all([config.SMTP_HOST, config.SMTP_USERNAME, config.SMTP_PASSWORD, config.SMTP_TO_EMAIL]):
        return False, "SMTP config không đầy đủ"
    
    try:
        # ========== DÙNG PRINT THAY VÌ LOGGER ==========
        print(f"[SMTP TEST] Connecting to {config.SMTP_HOST}:{config.SMTP_PORT}")
        
        if config.SMTP_USE_TLS:
            print("[SMTP TEST] Creating SMTP connection with STARTTLS...")
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
            print("[SMTP TEST] SMTP connection established, starting TLS...")
            server.starttls()
            print("[SMTP TEST] TLS handshake successful")
        else:
            print("[SMTP TEST] Creating SMTP connection (no TLS)...")
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
            print("[SMTP TEST] SMTP connection established")
        
        # Test login
        print(f"[SMTP TEST] Attempting login with username: {config.SMTP_USERNAME}")
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        print("[SMTP TEST] Login successful")
        
        # Send test email
        test_content = format_email_content(
            title="SMTP Test Email",
            sections=[
                ("Thông báo", "Đây là email test từ TomSamAutobot"),
                ("Trạng thái", "Cấu hình SMTP hoạt động tốt! ✅")
            ]
        )
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[TomSamAutobot] SMTP Test Email"
        from_email = config.SMTP_FROM_EMAIL if config.SMTP_FROM_EMAIL else config.SMTP_USERNAME
        msg['From'] = from_email
        msg['To'] = config.SMTP_TO_EMAIL
        msg.attach(MIMEText(test_content, 'html', 'utf-8'))
        
        print("[SMTP TEST] Sending test email...")
        server.send_message(msg)
        print("[SMTP TEST] Test email sent successfully")
        server.quit()
        
        return True, f"✓ Email test đã gửi tới {config.SMTP_TO_EMAIL}"
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[SMTP TEST ERROR] Auth failed: {e}")
        return False, f"✗ Xác thực thất bại: {str(e)}\n\nKiểm tra:\n- Username/Password đúng?\n- Mailtrap credentials?"
    
    except smtplib.SMTPConnectError as e:
        print(f"[SMTP TEST ERROR] Connect failed: {e}")
        return False, f"✗ Không kết nối được:\n{str(e)}\n\nKiểm tra:\n- Host/Port đúng?\n- Firewall?"
    
    except socket.timeout:
        print(f"[SMTP TEST ERROR] Timeout connecting to {config.SMTP_HOST}:{config.SMTP_PORT}")
        # ========== GỢI Ý PORT 2525 CHO MAILTRAP ==========
        suggestion = ""
        if "mailtrap" in config.SMTP_HOST.lower():
            suggestion = "\n\n💡 Mailtrap khuyến nghị dùng port 2525 hoặc 25 thay vì 587!"
        return False, f"✗ Timeout khi kết nối tới {config.SMTP_HOST}:{config.SMTP_PORT}\n\nKiểm tra:\n- Firewall block port?\n- Thử port 2525 (Mailtrap){suggestion}"
    
    except Exception as e:
        print(f"[SMTP TEST ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False, f"✗ Lỗi: {str(e)}"




# ========== EMAIL TEMPLATE FORMATTER ==========
def format_email_content(title, sections, footer_text=None):
    # ========== PREPEND MACHINE INFO TO SECTIONS (AUTO) ==========
    machine_sections = [
        ("🖥️ Máy tính", get_machine_name()),
        ("🌐 IP Address", get_machine_ip()),
        ("⏰ Thời gian", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("", "")  # Separator row (empty)
    ]
    
    # Combine machine info + user sections
    all_sections = machine_sections + sections
    
    # Build sections HTML
    sections_html = ""
    for section_title, section_content in all_sections:
        # Skip empty separator row rendering
        if section_title == "" and section_content == "":
            sections_html += """
            <tr>
                <td colspan="2" style="padding: 8px; background-color: #f0f0f0;">
                    <hr style="border: none; border-top: 1px dashed #ccc; margin: 0;">
                </td>
            </tr>
            """
            continue
        
        sections_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">
                <strong style="color: #555; font-size: 13px;">{section_title}:</strong>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333;">
                {section_content}
            </td>
        </tr>
        """
    
    # Default footer (with machine info)
    if footer_text is None:
        footer_text = f"Email tự động từ TomSamAutobot @ {get_machine_info()} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    
    # Full HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%); padding: 24px; border-radius: 8px 8px 0 0;">
                                <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">
                                    🤖 TomSamAutobot
                                </h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 24px; background-color: #fafafa; border-bottom: 3px solid #0078d4;">
                                <h2 style="margin: 0; color: #333; font-size: 20px; font-weight: 500;">
                                    {title}
                                </h2>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 0;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    {sections_html}
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; background-color: #fafafa; border-radius: 0 0 8px 8px; text-align: center;">
                                <p style="margin: 0; color: #999; font-size: 12px;">
                                    {footer_text}
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html_template


# ========== PRE-DEFINED TEMPLATE: CRASH ALERT ==========
def format_crash_email(exception_type, exception_message, traceback_str, context=None):
    """
    Pre-defined template: Crash alert email
    
    Args:
        exception_type (str): Exception class name
        exception_message (str): Exception message
        traceback_str (str): Full traceback string
        context (dict, optional): Extra context
    
    Returns:
        tuple: (title, html_content)
    """
    sections = [
        ("Loại lỗi", exception_type),
        ("Thông báo lỗi", f"<code style='color: #d13438;'>{exception_message}</code>"),
    ]

    
    if context:
        for key, value in context.items():
            sections.append((key.capitalize(), str(value)))
    
    # Add traceback (truncated)
    traceback_html = traceback_str.replace('\n', '<br>').replace(' ', '&nbsp;')
    if len(traceback_html) > 2000:
        traceback_html = traceback_html[:2000] + '<br>...(truncated)'
    
    sections.append((
        "Stack Trace",
        f"<pre style='background: #f5f5f5; padding: 12px; border-left: 3px solid #d13438; overflow-x: auto; font-size: 11px;'>{traceback_html}</pre>"
    ))
    
    title = f"🚨 CRASH: {exception_type}"
    content = format_email_content(title="Application Crash Alert", sections=sections)
    
    return title, content


def format_heartbeat_email(uptime_str, interval_hours, context=None):
    """
    Pre-defined template: Heartbeat health check email
    
    Args:
        uptime_str (str): Uptime string (e.g., "2.5 hours")
        interval_hours (float): Check interval in hours
        context (dict, optional): Extra context info
    
    Returns:
        tuple: (title, html_content)
    """
    sections = [
        ("Trạng thái", "✓ <span style='color: #107c10; font-weight: bold;'>App Đang Hoạt Động Bình Thường</span>"),
        ("Thời gian chạy", uptime_str),
        ("Khoảng kiểm tra", f"Mỗi {interval_hours} giờ"),
    ]
    
    # Add extra context if provided
    if context:
        for key, value in context.items():
            sections.append((key.capitalize(), str(value)))
    
    # Add note
    sections.append(("", ""))  # Separator
    sections.append(
        ("Lưu ý", 
         f"<em style='color: #666; font-size: 12px;'>"
         f"Email tự động được gửi để xác nhận app vẫn đang chạy.<br>"
         f"Nếu bạn không nhận được email sau <strong>{interval_hours} giờ</strong>, "
         f"có thể app đã dừng hoặc gặp sự cố.</em>")
    )
    
    title = f"✓ Heartbeat - App đang hoạt động"
    content = format_email_content(
        title="Health Check - App Running",
        sections=sections
    )
    
    return title, content
