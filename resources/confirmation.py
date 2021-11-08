import traceback

from flask import render_template, make_response
from flask_restful import Resource
from time import time

from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

NOT_FOUND = "Confirmation reference not found."
EXPIRED = "The link has expired."
ALREADY_CONFIRMED = "Registration has already been confirmed."
USER_NOT_FOUND = "User reference not found."
RESEND_SUCCESFUL = "Email confirmation succesfully re-sent"
RESEND_FAIL = "Internal server error. Failed to resend confirmation email."

confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Returns confirmations HTML page"""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND},404

        if confirmation.expired:
            return {"message": EXPIRED},400

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED},400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_path.html", email=confirmation.user.email), 200, headers)


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
            return {"message": RESEND_SUCCESFUL},200

        except MailGunException as e:
            return {"message": str(e)}, 500

        except:
            traceback.print_exc()
            return {"message": RESEND_FAIL}, 500