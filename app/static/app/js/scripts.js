
window.addEventListener("DOMContentLoaded", (event) => {
  setTimeout(function () {
    let alertElement = document.querySelector(".alert");
    if (alertElement) {
      alertElement.classList.remove("show");
      alertElement.classList.add("fade");
    }
  }, 3000); // 3 seconds
});