document.addEventListener('DOMContentLoaded', function() {
  // Sidenav initiator
  let sidenav = document.querySelectorAll('.sidenav');
  M.Sidenav.init(sidenav, {edge:"right"});

  // Effect on hovering over the recipe images
  let materialboxed = document.querySelectorAll('.materialboxed');
  M.Materialbox.init(materialboxed);    
});