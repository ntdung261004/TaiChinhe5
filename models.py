from flask_sqlalchemy import SQLAlchemy

# Khởi tạo đối tượng db độc lập
db = SQLAlchemy()

class QuanNhan(db.Model):
    __tablename__ = 'quan_nhan'
    id = db.Column(db.Integer, primary_key=True)
    loai = db.Column(db.String(20), nullable=False) # 'SQ' hoặc 'QNCN'
    ho_ten = db.Column(db.String(100), nullable=False)
    
    # Các trường Hệ số & Phụ cấp (Kiểu Float)
    cap_bac_hs = db.Column(db.Float, default=0.0)
    chuc_vu_hs = db.Column(db.Float, default=0.0)
    dtqs = db.Column(db.Float, default=0.0)          # Đặc thù quân sự
    trach_nhiem = db.Column(db.Float, default=0.0)   # Trách nhiệm
    ubkt = db.Column(db.Float, default=0.0)          # Ủy ban kiểm tra
    
    # Thông tin hành chính
    nhap_ngu = db.Column(db.String(20))
    don_vi = db.Column(db.String(100))
    nguoi_phu_thuoc = db.Column(db.Integer, default=0)
    so_tai_khoan = db.Column(db.String(50))
    trang_thai = db.Column(db.String(50), default='Đang công tác')