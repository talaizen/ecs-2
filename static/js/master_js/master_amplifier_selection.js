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
                    return `<button class='selectBtn btn-primary' data-item-id="${data}">Select</button>`
                }
            }
        ]
    });

    $('#collectionTable tbody').on('click', '.selectBtn', function() {
        var itemId = $(this).data('item-id'); // Retrieve the id
        var data = table.row($(this).parents('tr')).data();
        selectItem(data, itemId); // Pass the item id to the edit function
    });
});


function selectItem(data, itemId) {
    $('#amplifierForm').data('item-id', itemId);

    amplifierParagraph = 
    `
    Set here the required test configurations for your selected item: <br>
    <b>${data.name}(${data.category})- ${data.palga}, ${data.color}.</b>
    `

    $('#amplifierContent').html(amplifierParagraph)

    $('#amplifierModal').modal('show');
}

// When the edit form is submitted
$('#amplifierForm').on('submit', async function(e) {
    e.preventDefault();

    let requestData = prepareRequestData($(this));
    try {
        console.log("sending: ", requestData)
        const response = await fetch('/master/add_amplifier_tracking', {
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
        days_interval: $('#numberOfDays').val(),
        test_type: $('#testType').val()
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

function askConfirmation(itemId) {
    let myModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {
      keyboard: false
    });
    $('#confirmationModal').data('item-id', itemId);
    myModal.show();
}