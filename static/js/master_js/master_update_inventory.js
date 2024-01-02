$(document).ready(function() {
    var table = $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/inventory", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
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
                "data": "object_id",
                "render": function(data, type, row) {
                    return `<button class='editBtn btn-primary' data-item-id="${data}">Edit</button> <button class='deleteBtn btn-danger' data-item-id="${data}">Delete</button>`
                }
            }
        ]
    });

    $('#collectionTable tbody').on('click', '.editBtn', function() {
        var itemId = $(this).data('item-id'); // Retrieve the id
        var data = table.row($(this).parents('tr')).data();
        editItem(data, itemId); // Pass the item id to the edit function
    });

    // Delete button event listener
    $('#collectionTable tbody').on('click', '.deleteBtn', function() {
        var itemId = $(this).data('item-id'); // Retrieve the id
        askConfirmation(itemId); // Call delete function with the item id
    });
});

document.getElementById('addItemBtn').addEventListener('click', function() {
    $('#addModal').modal('show');
});

document.getElementById('confirmDelete').addEventListener('click', async function() {
    // perform the deletion action
    // Close the modal after action
    let itemId = $('#confirmationModal').data('item-id');
    console.log("Item deleted!", itemId); // Replace with actual deletion logic
    try {
        const response = await fetch('/master/delete_item_from_inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({item_id: itemId}),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    }
});


function editItem(data, itemId) {
    // Set the form action or data attribute to the item's id
    $('#editForm').data('item-id', itemId);

    // Populate the form fields
    $('#itemName').val(data.name);

    $('#itemCategory').val(data.category);

    count_string = data.count;
    let count_parts = count_string.split(' / ');
    let total_count = parseInt(count_parts[1], 10);

    $('#itemCount').val(total_count);
    $('#itemColor').val(data.color);
    $('#itemPalga').val(data.palga);
    $('#itemMamiSerial').val(data.mami_serial);
    $('#itemManufactureMkt').val(data.manufacture_mkt);
    $('#itemKatziMkt').val(data.katzi_mkt);
    $('#itemSerialNo').val(data.serial_no);
    $('#itemDescription').val(data.description);

    $('#editModal').modal('show');
}

// When the edit form is submitted
$('#editForm').on('submit', async function(e) {
    e.preventDefault();

    let requestData = prepareRequestData($(this));
    try {
        console.log("sending: ", requestData)
        const response = await fetch('/master/update_inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    }
});

function prepareRequestData(element) {
    return {
        item_id: element.data('item-id'),
        name: $('#itemName').val(),
        category: $('#itemCategory').val(),
        total_count: $('#itemCount').val(),
        color: $('#itemColor').val(),
        palga: $('#itemPalga').val(),
        mami_serial: $('#itemMamiSerial').val(),
        manufacture_mkt: $('#itemManufactureMkt').val(),
        katzi_mkt: $('#itemKatziMkt').val(),
        serial_no: $('#itemSerialNo').val(),
        description: $('#itemDescription').val()
    }
}

function prepareAddItemRequestData() {
    return {
        name: $('#addItemName').val(),
        category: $('#addItemCategory').val(),
        total_count: parseInt($('#addItemCount').val(), 10),
        color: $('#addItemColor').val(),
        palga: $('#addItemPalga').val(),
        mami_serial: $('#addItemMamiSerial').val(),
        manufacture_mkt: $('#addItemManufactureMkt').val(),
        katzi_mkt: $('#addItemKatziMkt').val(),
        serial_no: $('#addItemSerialNo').val(),
        description: $('#addItemDescription').val()
    }
}

$('#addForm').on('submit', async function(e) {
    e.preventDefault();

    let requestData = prepareAddItemRequestData($(this));
    try {
        console.log("sending: ", requestData)
        const response = await fetch('/master/add_item_to_inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    }
});

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

function askConfirmation(itemId) {
    let myModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {
      keyboard: false
    });
    $('#confirmationModal').data('item-id', itemId);
    myModal.show();
}