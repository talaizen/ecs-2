$(function() {
    // Initialize DataTable with dynamic data loading
    var table = $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/pending_signings", // Replace with your API endpoint
            "dataSrc": "" // Adjust this if your data is nested in the response JSON
        },
        "columns": [
            {
                "data": "object_id", // For the checkboxes, we're not binding to specific data
                "render": function(data, type, row) {
                    return `<input type="checkbox" class="row-checkbox" data-object-id="${data}">`;
                },
                "orderable": false
            },
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
            { "data": "signer" },  // Replace with the actual data property name
            { "data": "issuer" },   // Replace with the actual data property name
            { "data": "signing_description" },
            {
                "data": "object_id", // assuming object_id is the field name in your data
                "render": function(data, type, row) {
                    return `<button class="delete-btn" data-object-id="${data}">Delete</button>`;
                },
                "orderable": false
            }   // Replace with the actual data property name
            // ... Add other columns as needed ...
        ],
        // ... Additional DataTables options ...
    });

    // Handle click on "check all" box
    $('#checkAll').on('click', function() {
        var rows = table.rows({ 'search': 'applied' }).nodes();
        $('input[type="checkbox"].row-checkbox', rows).prop('checked', this.checked);
    });

    // Handle form submission event
    $('#itemsForm').on('submit', async function(e) {
        e.preventDefault();

        let checkedObjectIds = [];
    // Iterate over all checkboxes and collect the object IDs of checked ones
        $('#collectionTable .row-checkbox:checked').each(function() {
            let objectId = $(this).data('object-id')
            checkedObjectIds.push({pending_signing_id: objectId});
        });
        try {
            console.log(checkedObjectIds)
            const response = await fetch('/master/add_items_to_signings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({selected_items: checkedObjectIds}),
            });
            console.log("this is response: ", response)
            handleResponse(response);
        } catch (error) {
            console.error('Error creating master user:', error);
            showFailureAlert('An unexpected error occurred.');
        }     
        // ... your form submission logic ...
    });

    //Start with the "check all" checkbox checked
    $('#checkAll').prop('checked', true).trigger('click');

    $('#collectionTable tbody').on('click', '.delete-btn', async function() {
        let objectId = $(this).data('object-id'); // Get the object_id from the button's data attribute
        try {
            console.log("this is oi", objectId)
            const response = await fetch('/master/delete_item_from_pending_signings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({pending_signing_id: objectId}),
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
