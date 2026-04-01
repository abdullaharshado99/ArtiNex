import resend
import sqlite3
from pathlib import Path
from Anna_pipeline.config import RAGConfig


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
    resend.api_key = RAGConfig.RESEND_KEY
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
            "to": [f"{RAGConfig.RECEIVER_EMAIL}"],
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








    # Initialize your embeddings
    embeddings = SentenceTransformerEmbeddings("sentence-transformers/all-MiniLM-L6-v2")

    # Create the semantic chunker with your embedding model
    splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",  # Options: "percentile", "standard_deviation", "interquartile"
        breakpoint_threshold_amount=95  # 95th percentile threshold
    )

    from semantic_chunker import SemanticChunker
    from sentence_transformers import SentenceTransformer

    # Initialize your sentence transformer model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Create chunker with your embedding model
    chunker = SemanticChunker(
        model_name='all-MiniLM-L6-v2',  # This will load the model internally
        max_chunk_size=1000,
        similarity_threshold=0.3
    )

    # Use it directly
    text = "Your long document text here..."
    chunks = chunker.semantic_chunk(text)

    from chonkie import SemanticChunker, AutoEmbeddings

    # Auto-detect and load the right embeddings handler
    embeddings = AutoEmbeddings.get_embeddings("all-MiniLM-L6-v2")

    # Create semantic chunker
    chunker = SemanticChunker(
        embeddings=embeddings,
        similarity_threshold=0.7,
        chunk_size=1000
    )

    # Chunk your text
    text = "Your long document text here..."
    chunks = chunker(text)


# | Model                        | Embedding Dimension |
# | ---------------------------- | ------------------- |
# | `all-MiniLM-L6-v2`           | 384                 |
# | `all-MiniLM-L12-v2`          | 384                 |
# | `all-mpnet-base-v2`          | 768                 |
# | `multi-qa-MiniLM-L6-cos-v1`  | 384                 |
# | `multi-qa-mpnet-base-dot-v1` | 768                 |
# | `paraphrase-MiniLM-L6-v2`    | 384                 |
# | `paraphrase-mpnet-base-v2`   | 768                 |
