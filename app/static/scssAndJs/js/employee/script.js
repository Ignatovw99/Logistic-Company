const isCourierCheckboxElement = document.getElementById("is_courier");
const officeSectionElement = document.getElementById("office-section");

const handleIsCourierClick = event => {
    const newValue = event.target.checked;

    if (newValue) {
        officeSectionElement.style.display = "none";
    } else {
        officeSectionElement.style.removeProperty("display");
    }
};

isCourierCheckboxElement.addEventListener("click", handleIsCourierClick);
window.addEventListener('DOMContentLoaded', (e) => {
    const value = isCourierCheckboxElement.checked;
    if (value) {
        officeSectionElement.style.display = "none";
    } else {
        officeSectionElement.style.removeProperty("display");
    }
});