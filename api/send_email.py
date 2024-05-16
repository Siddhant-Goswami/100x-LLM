import os
import resend
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

params: resend.Emails.SendParams = {
    "sender": "hello@overpoweredjobs.com",
    "to": ["siddhant@100xengineers.com"],
    "subject": "Resend Email Test",
    "html": "<strong>it works!</strong>",
}

email = resend.Emails.send(params)
print(email)
