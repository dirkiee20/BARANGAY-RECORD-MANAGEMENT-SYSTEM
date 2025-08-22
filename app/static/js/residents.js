// Modal functionality
const newRecordModal = document.getElementById('newRecordModal');
const newRecordBtn = document.getElementById('newRecordBtn');
const form = document.getElementById('newRecordForm');

function openModal() {
    newRecordModal.style.display = 'block'; // Corrected line
    document.body.style.overflow = 'hidden';
}

if (newRecordBtn) {
    newRecordBtn.addEventListener('click', openModal);
} 

function closeModal() {
    newRecordModal.style.display = 'none'; // Corrected line
    document.body.style.overflow = 'auto';
    form.reset();
}

// Close modal if clicking outside
newRecordModal.addEventListener('click', (e) => {
    if (e.target === newRecordModal) { // Corrected line
        closeModal();
    }
});


const profileInput = document.getElementById('profileImage');
const profilePreview = document.getElementById('profilePreview');

profileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            profilePreview.src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
});

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    
   try {
        const response = await fetch('/api/residents', {
            method: 'POST',
            body: formData // This will automatically handle file upload
        });

        if (response.ok) {
            closeModal();
            // Reload residents table or update UI
            location.reload();
        } else {
            alert('Error adding resident');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding resident');
    }
});
