$(function() {
    // Initialize DataTable with dynamic data loading
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/master_approve_switch_requests", // Replace with your API endpoint
            "dataSrc": "" // Adjust this if your data is nested in the response JSON
        },
        "columns": [
            {
                "data": "request_id", // For the checkboxes, we're not binding to specific data
                "render": function(data, type, row) {
                    return `<input type="checkbox" class="row-checkbox" data-request-id="${data}">`;
                },
                "orderable": false
            },
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
            // ... Add other columns as needed ...
        ],
        // ... Additional DataTables options ...
    });
});
function prepareRequestData() {
    let table = $('#collectionTable').DataTable();
    let checkedObjectIds = [];

    // Iterate over all data in the DataTable
    table.rows().every(function() {
        let row = this.node();
        let $row = $(row);
        let $checkbox = $row.find('.row-checkbox');

        // Check if the row is valid and checked
        if ($checkbox.is(':checked')) {
            // If checked, get the data-object-id attribute value
            let objectId = $checkbox.data('request-id');
            checkedObjectIds.push({switch_request_id: objectId});
        }
    });
    return {selected_requests: checkedObjectIds}
}

async function approveRequests() {
    const selectedItems = prepareRequestData();
    console.log("here", selectedItems)

    try {
        const response = await fetch('/master/approve_switch_rquest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(selectedItems),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    } 
}

async function rejectRequests() {
    const selectedItems = prepareRequestData();

    try {
        const response = await fetch('/master/reject_switch_rquest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(selectedItems),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    } 
}

async function handleResponse(response) {
    const responseData = await response.json();

    if (response.ok) {
        console.log('redirecting page')
        const redirectUrl = responseData.redirect_url;
        window.location.href = redirectUrl;
    } else {
        handleErrorResponse(response, responseData);
    }
}

function handleErrorResponse(response, responseData) {
    if (response.status === 401 || response.status === 400 ) {
        const errorMessage = responseData.detail;
        console.error('verification failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else if (response.status === 422) {
        const errorDetail = responseData.detail[0];
        const errorMessage = errorDetail.msg;
        console.error('verification failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else {
        console.error('Unexpected error:', response.statusText);
        showFailureAlert('An unexpected error occurred.');
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