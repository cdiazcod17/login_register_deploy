
  // Ocultar mensajes después de 3 segundos (3000 ms)
  setTimeout(function() {
    var flashMessages = document.querySelectorAll('.flashes li');
    flashMessages.forEach(function(message) {
      message.style.transition = 'opacity 0.5s';
      message.style.opacity = '0';
      setTimeout(function() { message.remove(); }, 500); // Eliminar del DOM
    });
  }, 3000);
