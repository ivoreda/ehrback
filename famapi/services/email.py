# reference flask email package
from datetime import datetime
from flask import jsonify
from flask_mail import Message
from famapi.settings.extensions import mail

import logging


# mail_logger = logging.getLogger('flask_mail')
# mail_logger.setLevel(logging.INFO)
# mail_logger.addHandler(logging.StreamHandler())


class Email:
    def __init__(self, subject="Famwork Electronic Record",
                 sender="noreply@famEHR.com"):

        self.subject = subject
        self.sender = sender
        self.date_created = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        self.mail = mail

    def send_email(self, recipients, data):

        msg = Message("ReuniteTag Enquiry Form", sender=self.sender, recipients=[recipients])
        msg.html = '''
                    <div style="width:400px;">
                        <div style="background-color:#30628c;padding:20px;color:#fff;text-align:center;">
                            <h2>ReuniteTag ENQUIRIES</h2>
                        </div>
                        <div  style="padding:20px;">
                          <h3 style="margin-bottom:-10px; font-size:16px">Date Created</h3>
                          <p>{}</p>
                          <h3 style="margin-bottom:-10px; font-size:16px">Message </h3>
                          <p>{}</p>
                        </div>
                    </div>
                    '''.format(self.date_created, data)
        msg.body = data
        try:
            self.mail.connect()
            self.mail.send(msg)
            return {'status': 200, 'msg': 'Message sent'}

        except Exception as e:
            return jsonify(msg=str(e))

    def send_email_for_password_reset(self, recipients, data):
        msg = Message("Mecury Learning Password Reset Link", sender="noreply@ctrlearn.com", recipients=[recipients])
        msg.html = '''
                    <div style="width:400px;">
                        <div style="background-color:#30628c;padding:20px;color:#fff;text-align:center;">
                            <h2>Reset Password</h2>
                        </div>
                        <div  style="padding:20px;">
                          <h3 style="margin-bottom:-10px; font-size:16px">Date Created</h3>
                          <p>{}</p>
                          <h3 style="margin-bottom:-10px;font-size:16px">Reset_url</h3>
                          <p>{}</p>
                        </div>
                    </div>
                    '''.format(self.date_created, data)
        msg.body = f'Click the following link to reset your password: {data}'
        try:
            self.mail.connect()
            self.mail.send(msg)
            return {'status': 200, 'msg': 'Password reset instructions sent to email'}

        except Exception as e:
            return jsonify(msg=str(e))
