const isExpressCheckboxElement = document.getElementById("is_express");
const senderOfficeSectionElement = document.getElementById("sender-office-section");

const handleIsExpressClick = event => {
    const isExpress = event.target.checked;
    console.log(isExpress);
    if (isExpress) {
        senderOfficeSectionElement.style.display = "none";
    } else {
        senderOfficeSectionElement.style.removeProperty("display");
    }
};

isExpressCheckboxElement.addEventListener("click", handleIsExpressClick);
window.addEventListener('DOMContentLoaded', (e) => {
    const isExpress = isExpressCheckboxElement.checked;
    if (isExpress) {
        senderOfficeSectionElement.style.display = "none";
    } else {
        senderOfficeSectionElement.style.removeProperty("display");
    }
});