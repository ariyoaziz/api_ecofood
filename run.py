from app import create_app

# Membuat instance aplikasi dan menjalankan server
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
