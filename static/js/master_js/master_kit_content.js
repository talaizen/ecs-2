$(function() {
    // Initialize DataTable with dynamic data loading
    let kitId = $('#kitId').val();
    let apiUrl = `/collections-data/kit_content/${kitId}`
    console.log("api url", apiUrl)
    $('#collectionTable').DataTable({
        "ajax": {
            "url": apiUrl, // Replace with your API endpoint
            "dataSrc": "" // Adjust this if your data is nested in the response JSON
        },
        "columns": [
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
        ],
        // ... Additional DataTables options ...
    });
});