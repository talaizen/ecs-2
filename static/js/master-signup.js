async function createMasterAccount() {
    const userName = document.getElementById('userName').value;
    const password = document.getElementById('pwd').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: userName,
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

document.getElementById("showPassword").addEventListener("change", function () {
    var passwordInput = document.getElementById("pwd");
    passwordInput.type = this.checked ? "text" : "password";
  });
