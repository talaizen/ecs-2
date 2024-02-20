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
            { "data": "description" },
            {
                "data": "max_amount", // Replace with the actual data property
                "render": function(data, type, row) {
                    return `<input type="number" class="item-quantity" min="1" value="1" data-max-amount="${data}">`;
                },
                "orderable": false
            }
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

$('#itemsForm').on('submit', async function(e) {
    e.preventDefault();
    let signingDescription = document.getElementById('signingDescription').value;
    console.log("this is des:", signingDescription.trim())
    if (signingDescription.trim() === "") {
        showFailureAlert('signing description is required');
        return;
    }

    const selectedItems = prepareRequestData();
    if (selectedItems === null){
        showFailureAlert('detected invalid selected items');
        return;
    }

    try {
        const response = await fetch('/master/add_items_to_pending_signings', {
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
    console.log(selectedItems); // Log or process the selected items
});

function prepareRequestData() {
    let signingDescription = document.getElementById('signingDescription').value;
    let table = $('#collectionTable').DataTable();
    let selectedItems = [];
    let shouldStop = false;

    // Iterate over all data in the DataTable
    table.rows().every(function() {
        if (shouldStop) {
            return;
        }

        let row = this.node();
        let $row = $(row);

        if ($row.hasClass('invalid-checked')) {
            console.log('invalid');
            shouldStop = true;
            return;
        }

        // Check if the row is valid and checked
        if ($row.hasClass('valid-checked')) {
            console.log('valid');
            let itemId = $row.find('.item-checkbox').data('item-id');
            let quantity = $row.find('.item-quantity').val();
            selectedItems.push({ item_id: itemId, quantity: quantity });
        }
    });
    
    if (shouldStop){
        return null;
    }
    return {selected_items: selectedItems, signing_descrition: signingDescription}
}

async function handleResponse(response) {
    const responseData = await response.json();

    if (response.ok) {
        console.log('verified successfully - redirecting page')
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