document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const uploadForm = document.getElementById('uploadForm');
    const stepUpload = document.getElementById('step-upload');
    const stepReview = document.getElementById('step-review');
    const statusDiv = document.getElementById('status');
    const statusText = document.getElementById('status-text');
    const resultDiv = document.getElementById('result');

    // Inputs & Buttons
    const transcriptArea = document.getElementById('transcript');
    const refineBtn = document.getElementById('refineBtn');
    const sendBtn = document.getElementById('sendBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const resetBtn = document.getElementById('resetBtn');
    const emailInput = document.getElementById('email');
    const subjectInput = document.getElementById('subject');

    // State
    let state = {
        imagePath: null,
        audioPath: null
    };

    // 1. Upload Handler
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        showLoading("Uploading and transcribing...");
        stepUpload.classList.add('hidden');

        const formData = new FormData(uploadForm);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                state.imagePath = data.image_path;
                state.audioPath = data.audio_path;

                transcriptArea.value = data.transcript;

                hideLoading();
                stepReview.classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            handleError(error);
            stepUpload.classList.remove('hidden');
        }
    });

    // 2. Refine Handler
    refineBtn.addEventListener('click', async () => {
        const originalText = transcriptArea.value;
        if (!originalText) return;

        showLoading("Refining text with AI...");
        stepReview.classList.add('hidden');

        try {
            const response = await fetch('/api/refine', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: originalText })
            });

            const data = await response.json();

            if (response.ok) {
                transcriptArea.value = data.refined_text;
                hideLoading();
                stepReview.classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Refinement failed');
            }
        } catch (error) {
            handleError(error);
            stepReview.classList.remove('hidden');
        }
    });

    // 3. Send Handler
    sendBtn.addEventListener('click', async () => {
        const text = transcriptArea.value;
        const email = emailInput.value;
        const subject = subjectInput.value;

        if (!email || !text) {
            alert("Please provide email and ensure transcript is not empty.");
            return;
        }

        showLoading("Sending email...");
        stepReview.classList.add('hidden');

        try {
            const response = await fetch('/api/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    email: email,
                    subject: subject,
                    image_path: state.imagePath,
                    audio_path: state.audioPath
                })
            });

            const data = await response.json();

            if (response.ok) {
                hideLoading();
                resultDiv.classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Sending failed');
            }
        } catch (error) {
            handleError(error);
            stepReview.classList.remove('hidden');
        }
    });

    // Navigation Handlers
    cancelBtn.addEventListener('click', () => {
        stepReview.classList.add('hidden');
        stepUpload.classList.remove('hidden');
        uploadForm.reset();
        // Ideally notify backend to cleanup, but we'll rely on periodic cleanup or next upload
    });

    resetBtn.addEventListener('click', () => {
        resultDiv.classList.add('hidden');
        stepUpload.classList.remove('hidden');
        uploadForm.reset();
        state = { imagePath: null, audioPath: null };
    });

    // Helpers
    function showLoading(msg) {
        statusText.textContent = msg;
        statusDiv.classList.remove('hidden');
    }

    function hideLoading() {
        statusDiv.classList.add('hidden');
    }

    function handleError(error) {
        console.error(error);
        statusText.textContent = `Error: ${error.message}`;
        statusText.style.color = 'red';
        setTimeout(() => {
            hideLoading();
            statusText.style.color = 'inherit';
        }, 3000);
    }
});
