import os
import re
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from models import db, QuanNhan

app = Flask(__name__)
app.secret_key = 'taichinh_e5_secret_key'

basedir = os.path.abspath(os.path.dirname(__name__))
db_path = os.path.join(basedir, 'database')
if not os.path.exists(db_path):
    os.makedirs(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_path, 'luong_trungdoan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

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

@app.route('/api/delete-all-sq', methods=['DELETE'])
def delete_all_sq():
    try:
        QuanNhan.query.filter_by(loai='SQ').delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Đã xóa toàn bộ dữ liệu Sĩ quan!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Lỗi: {str(e)}'})

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
            duplicates = [] # Danh sách chứa các hồ sơ bị trùng
            
            for index, row in df.iterrows():
                ho_ten = get_val(row, ['Họ tên'], '')
                ho_ten_clean = str(ho_ten).strip().upper()
                
                if not ho_ten or ho_ten_clean == '' or ho_ten_clean == 'NAN' or ho_ten_clean.startswith('CỘNG') or ho_ten_clean.startswith('TỔNG'):
                    continue

                # Lấy tất cả dữ liệu từ Excel cho dòng này
                stk_raw = get_val(row, ['Số tài khoản', 'STK'], '')
                stk = ''
                if pd.notna(stk_raw) and str(stk_raw).strip() != '':
                    if isinstance(stk_raw, float):
                        stk = str(int(stk_raw))
                    else:
                        stk = str(stk_raw).strip()
                        if stk.endswith('.0'): stk = stk[:-2]

                nn_raw = get_val(row, ['NN', 'Nhập ngũ'], '')
                nn_str = ''
                if pd.notna(nn_raw) and str(nn_raw).strip() != '':
                    try:
                        parsed_date = pd.to_datetime(nn_raw, errors='coerce')
                        nn_str = parsed_date.strftime('%m/%Y') if pd.notna(parsed_date) else str(nn_raw).strip()
                    except:
                        nn_str = str(nn_raw).strip()

                new_cb = float(get_val(row, ['CB', 'Cấp bậc'], 0.0))
                new_cv = float(get_val(row, ['CV', 'Chức vụ'], 0.0))
                new_dtqs = float(get_val(row, ['PCĐTQS', 'ĐTQS'], 0.0))
                new_tn = float(get_val(row, ['PCTN', 'TN', 'Phụ cấp trách nhiệm'], 0.0))
                new_ubkt = float(get_val(row, ['UBKT'], 0.0))
                new_dv = str(get_val(row, ['ĐƠN VỊ', 'ĐV', 'Đơn vị'], '')).strip()
                new_npt = int(get_val(row, ['Số người phụ thuộc', 'NPT'], 0))

                # Kiểm tra trùng lặp trong DB
                existing_sq = QuanNhan.query.filter_by(loai='SQ', ho_ten=str(ho_ten).strip()).first()

                if existing_sq:
                    # Lưu vào danh sách chờ xác nhận thay thế
                    duplicates.append({
                        'id': existing_sq.id,
                        'ho_ten': existing_sq.ho_ten,
                        'old_cb': existing_sq.cap_bac_hs, 'new_cb': new_cb,
                        'old_cv': existing_sq.chuc_vu_hs, 'new_cv': new_cv,
                        'old_dv': existing_sq.don_vi, 'new_dv': new_dv,
                        'new_dtqs': new_dtqs, 'new_tn': new_tn, 'new_ubkt': new_ubkt,
                        'new_nn': nn_str, 'new_npt': new_npt, 'new_stk': stk
                    })
                else:
                    # Chưa có -> Thêm mới ngay lập tức
                    sq_moi = QuanNhan(
                        loai='SQ', ho_ten=str(ho_ten).strip(),
                        cap_bac_hs=new_cb, chuc_vu_hs=new_cv, dtqs=new_dtqs, trach_nhiem=new_tn, ubkt=new_ubkt,
                        nhap_ngu=nn_str, don_vi=new_dv, nguoi_phu_thuoc=new_npt, so_tai_khoan=stk
                    )
                    db.session.add(sq_moi)
                    count_added += 1
            
            db.session.commit()
            
            # Trả về cả số lượng đã thêm và danh sách trùng lặp
            return jsonify({
                'status': 'success', 
                'added_count': count_added, 
                'duplicates': duplicates
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Lỗi hệ thống: {str(e)}'})
            
    return jsonify({'status': 'error', 'message': 'Sai định dạng file'})

# API Nhận lệnh xác nhận ghi đè dữ liệu trùng lặp
@app.route('/api/update-duplicates-sq', methods=['POST'])
def update_duplicates_sq():
    try:
        data = request.json
        duplicates_to_update = data.get('duplicates', [])
        count_updated = 0
        
        for dup in duplicates_to_update:
            sq = QuanNhan.query.get(dup['id'])
            if sq:
                sq.cap_bac_hs = dup['new_cb']
                sq.chuc_vu_hs = dup['new_cv']
                sq.dtqs = dup['new_dtqs']
                sq.trach_nhiem = dup['new_tn']
                sq.ubkt = dup['new_ubkt']
                sq.nhap_ngu = dup['new_nn']
                sq.don_vi = dup['new_dv']
                sq.nguoi_phu_thuoc = dup['new_npt']
                sq.so_tai_khoan = dup['new_stk']
                count_updated += 1
                
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Đã ghi đè thành công {count_updated} hồ sơ trùng lặp!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)