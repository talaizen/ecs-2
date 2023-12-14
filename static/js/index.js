document.getElementById("showPassword").addEventListener("change", function () {
    var passwordInput = document.getElementById("pwd");
    passwordInput.type = this.checked ? "text" : "password";
});

async function loginForm() {
    const personalID = document.getElementById('personal-id').value;
    const password = document.getElementById('pwd').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            personal_id: personalID,
            password: password
        }),
    });

    if (response.ok) {
        const responseData = await response.json();
        console.log(responseData);
        const redirectUrl = responseData.redirect_url;
        if (redirectUrl) {
            // Redirect to the new URL
            window.location.href = redirectUrl;}
    } else {
        // Failed login, handle the error
        console.error('Login failed');
    }
}