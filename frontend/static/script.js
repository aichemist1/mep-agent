document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reportForm');
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    const resetBtn = document.getElementById('resetBtn');
    const statusText = document.getElementById('status-text');
    const transcriptText = document.getElementById('transcript-text');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI State: Loading
        form.classList.add('hidden');
        statusDiv.classList.remove('hidden');
        submitBtn.disabled = true;
        statusText.textContent = "Uploading and processing... This may take a minute.";

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                statusDiv.classList.add('hidden');
                resultDiv.classList.remove('hidden');
                transcriptText.textContent = data.transcript;
            } else {
                // Error
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            statusText.textContent = `Error: ${error.message}`;
            statusText.style.color = 'red';
            // Allow retry?
            setTimeout(() => {
                form.classList.remove('hidden');
                statusDiv.classList.add('hidden');
                submitBtn.disabled = false;
                statusText.style.color = 'inherit';
            }, 3000);
        }
    });

    resetBtn.addEventListener('click', () => {
        form.reset();
        resultDiv.classList.add('hidden');
        form.classList.remove('hidden');
        submitBtn.disabled = false;
    });

    // Simple File Previews (Optional enhancement)
    document.getElementById('image').addEventListener('change', function (e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                // Could show preview here
            }
            reader.readAsDataURL(this.files[0]);
        }
    });
});
