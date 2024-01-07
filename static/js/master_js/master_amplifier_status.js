$(document).ready(function() {
    var table = $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/amplifier_tracking", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            { "data": "name" }, 
            { "data": "category" },
            { "data": "color" },
            { "data": "palga" }, 
            { "data": "mami_serial" },
            { "data": "description" },
            { "data": "test_type"},
            { "data": "interval"},
            { "data": "results"},
            { "data": "last_updated"},
            {
                "data": "object_id",
                "render": function(data, type, row) {
                    return `
                    <button class='resultsBtn btn-primary' data-object-id="${data}">Update Results</button>
                    <button class='intervalBtn btn-warning' data-object-id="${data}">Change Interval</button>
                    <button class='deleteBtn btn-danger' data-object-id="${data}">Delete Tracking</button>
                    `
                }
            }
        ]
    });

    $('#collectionTable tbody').on('click', '.resultsBtn', function() {
        var objectId = $(this).data('object-id'); // Retrieve the id
        var data = table.row($(this).parents('tr')).data();
        updateResults(data, objectId);
    });

    $('#collectionTable tbody').on('click', '.intervalBtn', function() {
        var objectId = $(this).data('object-id'); // Retrieve the id
        var data = table.row($(this).parents('tr')).data();
        updateInterval(data, objectId);
    });

    $('#collectionTable tbody').on('click', '.deleteBtn', function() {
        var objectId = $(this).data('object-id'); // Retrieve the id
        var data = table.row($(this).parents('tr')).data();
        deleteTracking(data, objectId);
    });
});

function updateResults(data, objectId) {
    $('#amplifierResultsForm').data('object-id', objectId);

    amplifierParagraph = 
    `
    Insert here the updated test results for the selected amplifier: <br>
    <b>${data.name}(${data.category})- ${data.palga}, ${data.color}.</b>
    `

    $('#amplifierContent').html(amplifierParagraph)

    $('#amplifierResultsModal').modal('show');
}

function updateInterval(data, objectId) {
    $('#amplifierIntervalForm').data('object-id', objectId);

    amplifierParagraph = 
    `
    Insert here the updated interval for the selected amplifier: <br>
    <b>${data.name}(${data.category})- ${data.palga}, ${data.color}.</b>
    `

    $('#amplifierIntervalContent').html(amplifierParagraph)

    $('#interval').val(data.interval)

    $('#amplifierIntervalModal').modal('show');
}

document.getElementById('confirmDelete').addEventListener('click', async function() {
    // perform the deletion action
    // Close the modal after action
    let objectId = $('#confirmationModal').data('object-id');
    console.log("Item deleted!", objectId); // Replace with actual deletion logic
    try {
        const response = await fetch('/master/delete_amplifier_tracking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({object_id: objectId}),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    }
});

function deleteTracking(data, objectId) {
    $('#confirmationModal').data('object-id', objectId);

    amplifierParagraph = 
    `
    Are you sure you want to stop tracking for the selected amplifier: <br>
    <b>${data.name}(${data.category})- ${data.palga}, ${data.color}?</b>
    `
    console.log("I'm here", amplifierParagraph)

    $('#amplifierdeleteContent').html(amplifierParagraph)

    $('#confirmationModal').modal('show');
}

$('#amplifierResultsForm').on('submit', async function(e) {
    e.preventDefault();

    let requestData = prepareResultsRequestData($(this));
    try {
        console.log("sending: ", requestData)
        const response = await fetch('/master/update_amplifier_results', {
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


$('#amplifierIntervalForm').on('submit', async function(e) {
    e.preventDefault();

    let requestData = prepareIntervalRequestData($(this));
    try {
        console.log("sending: ", requestData)
        const response = await fetch('/master/update_amplifier_interval', {
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


function prepareResultsRequestData(element) {
    return {
        object_id: element.data('object-id'),
        results: $('#resultsText').val()
    }
}

function prepareIntervalRequestData(element) {
    return {
        object_id: element.data('object-id'),
        interval: $('#interval').val()
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