document.getElementById("showPassword").addEventListener("change", function () {
    var passwordInput = document.getElementById("pwd");
    passwordInput.type = this.checked ? "text" : "password";
});

function prepareRequestData() {
    const newPersonalID = document.getElementById('new-personal-id').value;
    const password = document.getElementById('pwd').value;

    return {
        new_personal_id: newPersonalID,
        client_password: password
    };
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

async function verifyAccess() {
    const requestData = prepareRequestData();

    try {
        console.log("sending request data:", requestData)
        const response = await fetch('/client/verify-switch-signing-access', {
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
}

function showFailureAlert(message) {
    document.getElementById('alert-text').innerText = message;
    document.getElementById('alert-container').style.backgroundColor = 'red';
    document.getElementById('alert-container').style.display = 'block';
}
  
function closeAlert() {
document.getElementById('alert-container').style.display = 'none';
}