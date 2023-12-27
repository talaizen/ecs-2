$(function() {
    // Initialize DataTable with dynamic data loading
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/client_signings", // Replace with your API endpoint
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
            { "data": "issuer" },   // Replace with the actual data property name
            { "data": "date"}
            // ... Add other columns as needed ...
        ],
        // ... Additional DataTables options ...
    });
});