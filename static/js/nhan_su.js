document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. MODAL THÊM MỚI (Giữ nguyên) ---
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

    // --- 2. CHỨC VỤ THÔNG MINH (Giữ nguyên) ---
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

    // --- 3 & 4. XỬ LÝ UPLOAD EXCEL VÀ MODAL TRÙNG LẶP ---
    const btnTriggerExcel = document.getElementById('btnTriggerExcel');
    const fileExcelSQ = document.getElementById('fileExcelSQ');
    const formExcelSQ = document.getElementById('formExcelSQ');
    
    // UI Modal Trùng lặp
    const modalTrungLap = document.getElementById('modalTrungLap');
    const tbTrungLap = document.getElementById('tableTrungLapBody');
    const btnConfirmUpdate = document.getElementById('btnConfirmUpdate');
    
    let pendingDuplicates = []; // Biến lưu tạm dữ liệu trùng chờ xác nhận

    function showModalTrungLap() {
        modalTrungLap.classList.remove('hidden');
        setTimeout(() => {
            document.getElementById('modalTrungLapBackdrop').classList.remove('opacity-0');
            document.getElementById('modalTrungLapBackdrop').classList.add('opacity-100');
            document.getElementById('modalTrungLapPanel').classList.remove('opacity-0', 'translate-y-4', 'sm:scale-95');
            document.getElementById('modalTrungLapPanel').classList.add('opacity-100', 'translate-y-0', 'sm:scale-100');
        }, 10);
    }
    
    function hideModalTrungLap() {
        document.getElementById('modalTrungLapBackdrop').classList.remove('opacity-100');
        document.getElementById('modalTrungLapBackdrop').classList.add('opacity-0');
        document.getElementById('modalTrungLapPanel').classList.remove('opacity-100', 'translate-y-0', 'sm:scale-100');
        document.getElementById('modalTrungLapPanel').classList.add('opacity-0', 'translate-y-4', 'sm:scale-95');
        setTimeout(() => { 
            modalTrungLap.classList.add('hidden'); 
            window.location.reload(); // Đóng là reload để nhận dữ liệu mới thêm
        }, 300);
    }

    if(document.getElementById('btnCloseTrungLap')) document.getElementById('btnCloseTrungLap').addEventListener('click', hideModalTrungLap);
    if(document.getElementById('btnCancelTrungLap')) document.getElementById('btnCancelTrungLap').addEventListener('click', hideModalTrungLap);

    // Hàm render text Cũ -> Mới
    function renderDiff(oldVal, newVal) {
        if(oldVal == newVal) return `<span class="text-slate-500">${oldVal}</span>`;
        return `<span class="text-rose-400 line-through text-xs">${oldVal}</span> <i class="fa-solid fa-arrow-right text-slate-300 mx-1 text-xs"></i> <span class="text-emerald-600 font-bold">${newVal}</span>`;
    }

    if(btnTriggerExcel && fileExcelSQ) {
        btnTriggerExcel.addEventListener('click', () => { fileExcelSQ.click(); });

        fileExcelSQ.addEventListener('change', function() {
            if(this.files.length > 0) {
                const formData = new FormData(formExcelSQ);
                btnTriggerExcel.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
                btnTriggerExcel.disabled = true;

                fetch('/api/upload-excel-sq', { method: 'POST', body: formData })
                .then(response => response.json())
                .then(data => {
                    if(data.status === 'success') {
                        pendingDuplicates = data.duplicates || [];
                        
                        if(pendingDuplicates.length > 0) {
                            // CÓ TRÙNG LẶP -> Hiện Modal
                            let html = '';
                            pendingDuplicates.forEach(dup => {
                                html += `
                                <tr class="hover:bg-amber-50/50">
                                    <td class="px-4 py-2 font-bold text-slate-800">${dup.ho_ten}</td>
                                    <td class="px-4 py-2">${renderDiff(dup.old_dv, dup.new_dv)}</td>
                                    <td class="px-4 py-2 text-center">${renderDiff(dup.old_cb, dup.new_cb)}</td>
                                    <td class="px-4 py-2 text-center">${renderDiff(dup.old_cv, dup.new_cv)}</td>
                                </tr>`;
                            });
                            tbTrungLap.innerHTML = html;
                            document.getElementById('txtTrungLapCount').innerText = `Đã thêm ${data.added_count} hồ sơ mới. Đang chờ xử lý ${pendingDuplicates.length} hồ sơ trùng.`;
                            showModalTrungLap();
                        } else {
                            // KHÔNG TRÙNG LẶP -> Báo thành công, reload
                            alert(`Đã thêm mới thành công ${data.added_count} hồ sơ!`);
                            window.location.reload();
                        }
                    } else {
                        alert('Lỗi: ' + data.message);
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('Lỗi hệ thống khi upload.');
                })
                .finally(() => {
                    btnTriggerExcel.innerHTML = '<i class="fa-solid fa-file-excel"></i> Nhập Excel SQ';
                    btnTriggerExcel.disabled = false;
                    formExcelSQ.reset(); 
                });
            }
        });
    }

    // XÁC NHẬN CẬP NHẬT GHI ĐÈ
    if(btnConfirmUpdate) {
        btnConfirmUpdate.addEventListener('click', () => {
            btnConfirmUpdate.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang cập nhật...';
            btnConfirmUpdate.disabled = true;

            fetch('/api/update-duplicates-sq', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ duplicates: pendingDuplicates })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    alert(data.message);
                    window.location.reload();
                } else {
                    alert('Lỗi: ' + data.message);
                    btnConfirmUpdate.innerHTML = '<i class="fa-solid fa-rotate"></i> Cập nhật (Ghi đè)';
                    btnConfirmUpdate.disabled = false;
                }
            })
            .catch(err => {
                console.error(err);
                alert('Lỗi hệ thống khi ghi đè.');
                btnConfirmUpdate.innerHTML = '<i class="fa-solid fa-rotate"></i> Cập nhật (Ghi đè)';
                btnConfirmUpdate.disabled = false;
            });
        });
    }

    // --- 5. NÚT XÓA TẤT CẢ (DEMO) ---
    const btnDeleteAll = document.getElementById('btnDeleteAll');
    if(btnDeleteAll) {
        btnDeleteAll.addEventListener('click', () => {
            if(confirm('Bạn có chắc chắn muốn XÓA TOÀN BỘ dữ liệu Sĩ quan? Hành động này không thể hoàn tác!')) {
                btnDeleteAll.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xóa...';
                btnDeleteAll.disabled = true;
                fetch('/api/delete-all-sq', { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if(data.status === 'success') { window.location.reload(); } 
                    else { alert('Lỗi: ' + data.message); btnDeleteAll.innerHTML = '<i class="fa-solid fa-trash-can"></i> Xóa tất cả'; btnDeleteAll.disabled = false; }
                })
            }
        });
    }
});