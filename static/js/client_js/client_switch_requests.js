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
});