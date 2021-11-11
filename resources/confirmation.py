import traceback

from flask import render_template, make_response
from flask_restful import Resource
from time import time
from libs.strings import gettext
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema


confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Returns confirmations HTML page"""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": gettext("not_found")},404

        if confirmation.expired:
            return {"message": gettext("expired")},400

        if confirmation.confirmed:
            return {"message": gettext("already_confirmed")},400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=confirmation.user.email), 200, headers)


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """Returns confirmations for a give user. Use for testin"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND},404

        return {
            "current_time": int(time()),
            "confirmation": [confirmation_schema.dump(each) for each in user.confirmation.order_by(ConfirmationModel.expire_at)]
        },200

    @classmethod
    def post(cls, user_id: int):
        """Resend confirmation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED},400
                else:
                    confirmation.force_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("resend_succesful")},200

        except MailGunException as e:
            return {"message": str(e)}, 500

        except:
            traceback.print_exc()
            return {"message": gettext("resend_fail")}, 500