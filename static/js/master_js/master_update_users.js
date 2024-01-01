$(document).ready(function() {
    $('#collectionTable').DataTable({
        "ajax": {
            "url": "/collections-data/update_client_users", // API endpoint in your FastAPI app that returns collection data
            "dataSrc": "" // Adjust this based on the structure of your response
        },
        "columns": [
            { "data": "first_name" }, 
            { "data": "last_name" },
            { "data": "personal_id" }, 
            { "data": "email" },
            { "data": "palga" }, 
            { "data": "team" },
            { "data": "password"},
            {
                "data": "user_id", // assuming object_id is the field name in your data
                "render": function(data, type, row) {
                    return `<button class="delete-btn" data-user-id="${data}">Delete</button>`;
                },
                "orderable": false
            }   // Replace with the actual data property name
        ]
    });

    $('#collectionTable tbody').on('click', '.delete-btn', async function() {
        let objectId = $(this).data('user-id'); // Get the object_id from the button's data attribute
        try {
            console.log("this is oi", objectId)
            const response = await fetch('/master/delete_client_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({user_id: objectId}),
            });
            console.log("this is response: ", response)
            handleResponse(response);
        } catch (error) {
            console.error('Error creating master user:', error);
            showFailureAlert('An unexpected error occurred.');
        }     
    });
});

function handleErrorResponse(response, responseData) {
    if (response.status === 401 || response.status === 400 ) {
        const errorMessage = responseData.detail;
        console.error('failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else if (response.status === 422) {
        const errorDetail = responseData.detail[0];
        const errorMessage = errorDetail.msg;
        console.error('failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else {
        console.error('Unexpected error:', response.statusText);
        showFailureAlert('An unexpected error occurred.');
    }
}

async function handleResponse(response) {
    const responseData = await response.json();

    if (response.ok) {
        console.log('status code ok - redirecting page')
        const redirectUrl = responseData.redirect_url;
        console.log('this is url: ', redirectUrl);
        window.location.href = redirectUrl;
    } else {
        handleErrorResponse(response, responseData);
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

