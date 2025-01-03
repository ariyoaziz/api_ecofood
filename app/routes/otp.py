from flask import Blueprint, request, jsonify
from ..models import User, OTP, db
from datetime import datetime, timedelta


# Blueprint untuk OTP
otp_bp = Blueprint('otp', __name__)


# Endpoint untuk verifikasi OTP
@otp_bp.route('/verify', methods=['POST'])
def verify_otp():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')

    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP are required'}), 400

    otp_record = OTP.query.filter_by(phone=phone, otp=otp).first()
    if not otp_record:
        return jsonify({'error': 'Invalid OTP'}), 400

    if (datetime.utcnow() - otp_record.timestamp) > timedelta(minutes=5):
        return jsonify({'error': 'OTP expired'}), 400

    user = User.query.filter_by(phone=phone).first()
    if user:
        user.is_verified = True
        db.session.commit()
        db.session.delete(otp_record)
        db.session.commit()

        return jsonify({'message': 'Account verified successfully'}), 200

    return jsonify({'error': 'User not found'}), 404
