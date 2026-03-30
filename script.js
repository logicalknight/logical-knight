// Script for navigation scroll effect and footer year
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('navbar');
  const yearSpan = document.getElementById('year');

  // Set current year in footer
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }

  // Add or remove nav background on scroll
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });
});