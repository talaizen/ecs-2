async function createMasterAccount() {
    const firstName = document.getElementById('first-name').value;
    const lastName = document.getElementById('last-name').value;
    const personalID = document.getElementById('personal-id').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

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
        }),
    });

    if (response.ok) {
        // Successful login, you can redirect or perform other actions
        console.log('Login successful');
    } else {
        // Failed login, handle the error
        console.error('Login failed');
    }
}

document.getElementById("show-password").addEventListener("change", function () {
    let passwordInput = document.getElementById("password");
    let confirmPasswordInput = document.getElementById("confirm-password");
    const status = this.checked ? "text" : "password";
    passwordInput.type = status;
    confirmPasswordInput.type = status;
  });
