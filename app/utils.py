import random
import requests
import logging


def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp_fonnte(phone, otp):
    url = "https://api.fonnte.com/send"
    token = "EW2WfJato3hJ9wVWr2bF"

    # Pesan dengan nama aplikasi EcoFood
    message = (
        f"Halo! Selamat datang di EcoFood 🌱\n\n"
        f"Kode OTP Anda adalah: {otp}\n"
        f"Silakan masukkan kode ini untuk melanjutkan proses verifikasi akun Anda.\n\n"
        f"Jangan bagikan kode ini kepada siapa pun demi keamanan akun Anda.\n\n"
        f"Terima kasih telah memilih EcoFood! 🌟"
    )

    payload = {
        # Nomor telepon tujuan (format internasional tanpa "+")
        'target': phone,
        'message': message,
    }

    headers = {
        'Authorization': token,
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # Raise error jika respons tidak sukses
        return response.json()  # Kembalikan respons JSON
    except requests.RequestException as e:
        logging.error(f"Error sending OTP via Fonnte: {e}")
        return {'error': 'Failed to send OTP'}
