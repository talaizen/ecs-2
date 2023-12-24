$(function() {
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/inventory", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            {
                "data": "object_id",
                "render": function (data, type, row) {
                    return `<input type="checkbox" class="item-checkbox" data-item-id="${data}">`;
                },
                "orderable": false
            },
            { "data": "name" }, 
            { "data": "category" },
            { "data": "count" }, 
            { "data": "color" },
            { "data": "palga" }, 
            { "data": "mami_serial" },
            { "data": "manufacture_mkt" }, 
            { "data": "katzi_mkt" },
            { "data": "serial_no" },
            { "data": "description" },
            {
                "data": "max_amount", // Replace with the actual data property
                "render": function(data, type, row) {
                    return `<input type="number" class="item-quantity" min="1" value="1" data-max-amount="${data}">`;
                },
                "orderable": false
            }
        ]
    });
});
function updateRowAppearance(row) {
    var checkbox = $(row).find('.item-checkbox').get(0);
    var quantityInput = $(row).find('.item-quantity');
    var maxAmount = parseInt(quantityInput.data('max-amount'), 10);
    var currentAmount = parseInt(quantityInput.val(), 10);

    if (checkbox.checked) {
        if (currentAmount <= maxAmount) {
            $(row).addClass('valid-checked').removeClass('invalid-checked');
        } else {
            $(row).addClass('invalid-checked').removeClass('valid-checked');
        }
    } else {
        $(row).removeClass('valid-checked').removeClass('invalid-checked');
    }
}

$('#collectionTable').on('change', '.item-checkbox, .item-quantity', function() {
    var row = $(this).closest('tr');
    updateRowAppearance(row);
});

$('#itemsForm').on('submit', function(e) {
    e.preventDefault();
    var table = $('#collectionTable').DataTable();
    var selectedItems = [];

    // Iterate over all data in the DataTable
    table.rows().every(function() {
        var row = this.node();
        var $row = $(row);

        // Check if the row is valid and checked
        if ($row.hasClass('valid-checked')) {
            var itemId = $row.find('.item-checkbox').data('item-id');
            var quantity = $row.find('.item-quantity').val();
            selectedItems.push({ id: itemId, quantity: quantity });
        }
    });

    console.log(selectedItems); // Log or process the selected items
});