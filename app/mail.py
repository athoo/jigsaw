from flask.ext.mail import Message

from app import app, mail

def send_email(to, subject, template):
    retcode = 0
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    try:
        mail.send(msg)
    except SMTPAuthenticationError, e:
        retcode = 2
    except SMTPServerDisconnected, e:
        retcode = 3
    except SMTPException, e:
        retcode = 1

    return retcode
