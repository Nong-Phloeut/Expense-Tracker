
window.addEventListener("DOMContentLoaded", (event) => {
  setTimeout(function () {
    let alertElement = document.querySelector(".alert");
    if (alertElement) {
      alertElement.classList.remove("show");
      alertElement.classList.add("fade");
    }
  }, 3000); // 3 seconds
});

document.addEventListener("DOMContentLoaded", function () {
  const deleteModal = document.getElementById("deleteModal");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  deleteModal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const url = button.getAttribute("data-url");
    confirmDeleteBtn.setAttribute("href", url);
  });
});