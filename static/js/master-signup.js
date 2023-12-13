async function createMasterAccount() {
    const firstName = document.getElementById('first-name').value;
    const lastName = document.getElementById('last-name').value;
    const personalID = document.getElementById('personal-id').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const masterPassword = document.getElementById('master-password').value;

    const response = await fetch('/create_master_account', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            personal_id: personalID,
            email: email,
            password: password,
            confirm_password: confirmPassword,
            master_password: masterPassword
        }),
    });

    const responseData = await response.json();
    console.log(response.status)
    
    if (response.ok) {
        // Successful login, you can redirect or perform other actions
        console.log('created master user successfully');
        showCreationAlert("created master user successfully");
    } else {
        if(response.status == 400) {
            const errorMessage = responseData.detail
            console.error('master user creation failed: ', errorMessage);
            showFailureAlert(errorMessage);    
        }
        else if(response.status == 422){
            const errorDetail = responseData.detail[0];
            const errorMessage = errorDetail.msg;
            console.error('master user creation failed: ', errorMessage);
            showFailureAlert(errorMessage); 
        }
    }
}

function showCreationAlert(message){
    document.getElementById('alert-text').innerText = message;
    document.getElementById('alert-container').style.backgroundColor = 'green';
    document.getElementById('alert-container').style.display = 'block';
}

function showFailureAlert(message) {
    document.getElementById('alert-text').innerText = message;
    document.getElementById('alert-container').style.display = 'block';
}
  
function closeAlert() {
document.getElementById('alert-container').style.display = 'none';
}
  
document.getElementById("show-password").addEventListener("change", function () {
    let passwordInput = document.getElementById("password");
    let confirmPasswordInput = document.getElementById("confirm-password");
    let masterPasswordInput = document.getElementById("master-password");
    const status = this.checked ? "text" : "password";
    passwordInput.type = status;
    confirmPasswordInput.type = status;
    masterPasswordInput.type = status;
});