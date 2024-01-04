$(function() {
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/kits", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            {"data": "kit_name"},
            {"data": "kit_description"},
            {
                "data": "kit_id",
                "render": function(data, type, row) {
                    return `
                        <button class="add-btn" data-object-id="${data}">Add Items</button>
                        <button class="remove-btn" data-object-id="${data}">Remove Items</button>
                        <button class="content-btn" data-object-id="${data}">Kit Content</button>
                        <button class="delete-btn" data-object-id="${data}">Delete Kit</button>
                    `;
                },
                "orderable": false
            }
        ]
    });
});

$(document).on('click', '.remove-btn', async function() {
    let kitId = $(this).data('object-id');
    console.log(kitId);
    try {
        const response = await fetch('/master/kit_remove_items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({kit_id: kitId}),
        });
        console.log("this is response: ", response)
        handleResponse(response);
    } catch (error) {
        console.error('Error creating master user:', error);
        showFailureAlert('An unexpected error occurred.');
    }
});

$(document).on('click', '.content-btn', async function() {
    console.log("here");
    let kitId = $(this).data('object-id');
    console.log(kitId);
    try {
        const response = await fetch('/master/kit_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({kit_id: kitId}),
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

// $('#newKitBtn').on('click', async function(){
//     try {
//         const response = await fetch('/master/add_items_to_pending_signings', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify(selectedItems),
//         });
//         console.log("this is response: ", response)
//         handleResponse(response);
//     } catch (error) {
//         console.error('Error creating master user:', error);
//         showFailureAlert('An unexpected error occurred.');
//     }
// })