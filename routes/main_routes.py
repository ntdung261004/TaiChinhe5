from flask import Blueprint, render_template
from models import QuanNhan

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def welcome():
    return render_template('welcome.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/nhan-su')
def nhan_su():
    tong_sq = QuanNhan.query.filter_by(loai='SQ').count()
    tong_qncn = QuanNhan.query.filter_by(loai='QNCN').count()
    tong_so = tong_sq + tong_qncn
    danh_sach_sq = QuanNhan.query.filter_by(loai='SQ').all()
    return render_template('nhan_su.html', ds_sq=danh_sach_sq, tong_so=tong_so, tong_sq=tong_sq, tong_qncn=tong_qncn)

@main_bp.route('/bang-luong')
def bang_luong():
    return render_template('bang_luong.html')