document.addEventListener('DOMContentLoaded', () => {
    const fileInput1 = document.getElementById('file-input1');
    const fileNameDisplay1 = document.getElementById('file-name1');
    const fileInfo1 = document.getElementById('file-info1');
    const alertMessage = document.querySelector('.alert');
    const downloadButton = document.getElementById('download-combined');
    const overlay = document.getElementById('overlay');
    const functionality = document.getElementById('functionality') ? document.getElementById('functionality').value : null;

    let firstFileLoaded = false;

    // Update alert message
    const updateAlert = (message, type = 'info') => {
        if (alertMessage) {
            alertMessage.textContent = message;
            alertMessage.className = `alert ${type}`;
            alertMessage.style.display = 'block';
        }
    };

    // Hide alert message
    const hideAlert = () => {
        if (alertMessage) {
            alertMessage.style.display = 'none';
        }
    };

    // Handle file upload
    const handleFileUpload = (fileInput, fileNameDisplay, fileInfo) => {
        const file = fileInput.files[0];
        if (!file) {
            updateAlert('يرجى تحميل الملف.', 'warning');
            return;
        }

        const fileName = file.name;
        const fileExtension = fileName.split('.').pop().toLowerCase();

        if (fileExtension !== 'xlsx') {
            updateAlert('يرجى تحميل ملف بصيغة .xlsx فقط.', 'warning');
            removeFile(fileInput, fileNameDisplay);
            return;
        }

        fileNameDisplay.textContent = fileName;
        fileInfo.classList.remove('hidden');
        firstFileLoaded = true;
        updateAlert('ملف جاهز للتحميل', 'info');
    };

    // Remove file and reset
    const removeFile = (fileInput, fileNameDisplay) => {
        fileInput.value = ''; // Clear the file input
        fileNameDisplay.textContent = ''; // Clear the displayed file name
        if (fileInfo1) {
            fileInfo1.classList.add('hidden'); // Hide the file info
        }
        firstFileLoaded = false; // Update the file loaded status
        updateAlert('يرجى تحميل الملف.', 'warning');
    };

    // Preview file (for development or additional features)
    const previewFile = (fileInput) => {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            alert(`معاينة الملف: ${file.name}`);
        } else {
            updateAlert('لا يوجد ملف لمعاينته.', 'warning');
        }
    };

    // Handle file drop event
    const handleDrop = (e, fileInput, fileNameDisplay, fileInfo) => {
        e.preventDefault();
        overlay.classList.remove('active');
        fileInput.files = e.dataTransfer.files;
        handleFileUpload(fileInput, fileNameDisplay, fileInfo);
    };

    // Show overlay when dragging a file
    document.addEventListener('dragenter', (e) => {
        if (e.dataTransfer.items && e.dataTransfer.items[0].kind === 'file') {
            overlay.classList.add('active');
        }
    });

    // Hide overlay when leaving the drag area
    document.addEventListener('dragleave', (e) => {
        if (e.clientX === 0 && e.clientY === 0) {
            overlay.classList.remove('active');
        }
    });

    // Prevent default behavior on dragover
    overlay.addEventListener('dragover', (e) => e.preventDefault());

    // Handle the drop event
    overlay.addEventListener('drop', (e) => {
        handleDrop(e, fileInput1, fileNameDisplay1, fileInfo1);
    });

    // Handle manual file input changes
    if (fileInput1) {
        fileInput1.addEventListener('change', () => handleFileUpload(fileInput1, fileNameDisplay1, fileInfo1));
    }

    // Preview button
    const previewButton = document.getElementById('preview-file1');
    if (previewButton) {
        previewButton.addEventListener('click', () => previewFile(fileInput1));
    }

    // Update button (allows for re-uploading)
    const updateButton = document.getElementById('update-file1');
    if (updateButton) {
        updateButton.addEventListener('click', () => fileInput1.click());
    }

    // Remove button
    const removeButton = document.getElementById('remove-file1');
    if (removeButton) {
        removeButton.addEventListener('click', () => removeFile(fileInput1, fileNameDisplay1));
    }

    // Handle form submission using fetch (AJAX)
    if (downloadButton) {
        downloadButton.addEventListener('click', function(event) {
            event.preventDefault();

            const file = fileInput1.files[0];
            if (file) {
                updateAlert('جارٍ تحميل الملف...', 'info');

                const formData = new FormData();
                formData.append('file', file);
                formData.append('functionality', functionality); // Send functionality type

                // Send the file and functionality type via fetch
                fetch(`/upload_file_${functionality}`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        updateAlert(data.message, 'success');
                        window.location.href = data.file_url; // Redirect to download URL
                    } else {
                        updateAlert(data.message, 'error');
                    }
                })
                .catch(error => {
                    updateAlert('حدث خطأ أثناء تحميل الملف.', 'error');
                    console.error('Error:', error);
                });
            } else {
                updateAlert('يرجى تحميل الملف.', 'warning');
            }
        });
    }

    // Hide alert after 5 seconds
    setTimeout(hideAlert, 5000);
});
