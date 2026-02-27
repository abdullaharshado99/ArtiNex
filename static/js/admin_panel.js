// Sample data (replace with actual data from Flask)
const contacts = {{ contacts|tojson }};

// Search functionality
document.getElementById('searchInput').addEventListener('keyup', function(e) {
  const searchTerm = e.target.value.toLowerCase();
  const rows = document.querySelectorAll('tbody tr');

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(searchTerm) ? '' : 'none';
  });
});

// Filter by date
document.getElementById('filterDate').addEventListener('change', function(e) {
  const filter = e.target.value;
  // Implement date filtering logic here
  console.log('Filtering by:', filter);
});

// View message
function viewMessage(id) {
  const contact = contacts.find(c => c[0] === id);
  if (contact) {
    document.getElementById('modalName').textContent = contact[1];
    document.getElementById('modalEmail').textContent = contact[2];
    document.getElementById('modalPhone').textContent = contact[3] || 'Not provided';
    document.getElementById('modalDate').textContent = contact[5];
    document.getElementById('modalMessage').textContent = contact[4];

    document.getElementById('messageModal').classList.remove('hidden');
    document.getElementById('messageModal').classList.add('flex');
  }
}

// Close modal
function closeModal() {
  document.getElementById('messageModal').classList.add('hidden');
  document.getElementById('messageModal').classList.remove('flex');
}

// Mark as read
function markAsRead(id) {
  // Send AJAX request to mark as read
  fetch(`/admin/contacts/${id}/read`, { method: 'POST' })
    .then(response => {
      if (response.ok) {
        showNotification('Message marked as read', 'success');
      }
    });
}

// Delete message
function deleteMessage(id) {
  if (confirm('Are you sure you want to delete this message?')) {
    // Send AJAX request to delete
    fetch(`/admin/contacts/${id}/delete`, { method: 'POST' })
      .then(response => {
        if (response.ok) {
          location.reload();
        }
      });
  }
}

// Reply to message
function replyToMessage() {
  const email = document.getElementById('modalEmail').textContent;
  window.location.href = `mailto:${email}`;
  closeModal();
}

// Export to CSV
function exportToCSV() {
  let csv = 'ID,Name,Email,Phone,Message,Date\n';

  contacts.forEach(contact => {
    csv += `${contact[0]},"${contact[1]}","${contact[2]}","${contact[3]}","${contact[4].replace(/"/g, '""')}","${contact[5]}"\n`;
  });

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'contact_submissions.csv';
  a.click();
}

// Refresh data
function refreshData() {
  location.reload();
}

// Notification function
function showNotification(message, type) {
  const notification = document.createElement('div');
  notification.className = `fixed top-5 right-5 px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in ${
    type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
  }`;
  notification.innerHTML = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Close modal when clicking outside
window.onclick = function(event) {
  const modal = document.getElementById('messageModal');
  if (event.target === modal) {
    closeModal();
  }
}