$('#newKitSubmit').on('click', async function() {
    let kitName = $('#kitName').val();
    let palga = $('#kitPalga').val();
    console.log(kitName, palga);
    try {
        const response = await fetch('/master/new_kit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({kit_name: kitName, palga: palga}),
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

