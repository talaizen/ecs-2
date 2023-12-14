document.getElementById("showPassword").addEventListener("change", function () {
    var passwordInput = document.getElementById("pwd");
    passwordInput.type = this.checked ? "text" : "password";
});

function prepareRequestData() {
    const personalID = document.getElementById('personal-id').value;
    const password = document.getElementById('pwd').value;

    return {
        personal_id: personalID,
        password: password
    };
}

async function handleResponse(response) {
    const responseData = await response.json();

    if (response.ok) {
        console.log('login successfully')
        const redirectUrl = responseData.redirect_url;
        if (redirectUrl) {
            // Redirect to the new URL
            window.location.href = redirectUrl;}
    } else {
        handleErrorResponse(response, responseData);
    }
}

function handleErrorResponse(response, responseData) {
    if (response.status === 400) {
        const errorMessage = responseData.detail;
        console.error('login failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else if (response.status === 422) {
        const errorDetail = responseData.detail[0];
        const errorMessage = errorDetail.msg;
        console.error('login failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else {
        console.error('Unexpected error:', response.statusText);
        showFailureAlert('An unexpected error occurred.');
    }
}

async function login() {
    const requestData = prepareRequestData();

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });
    
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