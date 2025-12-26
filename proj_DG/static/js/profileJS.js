// document.addEventListener("DOMContentLoaded", function () {
//     const checkbox = document.getElementById("id_same_as_delivery");
//     const bLine1 = document.getElementById("id_bLine1");
//     const bLine2 = document.getElementById("id_bLine2");
//     const bCity = document.getElementById("id_bCity");
//     const bState = document.getElementById("id_bState");
//     const bZip = document.getElementById("id_bZip");
//     const dLine1 = document.getElementById("id_dLine1");
//     const dLine2 = document.getElementById("id_dLine2");
//     const dCity = document.getElementById("id_dCity");
//     const dState = document.getElementById("id_dState");
//     const dZip = document.getElementById("id_dZip");

//     checkbox.addEventListener("change", function () {
//         if (checkbox.checked) {
//             dLine1.value = bLine1.value;
//             dLine2.value = bLine2.value;
//             dCity.value = bCity.value;
//             dState.value = bState.value;
//             dZip.value = bZip.value;
//             dLine1.readOnly = true;  // Optional: lock field
//             dLine2.readOnly = true;  // Optional: lock field
//             dCity.readOnly = true;  // Optional: lock field
//             dState.readOnly = true;  // Optional: lock field
//             dZip.readOnly = true;  // Optional: lock field
//         } else {
//             dLine1.readOnly = false;
//             dLine2.readOnly = false;
//             dCity.readOnly = false;
//             dState.readOnly = false;
//             dZip.readOnly = false;
//             dLine1.value = "";
//             dLine2.value = "";
//             dCity.value = "";
//             dState.value = "";
//             dZip.value = "";
//         }
//     });
//     });


// profileJS.js — tolerant, safe, production version
document.addEventListener("DOMContentLoaded", function () {

    // Try all possible selectors for the "Same as Delivery" checkbox
    const checkbox =
        document.getElementById("id_same_as_delivery") ||
        document.querySelector('input[name="same_as_delivery"]') ||
        document.querySelector('.same-as-delivery') ||
        document.querySelector('input[data-role="same-as-delivery"]') ||
        null;

    // If not found, stop quietly (prevents errors on other pages)
    if (!checkbox) {
        console.warn("profileJS: same-as-delivery checkbox not found on this page — aborting script.");
        return;
    }

    // Helper to safely get elements by ID
    const el = (id) => document.getElementById(id);

    // Billing fields
    const bLine1 = el("id_bLine1");
    const bLine2 = el("id_bLine2");
    const bCity  = el("id_bCity");
    const bState = el("id_bState");
    const bZip   = el("id_bZip");

    // Delivery fields
    const dLine1 = el("id_dLine1");
    const dLine2 = el("id_dLine2");
    const dCity  = el("id_dCity");
    const dState = el("id_dState");
    const dZip   = el("id_dZip");

    // Utility functions
    function setReadOnly(node, yes) {
        if (!node) return;
        node.readOnly = !!yes;
    }

    function setValue(node, value) {
        if (!node) return;
        node.value = value ?? "";
    }

    // Copy billing → delivery
    function copyBillingToDelivery() {
        setValue(dLine1, bLine1 ? bLine1.value : "");
        setValue(dLine2, bLine2 ? bLine2.value : "");
        setValue(dCity,  bCity  ? bCity.value  : "");
        setValue(dState, bState ? bState.value : "");
        setValue(dZip,   bZip   ? bZip.value   : "");

        [dLine1, dLine2, dCity, dState, dZip].forEach(node => setReadOnly(node, true));
    }

    // Clear delivery + unlock fields
    function clearDeliveryFields() {
        [dLine1, dLine2, dCity, dState, dZip].forEach(node => setReadOnly(node, false));
        [dLine1, dLine2, dCity, dState, dZip].forEach(node => setValue(node, ""));
    }

    // On checkbox toggle
    checkbox.addEventListener("change", function () {
        if (checkbox.checked) {
            copyBillingToDelivery();
        } else {
            clearDeliveryFields();
        }
    });

    // If already checked on page load → sync immediately
    if (checkbox.checked) {
        setTimeout(copyBillingToDelivery, 0);
    }
});
