function increment(id) {
  const quantity = document.getElementById(id);
  quantity.textContent = parseInt(quantity.textContent) + 1;
}

function decrement(id) {
  const quantity = document.getElementById(id);
  const count = parseInt(quantity.textContent);
  if (count > 0) {
    quantity.textContent = count - 1;
  }
}

function showProductDetails() {
  document.getElementById("productDetailsModal").style.display = "flex";
}

function closeProductDetails() {
  document.getElementById("productDetailsModal").style.display = "none";
}
