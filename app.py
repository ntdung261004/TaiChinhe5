import os
import re
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate

# Import DB và Model từ file models.py vừa tạo
from models import db, QuanNhan 

app = Flask(__name__)
app.secret_key = 'taichinh_e5_secret_key'

# 1. Cấu hình đường dẫn Database
basedir = os.path.abspath(os.path.dirname(__name__))
db_path = os.path.join(basedir, 'database')
if not os.path.exists(db_path):
    os.makedirs(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_path, 'luong_trungdoan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Khởi tạo liên kết DB với App
db.init_app(app)
migrate = Migrate(app, db)

# --- CÁC ĐƯỜNG DẪN (ROUTES) GIỮ NGUYÊN NHƯ CŨ ---
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/nhan-su')
def nhan_su():
    tong_sq = QuanNhan.query.filter_by(loai='SQ').count()
    tong_qncn = QuanNhan.query.filter_by(loai='QNCN').count()
    tong_so = tong_sq + tong_qncn
    danh_sach_sq = QuanNhan.query.filter_by(loai='SQ').all()
    return render_template('nhan_su.html', ds_sq=danh_sach_sq, tong_so=tong_so, tong_sq=tong_sq, tong_qncn=tong_qncn)

@app.route('/bang-luong')
def bang_luong():
    return render_template('bang_luong.html')

# Cập nhật API Upload Excel
@app.route('/api/upload-excel-sq', methods=['POST'])
def upload_excel_sq():
    if 'fileExcel' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên'})
    
    file = request.files['fileExcel']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Chưa chọn file'})

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            df_raw = pd.read_excel(file, header=None, nrows=20)
            header_row_index = -1
            core_cols = ['Họ tên', 'CB', 'CV']
            
            for index, row in df_raw.iterrows():
                row_values = [re.sub(r'\s+', ' ', str(val)).strip() for val in row.values if pd.notna(val)]
                if all(col in row_values for col in core_cols):
                    header_row_index = index
                    break
            
            if header_row_index == -1:
                return jsonify({'status': 'error', 'message': 'Không tìm thấy dòng tiêu đề chứa: Họ tên, CB, CV.'})

            file.seek(0)
            df = pd.read_excel(file, header=header_row_index)
            df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
            
            def get_val(row, possible_cols, default_val):
                for col in possible_cols:
                    if col in df.columns and pd.notna(row[col]):
                        return row[col]
                return default_val

            count_added = 0
            for index, row in df.iterrows():
                ho_ten = get_val(row, ['Họ tên'], '')
                ho_ten_clean = str(ho_ten).strip().upper()
                
                if not ho_ten or ho_ten_clean == '' or ho_ten_clean == 'NAN' or ho_ten_clean.startswith('CỘNG') or ho_ten_clean.startswith('TỔNG'):
                    continue

                # Xử lý số tài khoản (xóa đuôi .0 nếu Excel tự định dạng là số thập phân)
                stk = str(get_val(row, ['Số tài khoản', 'STK'], '')).strip()
                if stk.endswith('.0'):
                    stk = stk[:-2]

                # Xử lý ngày tháng nhập ngũ sang MM/YYYY
                nn_raw = get_val(row, ['NN', 'Nhập ngũ'], '')
                nn_str = ''
                if pd.notna(nn_raw) and str(nn_raw).strip() != '':
                    if isinstance(nn_raw, pd.Timestamp) or type(nn_raw).__name__ == 'datetime':
                        nn_str = nn_raw.strftime('%m/%Y')
                    else:
                        try:
                            nn_str = pd.to_datetime(nn_raw).strftime('%m/%Y')
                        except:
                            nn_str = str(nn_raw).strip()

                sq_moi = QuanNhan(
                    loai='SQ',
                    ho_ten=str(ho_ten).strip(),
                    cap_bac_hs=float(get_val(row, ['CB', 'Cấp bậc'], 0.0)),
                    chuc_vu_hs=float(get_val(row, ['CV', 'Chức vụ'], 0.0)),
                    dtqs=float(get_val(row, ['PCĐTQS', 'ĐTQS'], 0.0)),
                    trach_nhiem=float(get_val(row, ['PCTN', 'TN', 'Phụ cấp trách nhiệm'], 0.0)),
                    ubkt=float(get_val(row, ['UBKT'], 0.0)),
                    nhap_ngu=nn_str,
                    don_vi=str(get_val(row, ['ĐƠN VỊ', 'ĐV', 'Đơn vị'], '')).strip(),
                    nguoi_phu_thuoc=int(get_val(row, ['Số người phụ thuộc', 'NPT'], 0)),
                    so_tai_khoan=stk
                )
                db.session.add(sq_moi)
                count_added += 1
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'Đã import thành công {count_added} hồ sơ!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Lỗi hệ thống: {str(e)}'})
            
    return jsonify({'status': 'error', 'message': 'Sai định dạng file'})

# Thêm API Xóa tất cả Sĩ quan (Dùng cho Demo/Test)
@app.route('/api/delete-all-sq', methods=['DELETE'])
def delete_all_sq():
    try:
        QuanNhan.query.filter_by(loai='SQ').delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Đã xóa toàn bộ dữ liệu Sĩ quan!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Lỗi: {str(e)}'})
if __name__ == '__main__':
    app.run(debug=True, port=5000)