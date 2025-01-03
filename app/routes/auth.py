from flask import Blueprint, request, jsonify
from ..models import User, OTP, db
from app import bcrypt
from ..utils import generate_otp, send_otp_fonnte
from datetime import datetime
import logging
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)

auth_bp = Blueprint('auth', __name__)

# Registrasi


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validasi input
    if not all([name, email, phone, password, confirm_password]):
        return jsonify({'error': 'Semua kolom harus diisi'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Kata sandi tidak cocok'}), 400

    # Validasi email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return jsonify({'error': 'Format email tidak valid'}), 400

    # Validasi nomor telepon
    if not phone.isdigit() or len(phone) < 10:
        return jsonify({'error': 'Nomor telepon tidak valid'}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Periksa apakah user sudah ada
    user = User.query.filter((User.email == email) |
                             (User.phone == phone)).first()
    if user:
        return jsonify({'error': 'Pengguna sudah ada'}), 400

    # Simpan user ke database
    new_user = User(name=name, email=email, phone=phone,
                    password=hashed_password)
    db.session.add(new_user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Kesalahan menyimpan pengguna: {}'.format(str(e))}), 500

    # Generate OTP
    otp = generate_otp()
    new_otp = OTP(phone=phone, otp=otp, user_id=new_user.id,
                  timestamp=datetime.utcnow())
    db.session.add(new_otp)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Kesalahan menyimpan OTP: {}'.format(str(e))}), 500

    # Kirim OTP melalui WhatsApp
    send_result = send_otp_fonnte(phone, otp)
    if send_result.get('error'):
        return jsonify({'error': 'Gagal mengirim OTP melalui WhatsApp'}), 500

    return jsonify({'Pesan': 'Pengguna berhasil terdaftar. OTP dikirim ke WhatsApp.'}), 201

# login


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    # Validasi input data
    if not data or not data.get('email_or_phone') or not data.get('password'):
        return jsonify({'error': 'Email/Phone and Password are required'}), 400

    email_or_phone = data.get('email_or_phone').strip()
    password = data.get('password')

    # Cari user berdasarkan email atau nomor telepon
    user = User.query.filter((User.email == email_or_phone) | (
        User.phone == email_or_phone)).first()

    if not user:
        return jsonify({'error': 'Invalid email/phone or password'}), 400

    # Verifikasi password dengan bcrypt
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email/phone or password'}), 400

    # Periksa apakah akun sudah diverifikasi
    if not user.is_verified:
        return jsonify({'error': 'Your account is not verified. Please verify your account to login.'}), 403

    # Login berhasil
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'phone': user.phone
        }
    }), 200


@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.json
    phone = data.get('phone')

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'error': 'Phone number not found'}), 404

    otp = generate_otp()
    new_otp = OTP(phone=phone, otp=otp, timestamp=datetime.utcnow())
    db.session.add(new_otp)
    db.session.commit()

    send_otp_fonnte(phone, otp)

    return jsonify({'message': 'OTP sent for password reset'}), 200


# Confirm OTP
@auth_bp.route('/confirm-otp', methods=['POST'])
def confirm_otp():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')

    otp_record = OTP.query.filter_by(phone=phone, otp=otp).first()
    if not otp_record:
        return jsonify({'error': 'Invalid OTP'}), 400

    # Check if OTP is expired (5 minutes)
    if (datetime.utcnow() - otp_record.timestamp).total_seconds() > 300:
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({'error': 'OTP expired'}), 400

    return jsonify({'message': 'OTP verified successfully'}), 200


# Reset Password
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    otp_record = OTP.query.filter_by(phone=phone, otp=otp).first()
    if not otp_record:
        return jsonify({'error': 'Invalid OTP'}), 400

    user = User.query.filter_by(phone=phone).first()
    if user:
        hashed_password = bcrypt.generate_password_hash(
            new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

    db.session.delete(otp_record)
    db.session.commit()

    return jsonify({'message': 'Password reset successfully'}), 200
