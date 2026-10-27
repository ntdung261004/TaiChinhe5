from flask import Blueprint, request, jsonify
from models import db, QuanNhan
from services.excel_service import process_excel_sq

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/delete-all-sq', methods=['DELETE'])
def delete_all_sq():
    try:
        QuanNhan.query.filter_by(loai='SQ').delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Đã xóa toàn bộ dữ liệu Sĩ quan!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Lỗi: {str(e)}'})

@api_bp.route('/upload-excel-sq', methods=['POST'])
def upload_excel_sq():
    if 'fileExcel' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên'})
    
    file = request.files['fileExcel']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Chưa chọn file'})

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        result = process_excel_sq(file)
        return jsonify(result)
            
    return jsonify({'status': 'error', 'message': 'Sai định dạng file'})

@api_bp.route('/update-duplicates-sq', methods=['POST'])
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