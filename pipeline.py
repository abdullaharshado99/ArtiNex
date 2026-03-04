import os, random
import resend
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RESEND_KEY = os.environ.get('RESEND_KEY')


def generate_chat_response(message, session_id):
    """Generate intelligent responses based on your services"""

    # Service keywords mapping
    services = {
        'computer vision': 'We offer advanced computer vision solutions including object detection (YOLO), facial recognition, and visual quality control systems. Would you like to discuss a specific use case?',
        'object detection': 'Our object detection systems use state-of-the-art YOLO models with 94.98% accuracy. We can customize it for your specific needs, whether it\'s security, manufacturing, or retail.',
        'anomaly detection': 'We provide real-time anomaly detection for cybersecurity, fraud detection, and system monitoring. Our PyOD and DeepOD models detect unusual patterns with high precision.',
        'rag chatbot': 'Our RAG (Retrieval-Augmented Generation) chatbots integrate with your enterprise knowledge base for accurate, context-aware responses. Powered by LangChain and vector databases.',
        'ai agents': 'We develop autonomous AI agents for complex decision-making and workflow automation. Using AutoGen, LangGraph, and CrewAI for intelligent task execution.',
        'time series': 'Our time series forecasting solutions predict demand, financial trends, and operational patterns using Prophet, ARIMA, and LSTM models.',
        'model training': 'We offer custom ML model training with PyTorch, TensorFlow, and Scikit-learn. Transfer learning with pre-trained models like YOLO, SAM, and BERT available.',
        'integration': 'We seamlessly integrate AI models into web and mobile apps using Flask/FastAPI, React Native, and TensorFlow Lite for on-device inference.',
        'price': 'Our pricing is customized based on project scope. Contact us for a free consultation and quote tailored to your needs.',
        'cost': 'Project costs vary based on complexity. Simple chatbots start at $5K, while enterprise solutions range from $20K-$100K+. Let\'s discuss your requirements.',
        'contact': 'You can reach us at hello@arnasol.com or use the contact form on our website. We typically respond within 24 hours.',
        'hello': 'Hello! 👋 How can I help you with your AI needs today?',
        'hi': 'Hi there! 😊 What AI solution are you looking for?',
        'thank': 'You\'re welcome! Feel free to ask if you have more questions.',
        'bye': 'Goodbye! Feel free to return anytime you need AI assistance.'
    }

    # Check for matches
    response = None
    for key, value in services.items():
        if key in message:
            response = value
            break

    # Default response if no match
    if not response:
        response = random.choice([
            "I'd be happy to help with that! Could you provide more details about your AI requirements?",
            "Great question! We offer various AI solutions. Could you specify which area interests you most?",
            "I can definitely assist with that. To give you the best recommendation, could you tell me more about your use case?",
            "That's something we specialize in! Would you like to schedule a consultation with our AI experts?",
            "Excellent choice! We have extensive experience in this area. What specific features are you looking for?"
        ])

    return response


def save_to_database(name, email, phone, message, timestamp):
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  email TEXT,
                  phone TEXT,
                  message TEXT,
                  timestamp TEXT,
                  status TEXT DEFAULT 'unread')''')

    c.execute("INSERT INTO contacts (name, email, phone, message, timestamp) VALUES (?, ?, ?, ?, ?)",
              (name, email, phone, message, timestamp))

    conn.commit()
    conn.close()

def send_email_notification(name, email, phone, message, current_date):
    resend.api_key = RESEND_KEY
    template_path = Path(__file__).parent / 'templates' / 'contact_notification.html'

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()

        html_content = html_template
        html_content = html_content.replace('__NAME__', name)
        html_content = html_content.replace('__EMAIL__', email)
        html_content = html_content.replace('__DATE__', current_date)
        html_content = html_content.replace('__MESSAGE__', message.replace('\n', '<br>'))

        if phone and phone.strip():
            html_content = html_content.replace('__PHONE__', phone)
            html_content = html_content.replace('<!--PHONE_SECTION_START-->', '')
            html_content = html_content.replace('<!--PHONE_SECTION_END-->', '')
        else:
            import re
            pattern = r'<!--PHONE_SECTION_START-->.*?<!--PHONE_SECTION_END-->'
            html_content = re.sub(pattern, '', html_content, flags=re.DOTALL)

    except Exception as e:
        print(f"Template error: {e}, using fallback")
        html_content = f"""
        <h1>New Contact from {name}</h1>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
        <p><strong>Message:</strong></p>
        <p>{message.replace(chr(10), '<br>')}</p>
        <p><small>Received: {current_date}</small></p>
        """
    try:
        params = {
            "from": "ARNASOL <onboarding@resend.dev>",
            "to": ["abdullaharshado99@gmail.com"],
            "subject": f"📬 New Contact Form Submission from {name}",
            "html": html_content,
            "reply_to": email
        }

        response = resend.Emails.send(params)
        print(f"✅ Email sent successfully. ID: {response['id']}")
        return True

    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

# def send_email_notification(name, email, phone, message, timestamp):
#     socket.setdefaulttimeout(10)
#
#     sender_email = Sender_Email
#     sender_password = SENDER_KEY
#     receiver_email = Receiver_Email
#
#     msg = MIMEMultipart('alternative')
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = f"New Contact Form Submission from {name}"
#
#     template_path = Path(__file__).parent / 'templates' / 'contact_notification.html'
#
#     try:
#         with open(template_path, 'r', encoding='utf-8') as f:
#             html_template = f.read()
#
#         html_content = html_template
#         html_content = html_content.replace('__NAME__', name)
#         html_content = html_content.replace('__EMAIL__', email)
#         html_content = html_content.replace('__DATE__', timestamp)
#         html_content = html_content.replace('__MESSAGE__', message.replace('\n', '<br>'))
#
#         if phone and phone.strip():
#             html_content = html_content.replace('__PHONE__', phone)
#             html_content = html_content.replace('<!--PHONE_SECTION_START-->', '')
#             html_content = html_content.replace('<!--PHONE_SECTION_END-->', '')
#         else:
#             pattern = r'<!--PHONE_SECTION_START-->.*?<!--PHONE_SECTION_END-->'
#             html_content = re.sub(pattern, '', html_content, flags=re.DOTALL)
#
#     except Exception as e:
#         print(f"Error reading template: {e}")
#         html_content = f"""
#         <h1>New Contact from {name}</h1>
#         <p><strong>Email:</strong> {email}</p>
#         <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
#         <p><strong>Message:</strong></p>
#         <p>{message}</p>
#         <p><small>Received: {timestamp}</small></p>
#         """
#
#     msg.attach(MIMEText(html_content, 'html'))
#
#     try:
#         server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.send_message(msg)
#         server.quit()
#         print("✅ Email sent successfully")
#         return True
#     except socket.timeout:
#         print("❌ Connection timeout - SMTP may be blocked")
#         return False
#     except Exception as e:
#         print(f"❌ Email error: {e}")
#         return False
#     finally:
#         socket.setdefaulttimeout(None)



