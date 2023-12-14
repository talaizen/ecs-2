document.getElementById("show-password").addEventListener("change", function () {
    let passwordInput = document.getElementById("password");
    let confirmPasswordInput = document.getElementById("confirm-password");
    let masterPasswordInput = document.getElementById("master-password");
    passwordInput.type = confirmPasswordInput.type = masterPasswordInput.type = this.checked ? "text" : "password";
});

function prepareRequestData() {
    const palga = document.getElementById('palga').value;
    const team = document.getElementById('team').value;
    const firstName = document.getElementById('first-name').value;
    const lastName = document.getElementById('last-name').value;
    const personalID = document.getElementById('personal-id').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const masterPassword = document.getElementById('master-password').value;

    return {
        palga: palga,
        team: team,
        first_name: firstName,
        last_name: lastName,
        personal_id: personalID,
        email: email,
        password: password,
        confirm_password: confirmPassword,
        master_password: masterPassword
    };
}

async function handleResponse(response) {
    const responseData = await response.json();

    if (response.ok) {
        console.log('Created master user successfully');
        showCreationAlert('created client user successfully');
    } else {
        handleErrorResponse(response, responseData);
    }
}

function handleErrorResponse(response, responseData) {
    if (response.status === 400) {
        const errorMessage = responseData.detail;
        console.error('client user creation failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else if (response.status === 422) {
        const errorDetail = responseData.detail[0];
        const errorMessage = errorDetail.msg;
        console.error('client user creation failed:', errorMessage);
        showFailureAlert(errorMessage);
    } else {
        console.error('Unexpected error:', response.statusText);
        showFailureAlert('An unexpected error occurred.');
    }
}

async function createMasterAccount() {
    const requestData = prepareRequestData();

    try {
        const response = await fetch('/create_client_account', {
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

function showCreationAlert(message){
    document.getElementById('alert-text').innerText = message;
    document.getElementById('alert-container').style.backgroundColor = 'green';
    document.getElementById('alert-container').style.display = 'block';
}

function showFailureAlert(message) {
    document.getElementById('alert-text').innerText = message;
    document.getElementById('alert-container').style.backgroundColor = 'red';
    document.getElementById('alert-container').style.display = 'block';
}
  
function closeAlert() {
document.getElementById('alert-container').style.display = 'none';
}