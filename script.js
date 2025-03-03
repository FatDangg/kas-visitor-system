const backendURL = "https://kas-visitor-system.onrender.com";

document.getElementById('visitor-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent default form submission

    // Collect form data
    const formData = {
        name: document.getElementById('name').value,
        idNumber: document.getElementById('id-number').value,
        reason: document.getElementById('reason').value,
        visitDate: document.getElementById('visit-date').value,
    };

    try {
        // Send data to backend
        const response = await fetch(`${backendURL}/submit`, {  // ✅ Use backticks here!
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (response.ok) {
            alert('PDF Generated! Download it here: ' + backendURL + result.downloadLink);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong!');
    }
});
