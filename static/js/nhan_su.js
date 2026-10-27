document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // 1. XỬ LÝ ẨN/HIỆN MODAL THÊM MỚI HỒ SƠ
    // ==========================================
    const modal = document.getElementById('modalAddNew');
    const backdrop = document.getElementById('modalBackdrop');
    const panel = document.getElementById('modalPanel');
    
    const btnOpen = document.getElementById('btnAddNew');
    const btnClose = document.getElementById('btnCloseModal');
    const btnCancel = document.getElementById('btnCancelModal');

    if(btnOpen && modal) {
        function openModal() {
            modal.classList.remove('hidden');
            setTimeout(() => {
                backdrop.classList.remove('opacity-0');
                backdrop.classList.add('opacity-100');
                panel.classList.remove('opacity-0', 'translate-y-4', 'sm:scale-95');
                panel.classList.add('opacity-100', 'translate-y-0', 'sm:scale-100');
            }, 10);
        }

        function closeModal() {
            backdrop.classList.remove('opacity-100');
            backdrop.classList.add('opacity-0');
            panel.classList.remove('opacity-100', 'translate-y-0', 'sm:scale-100');
            panel.classList.add('opacity-0', 'translate-y-4', 'sm:scale-95');
            setTimeout(() => { modal.classList.add('hidden'); }, 300);
        }

        btnOpen.addEventListener('click', openModal);
        btnClose.addEventListener('click', closeModal);
        btnCancel.addEventListener('click', closeModal);
    }

    // ==========================================
    // 2. XỬ LÝ LOGIC "CHỨC VỤ THÔNG MINH"
    // ==========================================
    const danhMucChucVu = {
        'trung_doan': ['Trung đoàn trưởng', 'Chính ủy Trung đoàn', 'Phó Trung đoàn trưởng', 'Phó Chính ủy Trung đoàn', 'Chủ nhiệm', 'Trưởng ban', 'Trợ lý (Khối Cơ quan)'],
        'tieu_doan': ['Tiểu đoàn trưởng', 'Chính trị viên Tiểu đoàn', 'Phó Tiểu đoàn trưởng', 'Chính trị viên phó Tiểu đoàn', 'Trợ lý Tiểu đoàn'],
        'dai_doi': ['Đại đội trưởng', 'Chính trị viên Đại đội', 'Phó Đại đội trưởng', 'Chính trị viên phó Đại đội'],
        'trung_doi': ['Trung đội trưởng']
    };

    const selectCap = document.getElementById('selectCapDonVi');
    const selectChucVu = document.getElementById('selectChucVu');

    if(selectCap && selectChucVu) {
        selectCap.addEventListener('change', function() {
            const cap = this.value;
            selectChucVu.innerHTML = ''; 

            if (cap && danhMucChucVu[cap]) {
                selectChucVu.disabled = false; 
                selectChucVu.add(new Option('-- Chọn chức vụ cụ thể --', ''));
                
                danhMucChucVu[cap].forEach(chucVu => {
                    selectChucVu.add(new Option(chucVu, chucVu));
                });
            } else {
                selectChucVu.disabled = true;
                selectChucVu.add(new Option('Vui lòng chọn cấp đơn vị trước', ''));
            }
        });
    }

    // ==========================================
    // 3. XỬ LÝ UPLOAD EXCEL SĨ QUAN NGẦM (AJAX)
    // ==========================================
    const btnTriggerExcel = document.getElementById('btnTriggerExcel');
    const fileExcelSQ = document.getElementById('fileExcelSQ');
    const formExcelSQ = document.getElementById('formExcelSQ');

    if(btnTriggerExcel && fileExcelSQ) {
        // Kích hoạt thẻ input type=file ẩn
        btnTriggerExcel.addEventListener('click', () => {
            fileExcelSQ.click();
        });

        // Bắt sự kiện người dùng đã chọn file
        fileExcelSQ.addEventListener('change', function() {
            if(this.files.length > 0) {
                const formData = new FormData(formExcelSQ);
                
                // Trạng thái chờ
                btnTriggerExcel.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
                btnTriggerExcel.disabled = true;

                // Gửi dữ liệu tới Backend
                fetch('/api/upload-excel-sq', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if(data.status === 'success') {
                        alert(data.message);
                        window.location.reload(); 
                    } else {
                        alert('Lỗi: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Đã xảy ra lỗi hệ thống khi upload file.');
                })
                .finally(() => {
                    // Reset lại giao diện nút
                    btnTriggerExcel.innerHTML = '<i class="fa-solid fa-file-excel"></i> Nhập Excel SQ';
                    btnTriggerExcel.disabled = false;
                    formExcelSQ.reset(); 
                });
            }
        });
    }
// ==========================================
    // 4. XỬ LÝ NÚT XÓA TẤT CẢ (DEMO)
    // ==========================================
    const btnDeleteAll = document.getElementById('btnDeleteAll');
    if(btnDeleteAll) {
        btnDeleteAll.addEventListener('click', () => {
            if(confirm('Bạn có chắc chắn muốn XÓA TOÀN BỘ dữ liệu Sĩ quan? Hành động này không thể hoàn tác!')) {
                btnDeleteAll.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xóa...';
                btnDeleteAll.disabled = true;

                fetch('/api/delete-all-sq', { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if(data.status === 'success') {
                        alert(data.message);
                        window.location.reload();
                    } else {
                        alert('Lỗi: ' + data.message);
                        btnDeleteAll.innerHTML = '<i class="fa-solid fa-trash-can"></i> Xóa tất cả';
                        btnDeleteAll.disabled = false;
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('Lỗi hệ thống!');
                    btnDeleteAll.innerHTML = '<i class="fa-solid fa-trash-can"></i> Xóa tất cả';
                    btnDeleteAll.disabled = false;
                });
            }
        });
    }
});