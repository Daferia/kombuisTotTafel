document.addEventListener('DOMContentLoaded', function() {
  // Sidenav initiator
  let sidenav = document.querySelectorAll('.sidenav');
  M.Sidenav.init(sidenav, {edge:"right"});

  // Effect on hovering over the recipe images
  let materialboxed = document.querySelectorAll('.materialboxed');
  M.Materialbox.init(materialboxed);    

  // adding a floating action button
  let actionButton = document.querySelectorAll('.fixed-action-btn');
  M.FloatingActionButton.init(actionButton);
});