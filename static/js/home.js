document.getElementById('contactForm').addEventListener('submit', function(e) {
e.preventDefault();
const formData = new FormData(this);

// Show loading state
const submitBtn = this.querySelector('button[type="submit"]');
const originalText = submitBtn.innerHTML;
submitBtn.innerHTML = '<span>Sending...</span> <i class="bi bi-hourglass-split"></i>';
submitBtn.disabled = true;

fetch('/contact', {
method: 'POST',
body: formData
})
.then(response => response.text())
.then(data => {
// Show success message
showNotification('Thank you for your message! We will get back to you soon.', 'success');
this.reset();
})
.catch(error => {
console.error('Error:', error);
showNotification('Something went wrong. Please try again.', 'error');
})
.finally(() => {
// Restore button
submitBtn.innerHTML = originalText;
submitBtn.disabled = false;
});
});

function showNotification(message, type) {
// Create notification element
const notification = document.createElement('div');
notification.className = `fixed top-5 right-5 px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in ${
type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
}`;
notification.innerHTML = message;

document.body.appendChild(notification);

// Remove after 3 seconds
setTimeout(() => {
notification.remove();
}, 3000);
}

function toggleMenu() {
const menu = document.getElementById("mobileMenu");
menu.classList.toggle("hidden");
}

document.addEventListener('DOMContentLoaded', function() {
const observer = new IntersectionObserver((entries) => {
entries.forEach(entry => {
  if (entry.isIntersecting) {
    entry.target.classList.add('animate-fade-in-up');
  }
});
}, {
threshold: 0.1
});

document.querySelectorAll('.feature-card, .about-section, .testimonial').forEach(el => {
observer.observe(el);
});
});

// Auto-update copyright year
document.getElementById('currentYear').textContent = new Date().getFullYear();

let greeted = false;

const hasVisited = localStorage.getItem('hasVisitedBefore');

// Only play on first visit (remove this condition if you want it every time)
if (!hasVisited) {
  setTimeout(() => {
      speakWelcome();
  }, 1000);

  localStorage.setItem('hasVisitedBefore', 'true');
};

function playWelcome() {
if (greeted) return;
greeted = true;

const speak = () => {
  const utterance = new SpeechSynthesisUtterance(
    "Hello, I'm ANNA. Welcome to ARTINEX, powered by ARNA Technology — a platform where we predict what's next to transform your business."
  );

  const voices = speechSynthesis.getVoices();
  const voice = voices.find(v => v.lang.startsWith("en"));
  if (voice) utterance.voice = voice;

  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  speechSynthesis.cancel(); // clear stuck queue
  speechSynthesis.speak(utterance);
};

if (speechSynthesis.getVoices().length === 0) {
  speechSynthesis.onvoiceschanged = speak;
} else {
  speak();
}
}
console.log("Triggered!")
document.addEventListener("pointerdown", playWelcome, { once: true });
