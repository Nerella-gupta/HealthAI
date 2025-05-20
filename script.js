let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const slider = document.getElementById('slider');

function updateSlider() {
  const offset = -currentSlide * 100;
  slider.style.transform = `translateX(${offset}%)`;
}

function nextSlide() {
  currentSlide = (currentSlide + 1) % slides.length;
  updateSlider();
}

function prevSlide() {
  currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  updateSlider();
}

setInterval(nextSlide, 5000); // Auto-slide every 5 sec

function sendMessage() {
  const input = document.getElementById("userInput");
  const chatBox = document.getElementById("chatBox");
  const userText = input.value.trim();

  if (userText !== "") {
    const userMsg = document.createElement("p");
    userMsg.textContent = "🧑 You: " + userText;
    chatBox.appendChild(userMsg);

    // Send to backend
    fetch('http://localhost:3000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
    })
    .then(res => res.json())
    .then(data => {
      const botReply = document.createElement("p");
      botReply.textContent = data.reply;
      chatBox.appendChild(botReply);
      chatBox.scrollTop = chatBox.scrollHeight;
    });

    input.value = "";
  }
}

function openProfileForm() {
  document.getElementById("profileForm").style.display = "block";
}

function saveProfile(event) {
  event.preventDefault();
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const language = document.getElementById("language").value;

  fetch("http://localhost:3000/profile", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, language })
  }).then(() => {
    alert("Profile saved!");
    document.getElementById("profileForm").style.display = "none";
  });
}
