$(function() {
    // Initialize DataTable with dynamic data loading
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/client_switch_requests", // Replace with your API endpoint
            "dataSrc": "" // Adjust this if your data is nested in the response JSON
        },
        "columns": [
            { "data": "signer" },  // Replace with the actual data property name
            { "data": "name" },  // Replace with the actual data property name
            { "data": "category" },   // Replace with the actual data property name
            { "data": "quantity" },  // Replace with the actual data property name
            { "data": "color" },   // Replace with the actual data property name
            { "data": "palga" },  // Replace with the actual data property name
            { "data": "mami_serial" },   // Replace with the actual data property name
            { "data": "manufacture_mkt" },  // Replace with the actual data property name
            { "data": "katzi_mkt" },   // Replace with the actual data property name
            { "data": "serial_no" },  // Replace with the actual data property name
            { "data": "item_description" },   // Replace with the actual data property name
            { "data": "signing_description" },
            { "data": "new_signer"},
            { "data": "switch_description"},
            { "data": "status"},
            {
                "data": "request_id", // assuming object_id is the field name in your data
                "render": function(data, type, row) {
                    return `<button class="cancel-btn" data-request-id="${data}">Cancel</button>`;
                },
                "orderable": false
            }   // Replace with the actual data property name
            // ... Add other columns as needed ...
        ],
        // ... Additional DataTables options ...
    });

    $('#collectionTable tbody').on('click', '.cancel-btn', async function() {
        // e.preventDefault();
        let objectId = $(this).data('request-id'); // Get the object_id from the button's data attribute
        try {
            console.log("this is oi", objectId)
            const response = await fetch('/client/cancel_switch_request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({canceled_request_id: objectId}),
            });
            console.log("this is response: ", response)
            handleResponse(response);
        } catch (error) {
            console.error('Error creating master user:', error);
            showFailureAlert('An unexpected error occurred.');
        }     
    });
});



function handleErrorResponse(response, responseData) {
    if (response.status === 401 || response.status === 400 ) {
        const errorMessage = responseData.detail;
        console.error('failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else if (response.status === 422) {
        const errorDetail = responseData.detail[0];
        const errorMessage = errorDetail.msg;
        console.error('failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else {
        console.error('Unexpected error:', response.statusText);
        showFailureAlert('An unexpected error occurred.');
    }
}

async function handleResponse(response) {
    const responseData = await response.json();

    if (response.ok) {
        console.log('status code ok - redirecting page')
        const redirectUrl = responseData.redirect_url;
        console.log('this is url: ', redirectUrl);
        window.location.href = redirectUrl;
    } else {
        handleErrorResponse(response, responseData);
    }
}

function showFailureAlert(message) {
    document.getElementById('alert-text').innerText = message;
    document.getElementById('alert-container').style.backgroundColor = 'red';
    document.getElementById('alert-container').style.display = 'block';
}
  
function closeAlert() {
document.getElementById('alert-container').style.display = 'none';
}
