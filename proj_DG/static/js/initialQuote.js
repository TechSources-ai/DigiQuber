function calculateTax() {

    const quoteData = document.getElementById('quote-data');
    const ptaInput = document.getElementById('pta');
    const cgstOutput = document.getElementById('cgstAmt');
    const sgstOutput = document.getElementById('sgstAmt');
    const taxAmountOutput = document.getElementById('taxAmount');
    const totalAmountOutput = document.getElementById('totalAmount');

    const preTaxAmt = parseFloat(ptaInput.value) || 0;
    const cgstRate = quoteData.dataset.cgst || 0;
    const sgstRate = quoteData.dataset.sgst || 0;

    // Calculate tax and total
    const cgstAmt = preTaxAmt * (cgstRate / 100);
    const sgstAmt = preTaxAmt * (sgstRate / 100);
    const taxAmt = cgstAmt + sgstAmt;
    const totalAmount = preTaxAmt + taxAmt;

    // Update the output boxes
    cgstOutput.value = cgstAmt.toFixed(2);
    sgstOutput.value = sgstAmt.toFixed(2);
    taxAmountOutput.value = taxAmt.toFixed(2);
    totalAmountOutput.value = totalAmount.toFixed(2);
}

// Single handler function to manage all core input boxes
function handleInput(changedId) {
    // 1. Get ALL core values
    const quote = document.getElementById('quote-data');
    const qtyInput = document.getElementById('qty');
    const ptaInput = document.getElementById('pta');
    
    const unitPrice = parseFloat(quote.dataset.unitPrice);
    console.log("Unit Price from dataset:", unitPrice);
    let priceVal = unitPrice || 0;
    let qtyVal = parseFloat(qtyInput.value) || 0;
    let ptaVal = parseFloat(ptaInput.value) || 0;

    // 2. Decide what to calculate based on which box was edited
    if (changedId === 'qty') {
        // User edited Quantity: Recalculate PTA
        ptaVal = priceVal * qtyVal;
        ptaInput.value = ptaVal.toFixed(2);

    } else if (changedId === 'pta') {
        // User edited PTA: Recalculate the Quantity
        if (priceVal > 0) {
            qtyVal = ptaVal / priceVal; // Quantity = PTA / Price
            qtyInput.value = qtyVal.toFixed(2);
        } else {
            // If Price is zero, assume Quantity is zero
            qtyInput.value = 0;
            // Optionally, you could recalculate price instead: priceVal = ptaVal / qtyVal
        }
    }
    // This executes the tax calculation based on the new PTA value
    calculateTax();
}

// Initial calculation on page load
// window.onload = () => {
//     handleInput('pta'); // Run the handler to set initial PTA/Qty relationship
//     calculateTax();      // Run the tax calculation
// };