import pandas as pd
import re
from models import db, QuanNhan

def process_excel_sq(file):
    try:
        # 1. Tìm dòng tiêu đề
        df_raw = pd.read_excel(file, header=None, nrows=20)
        header_row_index = -1
        core_cols = ['Họ tên', 'CB', 'CV']
        
        for index, row in df_raw.iterrows():
            row_values = [re.sub(r'\s+', ' ', str(val)).strip() for val in row.values if pd.notna(val)]
            if all(col in row_values for col in core_cols):
                header_row_index = index
                break
        
        if header_row_index == -1:
            return {'status': 'error', 'message': 'Không tìm thấy dòng tiêu đề chứa: Họ tên, CB, CV.'}

        # 2. Đọc file chính thức
        file.seek(0)
        df = pd.read_excel(file, header=header_row_index)
        df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
        
        def get_val(row, possible_cols, default_val):
            for col in possible_cols:
                if col in df.columns and pd.notna(row[col]):
                    return row[col]
            return default_val

        count_added = 0
        duplicates = []
        
        # 3. Quét dữ liệu
        for index, row in df.iterrows():
            ho_ten = get_val(row, ['Họ tên'], '')
            ho_ten_clean = str(ho_ten).strip().upper()
            
            if not ho_ten or ho_ten_clean == '' or ho_ten_clean == 'NAN' or ho_ten_clean.startswith('CỘNG') or ho_ten_clean.startswith('TỔNG'):
                continue

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

            existing_sq = QuanNhan.query.filter_by(loai='SQ', ho_ten=str(ho_ten).strip()).first()

            if existing_sq:
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
                sq_moi = QuanNhan(
                    loai='SQ', ho_ten=str(ho_ten).strip(),
                    cap_bac_hs=new_cb, chuc_vu_hs=new_cv, dtqs=new_dtqs, trach_nhiem=new_tn, ubkt=new_ubkt,
                    nhap_ngu=nn_str, don_vi=new_dv, nguoi_phu_thuoc=new_npt, so_tai_khoan=stk
                )
                db.session.add(sq_moi)
                count_added += 1
        
        db.session.commit()
        return {'status': 'success', 'added_count': count_added, 'duplicates': duplicates}
        
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}