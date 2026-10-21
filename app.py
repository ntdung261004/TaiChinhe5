from flask import Flask, render_template

app = Flask(__name__)

# Trang chào (Landing / Sau này là Login)
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Trang Tổng quan
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Trang Quản lý Hồ sơ
@app.route('/nhan-su')
def nhan_su():
    return render_template('nhan_su.html')

@app.route('/bang-luong')
def bang_luong():
    return render_template('bang_luong.html')
if __name__ == '__main__':
    app.run(debug=True, port=5000)