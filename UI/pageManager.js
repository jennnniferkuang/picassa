// Page Manager for handling navigation between different pages
const chatButton = document.getElementById("chat-button");
const blankButton = document.getElementById("blank-button");
const chatPage = document.getElementById("chat-page");
const blankPage = document.getElementById("blank-page");

// Function to show a specific page
function showPage(pageId) {
  // Hide all pages
  const pages = document.querySelectorAll('.page');
  pages.forEach(page => {
    page.classList.remove('active');
  });
  
  // Remove active class from all buttons
  const buttons = document.querySelectorAll('.sidebar-button');
  buttons.forEach(button => {
    button.classList.remove('active');
  });
  
  // Show the selected page
  const selectedPage = document.getElementById(pageId);
  if (selectedPage) {
    selectedPage.classList.add('active');
  }
  
  // Add active class to the corresponding button
  const selectedButton = document.getElementById(pageId.replace('-page', '-button'));
  if (selectedButton) {
    selectedButton.classList.add('active');
  }
}

// Event listeners for sidebar buttons
chatButton.addEventListener("click", () => {
  showPage('chat-page');
});

blankButton.addEventListener("click", () => {
  showPage('blank-page');
});

// Initialize with chat page active
showPage('chat-page'); 