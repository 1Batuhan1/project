// Elemanları seçelim
const sliderContainer = document.querySelector('.slider-container');
const toLoginButton = document.getElementById('toLogin');
const toSignupButton = document.getElementById('toSignup');

// Üye Ol butonuna tıklandığında formu sağa kaydır
toSignupButton.addEventListener('click', function() {
    sliderContainer.style.transform = 'translateX(-50%)'; // Üye ol formuna kaydır
});

// Giriş Yap butonuna tıklandığında formu sola kaydır
toLoginButton.addEventListener('click', function() {
    sliderContainer.style.transform = 'translateX(0)'; // Giriş yap formuna geri kaydır
});
