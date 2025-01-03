from flask import Blueprint, request, jsonify
from ..models import User
from .. import db  # Mengimpor db dengan benar dari app (bukan dari app.routes)
import re
# Blueprint untuk profile
profile_bp = Blueprint('profile', __name__)

# Fungsi untuk memeriksa format email


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

# Fungsi untuk memeriksa format nomor telepon


def is_valid_phone(phone):
    phone_regex = r'^\+?\d{10,15}$'
    return re.match(phone_regex, phone)

# Endpoint untuk mendapatkan profil pengguna


@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    email_or_phone = request.args.get('email_or_phone')

    if not email_or_phone:
        return jsonify({'error': 'Email or phone is required'}), 400

    # Cek apakah format email atau phone valid
    if not is_valid_email(email_or_phone) and not is_valid_phone(email_or_phone):
        return jsonify({'error': 'Invalid email or phone format'}), 400

    # Cek apakah parameter email_or_phone valid
    user = User.query.filter((User.email == email_or_phone) | (
        User.phone == email_or_phone)).first()

    if user:
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'is_verified': user.is_verified
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404
