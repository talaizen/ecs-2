$(document).ready(function() {
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
    $('#itemsForm').on('submit', function(e) {
        e.preventDefault();
        // ... your form submission logic ...
    });

    //Start with the "check all" checkbox checked
    $('#checkAll').prop('checked', true).trigger('click');
});
