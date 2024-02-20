$(document).ready(function() {
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/inventory", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            { 
                "data": "name",
                "render": function(data, type, row) {
                    // Encapsulate the name in a clickable element, such as a button or span, and include the category in a data attribute
                    return `<span class="clickable-name" data-category="${row.category}" data-item-id="${row.object_id}" data-name="${data}">${data}</span>`;
                }
            }, 
            { "data": "category" },
            { "data": "count" }, 
            { "data": "color" },
            { "data": "palga" }, 
            { "data": "mami_serial" },
            { "data": "manufacture_mkt" }, 
            { "data": "katzi_mkt" },
            { "data": "serial_no" },
            { "data": "description" }
        ],
        "drawCallback": function(settings) {
            // Add click event listener for names after table draw
            $('.clickable-name').on('click', function() {
                var category = $(this).data('category');
                var itemId = $(this).data('item-id');
                var kitName = $(this).data('name');
                if (category === 'kit') {
                    openModalAndShowDetails(itemId, kitName);
                }
            });
        }
    });
});

function openModalAndShowDetails(itemId, kitName) {
    // Code to open modal
    console.log("open kit content modal", itemId);
    $('#kit-content-modal').modal('show');

    $('.modal-title').text("kit content: " + kitName);

    if ($.fn.DataTable.isDataTable('#kitContentTable')) {
        $('#kitContentTable').DataTable().destroy();
    }

    let apiUrl = `/collections-data/kit_content_item_based/${itemId}`;
    $('#kitContentTable').DataTable({
        scrollX: true,
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
}