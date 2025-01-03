# from models import User, OTP
# from . import db
# from flask import jsonify, request, app
# from flask import Blueprint, request, jsonify
# from .models import User, OTP
# from . import db, bcrypt
# import requests
# import random
# import time
# from datetime import datetime
# from app import app


# main = Blueprint('main', __name__)

# # Helper function for OTP


# def send_otp_fonnte(phone, otp):
#     url = "https://api.fonnte.com/send"
#     token = "EW2WfJato3hJ9wVWr2b"
#     payload = {
#         'target': phone,
#         'message': f"Your OTP: {otp}"
#     }
#     headers = {'Authorization': token}
#     response = requests.post(url, data=payload, headers=headers)
#     return response.json()

# # Registration
# # Route for registration


# @main.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     name = data.get('name')
#     email = data.get('email')
#     phone = data.get('phone')
#     password = data.get('password')
#     confirm_password = data.get('confirm_password')

#     # Validasi password
#     if password != confirm_password:
#         return jsonify({'error': 'Passwords do not match'}), 400

#     # Hash password
#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

#     # Cek apakah user sudah ada
#     user = User.query.filter((User.email == email) |
#                              (User.phone == phone)).first()
#     if user:
#         return jsonify({'error': 'User already exists'}), 400

#     # Buat user baru
#     new_user = User(name=name, email=email, phone=phone,
#                     password=hashed_password)
#     db.session.add(new_user)

#     try:
#         db.session.commit()  # Simpan user
#         app.logger.debug(f"User saved with ID: {new_user.id}")
#     except Exception as e:
#         db.session.rollback()
#         app.logger.error(f"Error saving user: {str(e)}")
#         return jsonify({'error': 'Error saving user'}), 500

#     # Pastikan user.id sudah ada setelah commit
#     if not new_user.id:
#         return jsonify({'error': 'Failed to retrieve user ID'}), 500

#     # Generate OTP
#     otp = str(random.randint(100000, 999999))

#     # Log OTP untuk memastikan OTP benar-benar dihasilkan
#     app.logger.debug(f"Generated OTP: {otp} for phone: {phone}")

#     # Simpan OTP ke dalam database
#     new_otp = OTP(phone=phone, otp=otp, user_id=new_user.id)
#     db.session.add(new_otp)

#     # Log sebelum commit OTP
#     app.logger.debug(f"Attempting to save OTP: {otp} for phone: {
#                      phone} and user_id: {new_user.id}")

#     try:
#         db.session.commit()  # Simpan OTP
#         app.logger.debug(f"OTP saved to DB for phone: {phone}, OTP: {otp}")
#     except Exception as e:
#         db.session.rollback()  # Rollback jika ada error
#         app.logger.error(f"Error saving OTP to database: {str(e)}")
#         return jsonify({'error': 'Error saving OTP'}), 500

#     # Kirim OTP melalui SMS (pastikan fungsi ini ada dan benar)
#     send_otp_fonnte(phone, otp)

#     # Berikan respon sukses
#     return jsonify({'message': 'User registered. Verify OTP sent to phone.'}), 201


# # Verify OTP
# @main.route('/verify', methods=['POST'])
# def verify_otp():
#     data = request.json
#     phone = data.get('phone')
#     otp = data.get('otp')

#     # Log input data for debugging
#     app.logger.debug(f"Verifying OTP for phone: {phone}, OTP: {otp}")

#     # Mencari OTP berdasarkan telepon dan kode OTP
#     otp_record = OTP.query.filter_by(phone=phone, otp=otp).first()
#     if not otp_record:
#         app.logger.debug(f"OTP not found for phone: {phone} and OTP: {otp}")
#         return jsonify({'error': 'Invalid OTP'}), 400

#     # Cek apakah OTP kadaluarsa (misalnya dalam 5 menit)
#     if (datetime.utcnow() - otp_record.timestamp).total_seconds() > 300:
#         return jsonify({'error': 'OTP expired'}), 400

#     user = User.query.filter_by(phone=phone).first()
#     if user:
#         user.is_verified = True
#         db.session.commit()

#     db.session.delete(otp_record)  # Hapus OTP setelah verifikasi
#     db.session.commit()

#     return jsonify({'message': 'Account verified successfully'}), 200


# # Login


# @main.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     email_or_phone = data.get('email_or_phone')
#     password = data.get('password')

#     user = User.query.filter((User.email == email_or_phone) | (
#         User.phone == email_or_phone)).first()
#     if not user or not bcrypt.check_password_hash(user.password, password):
#         return jsonify({'error': 'Invalid credentials'}), 400

#     if not user.is_verified:
#         return jsonify({'error': 'Account not verified'}), 403

#     return jsonify({'message': 'Login successful'}), 200


# # Request Password Reset

# @main.route('/request-password-reset', methods=['POST'])
# def request_password_reset():
#     data = request.json
#     phone = data.get('phone')

#     user = User.query.filter_by(phone=phone).first()
#     if not user:
#         return jsonify({'error': 'Phone number not found'}), 404

#     otp = str(random.randint(100000, 999999))
#     new_otp = OTP(phone=phone, otp=otp, timestamp=int(time.time()))
#     db.session.add(new_otp)
#     db.session.commit()

#     send_otp_fonnte(phone, otp)

#     return jsonify({'message': 'OTP sent for password reset'}), 200

# # Reset Password


# @main.route('/reset-password', methods=['POST'])
# def reset_password():
#     data = request.json
#     phone = data.get('phone')
#     otp = data.get('otp')
#     new_password = data.get('new_password')
#     confirm_password = data.get('confirm_password')

#     if new_password != confirm_password:
#         return jsonify({'error': 'Passwords do not match'}), 400

#     otp_record = OTP.query.filter_by(phone=phone, otp=otp).first()
#     if not otp_record:
#         return jsonify({'error': 'Invalid OTP'}), 400

#     user = User.query.filter_by(phone=phone).first()
#     if user:
#         hashed_password = bcrypt.generate_password_hash(
#             new_password).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()

#     db.session.delete(otp_record)
#     db.session.commit()

#     return jsonify({'message': 'Password reset successfully'}), 200
